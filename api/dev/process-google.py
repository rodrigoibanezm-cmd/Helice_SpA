import json
import os
import re
import tempfile
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from io import BytesIO

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from guia_ai import extract_data, validate_data, review_data
from guia_schema import normalize_result, VALID_STATES


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def response_json(start_response, status_code, payload):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    status = f"{status_code} {'OK' if status_code < 400 else 'ERROR'}"
    headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Content-Length", str(len(body))),
    ]
    start_response(status, headers)
    return [body]


def get_query_params(environ):
    query_string = environ.get("QUERY_STRING", "")

    if not query_string:
        request_uri = environ.get("REQUEST_URI", "") or environ.get("RAW_URI", "")
        if "?" in request_uri:
            query_string = request_uri.split("?", 1)[1]

    return urllib.parse.parse_qs(query_string)


def normalize_numero_guia(value):
    return re.sub(r"[^0-9A-Za-z_-]", "", str(value or "").strip())


def redis_command(command):
    url = os.environ.get("KV_REST_API_URL")
    token = os.environ.get("KV_REST_API_TOKEN")

    if not url or not token:
        raise ValueError("Missing KV_REST_API_URL or KV_REST_API_TOKEN")

    request = urllib.request.Request(
        url,
        data=json.dumps(command).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(request) as response:
        payload = json.loads(response.read().decode("utf-8"))
        return payload.get("result")


def redis_get(key):
    return redis_command(["GET", key])


def redis_set(key, value):
    return redis_command(["SET", key, json.dumps(value, ensure_ascii=False)])


def redis_lpush(key, value):
    return redis_command(["LPUSH", key, json.dumps(value, ensure_ascii=False)])


def find_storage_key(numero_guia):
    base_key = f"helice:guia:numero:{numero_guia}"

    if redis_get(base_key) is None:
        return base_key, False, None

    first_duplicate_key = f"{base_key}_resp"

    if redis_get(first_duplicate_key) is None:
        return first_duplicate_key, True, base_key

    index = 2
    while True:
        candidate = f"{base_key}_resp_{index}"
        if redis_get(candidate) is None:
            return candidate, True, base_key
        index += 1


def save_guia_envelope(result, source):
    numero_guia = normalize_numero_guia(result.get("data", {}).get("numero_guia", ""))

    if not numero_guia:
        raise ValueError("Missing numero_guia")

    storage_key, duplicate, duplicate_of = find_storage_key(numero_guia)
    saved_at = now_iso()

    envelope = {
        "numero_guia": numero_guia,
        "storage_key": storage_key,
        "duplicate": duplicate,
        "duplicate_of": duplicate_of,
        "saved_at": saved_at,
        "source": source,
        "result": result,
    }

    redis_set(storage_key, envelope)

    bitacora_event = {
        "event": "guia_processed",
        "numero_guia": numero_guia,
        "storage_key": storage_key,
        "duplicate": duplicate,
        "duplicate_of": duplicate_of,
        "estado": result.get("estado"),
        "saved_at": saved_at,
        "source": source,
    }

    redis_lpush("helice:bitacora", bitacora_event)

    return envelope, bitacora_event


def get_google_services():
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
        scopes=[
            "https://www.googleapis.com/auth/drive.readonly",
            "https://www.googleapis.com/auth/spreadsheets",
        ],
    )

    return (
        build("drive", "v3", credentials=credentials),
        build("sheets", "v4", credentials=credentials),
    )


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


def build_destino(data):
    parts = [
        data.get("destino_empresa", ""),
        data.get("destino_direccion", ""),
        data.get("destino_comuna", ""),
    ]
    return " - ".join([part for part in parts if part])


def build_sheet_row(result):
    data = result.get("data", {})
    return [
        data.get("correlativo", ""),
        data.get("tipo_guia", ""),
        data.get("numero_guia", ""),
        data.get("marca", ""),
        data.get("modelo", ""),
        data.get("chassis_serie", ""),
        data.get("posicion_lote_codigo", ""),
        data.get("origen", ""),
        build_destino(data),
        data.get("comentarios", ""),
        data.get("tipo_factura", ""),
    ]


def append_sheet_row(sheets, result):
    spreadsheet_id = os.environ.get("GOOGLE_SHEET_ID")
    if not spreadsheet_id:
        raise ValueError("Missing GOOGLE_SHEET_ID")

    row = build_sheet_row(result)
    sheets.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range="A:K",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": [row]},
    ).execute()
    return row


def process_image(image_path):
    extracted = extract_data(image_path)
    validation = validate_data(image_path, extracted)

    result = normalize_result({**extracted, **validation})
    result["fecha_procesamiento"] = now_iso()
    result["review_applied"] = False

    review = None

    if result["estado"] == "REVISAR":
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


def process_drive_image(drive, sheets, image_file):
    binary = download_file(drive, image_file["id"])
    suffix = Path(image_file["name"]).suffix or ".jpg"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(binary)
        tmp_path = Path(tmp.name)

    try:
        extracted, validation, review, result = process_image(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)

    result["archivo"] = image_file["name"]

    source = {
        "drive_file_id": image_file["id"],
        "filename": image_file["name"],
        "mimeType": image_file["mimeType"],
        "sizeBytes": len(binary),
    }

    sheet_row = None
    sheet_written = False
    envelope = None
    bitacora_event = None

    if result.get("estado") in {"OK", "REVISAR"}:
        envelope, bitacora_event = save_guia_envelope(result, source)
        if not envelope.get("duplicate"):
            sheet_row = append_sheet_row(sheets, result)
            sheet_written = True

    return {
        "ok": True,
        "file": source,
        "sheetWritten": sheet_written,
        "sheetRow": sheet_row,
        "upstashSaved": envelope is not None,
        "duplicate": envelope.get("duplicate") if envelope else False,
        "storageKey": envelope.get("storage_key") if envelope else None,
        "bitacoraEvent": bitacora_event,
        "extracted": extracted,
        "validation": validation,
        "review": review,
        "result": result,
    }


def build_move_plan(image_files, processed_folder_id):
    return [
        {
            "fileId": file.get("id"),
            "name": file.get("name"),
            "mimeType": file.get("mimeType"),
            "target": "processed",
            "targetFolderId": processed_folder_id,
        }
        for file in image_files
    ]


def app(environ, start_response):
    try:
        folder_id = os.environ.get("GOOGLE_DRIVE_FOLDER_ID")
        if not folder_id:
            return response_json(start_response, 500, {
                "ok": False,
                "runtime": "python",
                "error": "Missing GOOGLE_DRIVE_FOLDER_ID",
            })

        query = get_query_params(environ)
        mode = query.get("mode", ["process"])[0]

        drive, sheets = get_google_services()
        files = list_drive_files(drive, folder_id)
        image_files = [f for f in files if f.get("mimeType", "").startswith("image/")]

        if mode == "list":
            return response_json(start_response, 200, {
                "ok": True,
                "runtime": "python",
                "mode": "list",
                "folderId": folder_id,
                "totalFiles": len(files),
                "totalImages": len(image_files),
                "files": image_files,
            })

        if mode == "move-dry-run":
            processed_folder_id = os.environ.get("GOOGLE_DRIVE_PROCESSED_FOLDER_ID")
            if not processed_folder_id:
                return response_json(start_response, 500, {
                    "ok": False,
                    "runtime": "python",
                    "mode": "move-dry-run",
                    "error": "Missing GOOGLE_DRIVE_PROCESSED_FOLDER_ID",
                })

            move_plan = build_move_plan(image_files, processed_folder_id)

            return response_json(start_response, 200, {
                "ok": True,
                "runtime": "python",
                "mode": "move-dry-run",
                "folderId": folder_id,
                "totalImages": len(image_files),
                "plannedMoves": len(move_plan),
                "movePlan": move_plan,
            })

        if not os.environ.get("OPENAI_API_KEY"):
            return response_json(start_response, 500, {
                "ok": False,
                "runtime": "python",
                "error": "Missing OPENAI_API_KEY",
            })

        results = []
        processed = 0
        written = 0
        duplicates = 0
        errors = 0

        for image_file in image_files:
            try:
                item = process_drive_image(drive, sheets, image_file)
                processed += 1
                if item.get("sheetWritten"):
                    written += 1
                if item.get("duplicate"):
                    duplicates += 1
                results.append(item)
            except Exception as error:
                errors += 1
                results.append({
                    "ok": False,
                    "file": {
                        "id": image_file.get("id"),
                        "name": image_file.get("name"),
                        "mimeType": image_file.get("mimeType"),
                    },
                    "error": str(error),
                })

        return response_json(start_response, 200, {
            "ok": errors == 0,
            "runtime": "python",
            "mode": "process",
            "folderId": folder_id,
            "totalFiles": len(files),
            "totalImages": len(image_files),
            "processed": processed,
            "written": written,
            "duplicates": duplicates,
            "errors": errors,
            "results": results,
        })

    except Exception as error:
        return response_json(start_response, 500, {
            "ok": False,
            "runtime": "python",
            "error": str(error),
        })
