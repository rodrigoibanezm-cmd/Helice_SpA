# guia_config.py

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

INPUT_DIR = BASE_DIR / "inputs"
OUTPUT_DIR = BASE_DIR / "outputs"
ERROR_DIR = BASE_DIR / "errores"
PROCESSED_DIR = BASE_DIR / "procesados"

VALID_EXTENSIONS = frozenset({
    ".jpg",
    ".jpeg",
    ".png"
})

EXTRACT_MODEL = "gpt-4.1-mini"
VALIDATE_MODEL = "gpt-4.1-mini"
REVIEW_MODEL = "gpt-4.1"

RESULTS_JSON = OUTPUT_DIR / "resultado_guias_v1.json"
