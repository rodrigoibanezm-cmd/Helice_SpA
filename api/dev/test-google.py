import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from io import BytesIO

from guia_ai import extract_data, validate_data, review_data
from guia_schema import normalize_result, VALID_STATES


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def json_response(handler, status, payload):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def get_drive_service():
    client_email = os.environ.get("GOOGLE_CLIENT_EMAIL")
    private_key = os.environ.get("GOOGLE_PRIVATE_KEY", "").replace("\\n", "\n")

    if not client_email or not private_key:
        raise ValueError("Missing GOOGLE_CLIENT_EMAIL or GOOGLE_PRIVATE_KEY")

    credentials = service_account.Credentials.from_service_account_info(
        {
            "type": "service_account",
            "client_email": client_email,
            "private_key": private_key,
            "token_uri": "https://oauth2.googleapis.com/token",
        },
        scopes=["https://www.googleapis.com/auth/drive.readonly"],
    )

    return build("drive", "v3", credentials=credentials)


def list_drive_files(drive, folder_id):
    response = drive.files().list(
        q=f"'{folder_id}' in parents and trashed = false",
        fields="files(id,name,mimeType,createdTime,modifiedTime)",
        orderBy="createdTime desc",
        pageSize=50,
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()

    return response.get("files", [])


def download_file(drive, file_id):
    request = drive.files().get_media(fileId=file_id, supportsAllDrives=True)
    buffer = BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)

    done = False
    while not done:
        _, done = downloader.next_chunk()

    return buffer.getvalue()


def process_image(image_path):
    extracted = extract_data(image_path)
    validation = validate_data(image_path, extracted)

    result = normalize_result({
        **extracted,
        **validation,
    })

    result["fecha_procesamiento"] = now_iso()
    result["review_applied"] = False

    review = None

    if result["estado"] == "REVISAR":
        result["review_applied"] = True

        review = review_data(image_path, result)
        corrections = review.get("correcciones", {})

        result["data"].update(corrections)
        result = normalize_result(result)

        estado_final = review.get("estado_final", "REVISAR")

        if estado_final not in VALID_STATES:
            estado_final = "REVISAR"

        result["estado"] = estado_final
        result["observaciones"] = review.get(
            "observaciones_finales",
            result["observaciones"],
        )
        result["fecha_procesamiento"] = now_iso()
        result["review_applied"] = True

    return extracted, validation, review, result


class handler:
    def __init__(self, request, response):
        self.rfile = request.body
        self.wfile = response
        self.headers = request.headers
        self.command = request.method

    def send_response(self, status):
        self.status = status

    def send_header(self, key, value):
        self.wfile.headers[key] = value

    def end_headers(self):
        self.wfile.status_code = self.status

    def do_GET(self):
        try:
            folder_id = os.environ.get("GOOGLE_DRIVE_FOLDER_ID")

            if not folder_id:
                return json_response(self, 500, {
                    "ok": False,
                    "error": "Missing GOOGLE_DRIVE_FOLDER_ID",
                })

            if not os.environ.get("OPENAI_API_KEY"):
                return json_response(self, 500, {
                    "ok": False,
                    "error": "Missing OPENAI_API_KEY",
                })

            drive = get_drive_service()
            files = list_drive_files(drive, folder_id)

            first_image = next(
                (f for f in files if f.get("mimeType", "").startswith("image/")),
                None,
            )

            if not first_image:
                return json_response(self, 200, {
                    "ok": True,
                    "folderId": folder_id,
                    "count": len(files),
                    "files": files,
                    "result": None,
                })

            binary = download_file(drive, first_image["id"])
            suffix = Path(first_image["name"]).suffix or ".jpg"

            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(binary)
                tmp_path = Path(tmp.name)

            try:
                extracted, validation, review, result = process_image(tmp_path)
            finally:
                tmp_path.unlink(missing_ok=True)

            result["archivo"] = first_image["name"]

            return json_response(self, 200, {
                "ok": True,
                "folderId": folder_id,
                "count": len(files),
                "file": {
                    "id": first_image["id"],
                    "name": first_image["name"],
                    "mimeType": first_image["mimeType"],
                    "sizeBytes": len(binary),
                },
                "extracted": extracted,
                "validation": validation,
                "review": review,
                "result": result,
            })

        except Exception as error:
            return json_response(self, 500, {
                "ok": False,
                "error": str(error),
            })
