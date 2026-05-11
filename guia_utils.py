# guia_utils.py

import base64
import json

from guia_config import (
    INPUT_DIR,
    OUTPUT_DIR,
    ERROR_DIR,
    PROCESSED_DIR,
    VALID_EXTENSIONS
)


def ensure_dirs():
    INPUT_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    ERROR_DIR.mkdir(exist_ok=True)
    PROCESSED_DIR.mkdir(exist_ok=True)



def file_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")



def clean_json(text):
    text = text.strip()

    text = (
        text
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError(
            f"No se encontró JSON válido:\n{text}"
        )

    text = text[start:end + 1]

    return json.loads(text)



def get_input_files():
    return sorted([
        p for p in INPUT_DIR.iterdir()
        if (
            p.is_file()
            and p.suffix.lower() in VALID_EXTENSIONS
        )
    ])
