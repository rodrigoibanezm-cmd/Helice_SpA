import json
import os
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from google.oauth2 import service_account
from googleapiclient.discovery import build

from guia_ai import extract_data, validate_data, review_data
from guia_schema import normalize_result, VALID_STATES

CAPTURA_SHEET = "CAPTURA_ACTUAL"
HISTORICO_SHEET = "HISTORICO"
SHEET_RANGE = "A:K"
CAPTURA_DATA_RANGE = "A2:K"


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


def get_sheets_service():
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
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )

    return build("sheets", "v4", credentials=credentials)


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


def write_sheet_row(result):
    spreadsheet_id = os.environ.get("GOOGLE_SHEET_ID")
    if not spreadsheet_id:
        raise ValueError("Missing GOOGLE_SHEET_ID")

    row = build_sheet_row(result)
    sheets = get_sheets_service()

    sheets.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range=f"{CAPTURA_SHEET}!{CAPTURA_DATA_RANGE}",
        body={},
    ).execute()

    sheets.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"{CAPTURA_SHEET}!A2:K2",
        valueInputOption="RAW",
        body={"values": [row]},
    ).execute()

    sheets.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=f"{HISTORICO_SHEET}!{SHEET_RANGE}",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": [row]},
    ).execute()

    return row


append_sheet_row = write_sheet_row


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
