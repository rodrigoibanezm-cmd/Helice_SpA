import base64
import json
import os
import sys
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from lib.email_alerts import send_guia_processed_email  # noqa: E402
from lib.guia_pipeline import (  # noqa: E402
    append_sheet_row,
    get_query_params,
    now_iso,
    process_image,
    save_guia_envelope,
)

ALLOWED_MIME_TYPES = frozenset({
    "image/jpeg",
    "image/png",
})


def response_json(start_response, status_code, payload):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    status = f"{status_code} {'OK' if status_code < 400 else 'ERROR'}"
    headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Content-Length", str(len(body))),
        ("Access-Control-Allow-Origin", "*"),
        ("Access-Control-Allow-Methods", "POST, OPTIONS"),
        ("Access-Control-Allow-Headers", "Content-Type"),
    ]
    start_response(status, headers)
    return [body]


def response_options(start_response):
    headers = [
        ("Access-Control-Allow-Origin", "*"),
        ("Access-Control-Allow-Methods", "POST, OPTIONS"),
        ("Access-Control-Allow-Headers", "Content-Type"),
        ("Content-Length", "0"),
    ]
    start_response("204 OK", headers)
    return [b""]


def error_payload(error):
    return {
        "type": error.__class__.__name__,
        "message": str(error) or repr(error),
    }


def build_ai_audit(review):
    steps = ["extract", "validate"]
    review_applied = review is not None

    if review_applied:
        steps.append("review")

    return {
        "steps": steps,
        "stepsCount": len(steps),
        "reviewApplied": review_applied,
    }


def safe_send_email(numero_guia, estado, ai_audit, blob_url):
    try:
        return send_guia_processed_email(
            numero_guia=numero_guia,
            estado=estado,
            ai_audit=ai_audit,
            blob_url=blob_url,
        )
    except Exception as error:
        return {
            "sent": False,
            "skipped": False,
            "error": error_payload(error),
        }


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


def safe_filename(filename):
    clean = Path(str(filename or "guia.jpg")).name.strip()
    return clean or "guia.jpg"


def blob_path(filename):
    return f"guias/{now_iso().replace(':', '-')}__{safe_filename(filename)}"


def upload_blob(filename, mime_type, binary):
    token = os.environ.get("BLOB_READ_WRITE_TOKEN")
    if not token:
        raise ValueError("Missing BLOB_READ_WRITE_TOKEN")

    path = blob_path(filename)
    url = f"https://blob.vercel-storage.com/{urllib.parse.quote(path)}"

    request = urllib.request.Request(
        url,
        data=binary,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": mime_type,
            "x-add-random-suffix": "0",
        },
        method="PUT",
    )

    with urllib.request.urlopen(request) as response:
        payload = json.loads(response.read().decode("utf-8"))
        return payload


def process_uploaded_binary(filename, mime_type, binary, blob):
    suffix = Path(filename).suffix.lower()

    if not suffix:
        suffix = ".jpg" if mime_type == "image/jpeg" else ".png"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(binary)
        tmp_path = Path(tmp.name)

    try:
        extracted, validation, review, result = process_image(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)

    result["archivo"] = filename
    result["ai_audit"] = build_ai_audit(review)

    source = {
        "type": "blob_upload",
        "filename": filename,
        "mimeType": mime_type,
        "sizeBytes": len(binary),
        "blob": blob,
    }

    sheet_row = None
    sheet_written = False
    envelope = None
    bitacora_event = None
    email_result = None

    if result.get("estado") in {"OK", "REVISAR"}:
        envelope, bitacora_event = save_guia_envelope(result, source)

        if not envelope.get("duplicate"):
            sheet_row = append_sheet_row(result)
            sheet_written = True

            if result.get("estado") == "OK":
                email_result = safe_send_email(
                    numero_guia=result.get("data", {}).get("numero_guia", ""),
                    estado=result.get("estado"),
                    ai_audit=result.get("ai_audit", {}),
                    blob_url=blob.get("url"),
                )

    return {
        "ok": True,
        "file": source,
        "sheetWritten": sheet_written,
        "sheetRow": sheet_row,
        "upstashSaved": envelope is not None,
        "duplicate": envelope.get("duplicate") if envelope else False,
        "storageKey": envelope.get("storage_key") if envelope else None,
        "bitacoraEvent": bitacora_event,
        "emailResult": email_result,
        "aiAudit": result["ai_audit"],
        "extracted": extracted,
        "validation": validation,
        "review": review,
        "result": result,
    }


def app(environ, start_response):
    try:
        method = environ.get("REQUEST_METHOD", "GET").upper()
        if method == "OPTIONS":
            return response_options(start_response)

        query = get_query_params(environ)

        if not validate_token(query):
            return response_json(start_response, 401, {
                "ok": False,
                "error": "invalid_token",
            })

        if method != "POST":
            return response_json(start_response, 405, {
                "ok": False,
                "error": "method_not_allowed",
            })

        if not os.environ.get("OPENAI_API_KEY"):
            raise ValueError("Missing OPENAI_API_KEY")

        body = read_json_body(environ)
        filename = safe_filename(body.get("filename") or "guia.jpg")
        mime_type = str(body.get("mimeType") or "").strip().lower()

        if mime_type not in ALLOWED_MIME_TYPES:
            return response_json(start_response, 400, {
                "ok": False,
                "error": "unsupported_mime_type",
                "allowedMimeTypes": sorted(ALLOWED_MIME_TYPES),
            })

        binary = decode_image_base64(body.get("imageBase64"))
        blob = upload_blob(filename, mime_type, binary)
        item = process_uploaded_binary(filename, mime_type, binary, blob)

        result = item.get("result", {})
        data = result.get("data", {})
        email_result = item.get("emailResult") or {}

        return response_json(start_response, 200, {
            "ok": True,
            "estado": result.get("estado"),
            "numeroGuia": data.get("numero_guia", ""),
            "camposDudosos": result.get("campos_dudosos", []),
            "duplicate": item.get("duplicate", False),
            "sheetWritten": item.get("sheetWritten", False),
            "storageKey": item.get("storageKey"),
            "emailSent": bool(email_result.get("sent")),
            "emailError": email_result.get("error"),
            "aiAudit": item.get("aiAudit"),
            "blobUrl": blob.get("url"),
            "blobPathname": blob.get("pathname"),
        })

    except Exception as error:
        return response_json(start_response, 500, {
            "ok": False,
            "error": error_payload(error),
        })
