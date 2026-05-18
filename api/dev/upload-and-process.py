import base64
import importlib.util
import json
import os
from io import BytesIO
from pathlib import Path

from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload


def load_process_google():
    module_path = Path(__file__).resolve().with_name("process_google.py")
    spec = importlib.util.spec_from_file_location("process_google", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


process_google = load_process_google()

get_google_services = process_google.get_google_services
get_query_params = process_google.get_query_params
move_drive_file = process_google.move_drive_file
process_drive_image = process_google.process_drive_image
response_json = process_google.response_json

ALLOWED_MIME_TYPES = frozenset({
    "image/jpeg",
    "image/png",
})


def error_payload(error):
    payload = {
        "type": error.__class__.__name__,
        "message": str(error) or repr(error),
    }

    if isinstance(error, HttpError):
        payload["status"] = getattr(error.resp, "status", None)
        payload["reason"] = getattr(error.resp, "reason", None)

        try:
            content = error.content.decode("utf-8")
            payload["content"] = content

            parsed = json.loads(content)
            details = parsed.get("error", {})
            payload["googleError"] = {
                "code": details.get("code"),
                "message": details.get("message"),
                "status": details.get("status"),
                "reason": details.get("errors", [{}])[0].get("reason") if details.get("errors") else None,
            }
        except Exception:
            pass

    return payload


def read_json_body(environ):
    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
    except ValueError:
        length = 0

    if length <= 0:
        raise ValueError("Missing request body")

    raw = environ["wsgi.input"].read(length).decode("utf-8")
    return json.loads(raw)


def validate_token(query):
    expected = os.environ.get("UPLOAD_PROCESS_TOKEN")
    received = query.get("token", [""])[0]

    if not expected:
        raise ValueError("Missing UPLOAD_PROCESS_TOKEN")

    return received == expected


def decode_image_base64(value):
    clean = str(value or "").strip()

    if clean.startswith("data:") and "," in clean:
        clean = clean.split(",", 1)[1]

    if not clean:
        raise ValueError("Missing imageBase64")

    return base64.b64decode(clean, validate=True)


def upload_drive_file(drive, folder_id, filename, mime_type, binary):
    media = MediaIoBaseUpload(
        BytesIO(binary),
        mimetype=mime_type,
        resumable=False,
    )

    metadata = {
        "name": filename,
        "parents": [folder_id],
        "mimeType": mime_type,
    }

    return drive.files().create(
        body=metadata,
        media_body=media,
        fields="id,name,mimeType",
        supportsAllDrives=True,
    ).execute()


def app(environ, start_response):
    drive_file = None
    pending_folder_id = os.environ.get("GOOGLE_DRIVE_FOLDER_ID")

    try:
        query = get_query_params(environ)

        if not validate_token(query):
            return response_json(start_response, 401, {
                "ok": False,
                "error": "invalid_token",
            })

        if environ.get("REQUEST_METHOD", "GET").upper() != "POST":
            return response_json(start_response, 405, {
                "ok": False,
                "error": "method_not_allowed",
            })

        if not pending_folder_id:
            raise ValueError("Missing GOOGLE_DRIVE_FOLDER_ID")

        processed_folder_id = os.environ.get("GOOGLE_DRIVE_PROCESSED_FOLDER_ID")
        error_folder_id = os.environ.get("GOOGLE_DRIVE_ERROR_FOLDER_ID")

        if not processed_folder_id:
            raise ValueError("Missing GOOGLE_DRIVE_PROCESSED_FOLDER_ID")

        if not error_folder_id:
            raise ValueError("Missing GOOGLE_DRIVE_ERROR_FOLDER_ID")

        if not os.environ.get("OPENAI_API_KEY"):
            raise ValueError("Missing OPENAI_API_KEY")

        body = read_json_body(environ)
        filename = str(body.get("filename") or "guia.jpg").strip()
        mime_type = str(body.get("mimeType") or "").strip().lower()

        if mime_type not in ALLOWED_MIME_TYPES:
            return response_json(start_response, 400, {
                "ok": False,
                "error": "unsupported_mime_type",
                "allowedMimeTypes": sorted(ALLOWED_MIME_TYPES),
            })

        binary = decode_image_base64(body.get("imageBase64"))
        drive, sheets = get_google_services()

        drive_file = upload_drive_file(
            drive=drive,
            folder_id=pending_folder_id,
            filename=filename,
            mime_type=mime_type,
            binary=binary,
        )

        item = process_drive_image(drive, sheets, drive_file)
        result = item.get("result", {})
        data = result.get("data", {})

        move_drive_file(
            drive,
            drive_file["id"],
            pending_folder_id,
            processed_folder_id,
        )

        return response_json(start_response, 200, {
            "ok": True,
            "estado": result.get("estado"),
            "numeroGuia": data.get("numero_guia", ""),
            "duplicate": item.get("duplicate", False),
            "sheetWritten": item.get("sheetWritten", False),
            "storageKey": item.get("storageKey"),
            "movedTo": "processed",
            "driveFile": {
                "id": drive_file.get("id"),
                "name": drive_file.get("name"),
                "mimeType": drive_file.get("mimeType"),
            },
        })

    except Exception as error:
        moved_to = None

        try:
            if drive_file and pending_folder_id:
                error_folder_id = os.environ.get("GOOGLE_DRIVE_ERROR_FOLDER_ID")
                if error_folder_id:
                    drive, _ = get_google_services()
                    move_drive_file(
                        drive,
                        drive_file["id"],
                        pending_folder_id,
                        error_folder_id,
                    )
                    moved_to = "error"
        except Exception:
            moved_to = None

        return response_json(start_response, 500, {
            "ok": False,
            "error": error_payload(error),
            "movedTo": moved_to,
            "driveFile": {
                "id": drive_file.get("id"),
                "name": drive_file.get("name"),
                "mimeType": drive_file.get("mimeType"),
            } if drive_file else None,
        })
