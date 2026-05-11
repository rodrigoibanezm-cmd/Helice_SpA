# extract_guia.py

import json
from datetime import datetime, timezone

from guia_utils import (
    ensure_dirs,
    get_input_files,
)

from guia_ai import (
    extract_data,
    validate_data,
    review_data,
)

from guia_schema import (
    normalize_result,
    VALID_STATES,
)

from guia_config import (
    RESULTS_JSON,
)



def now_iso():
    return datetime.now(timezone.utc).isoformat()



def process_file(image_path):

    extracted = extract_data(image_path)

    validation = validate_data(
        image_path,
        extracted,
    )

    result = {
        **extracted,
        **validation,
    }

    result = normalize_result(result)

    result["fecha_procesamiento"] = now_iso()
    result["review_applied"] = False

    if result["estado"] == "REVISAR":

        result["review_applied"] = True

        review = review_data(
            image_path,
            result,
        )

        corrections = review.get("correcciones", {})

        result["data"].update(corrections)

        result = normalize_result(result)

        estado_final = review.get(
            "estado_final",
            "REVISAR"
        )

        if estado_final not in VALID_STATES:
            estado_final = "REVISAR"

        result["estado"] = estado_final

        result["observaciones"] = review.get(
            "observaciones_finales",
            result["observaciones"],
        )

    return result



def main():

    ensure_dirs()

    files = get_input_files()

    if not files:
        print("No se encontraron archivos.")
        return

    results = []

    for image_path in files:

        print(f"\nProcesando: {image_path.name}")

        try:

            result = process_file(image_path)

            result["archivo"] = image_path.name

            results.append(result)

            print(json.dumps(
                result,
                ensure_ascii=False,
                indent=2,
            ))

        except Exception as e:

            error_result = {
                "archivo": image_path.name,
                "fecha_procesamiento": now_iso(),
                "review_applied": False,
                "estado": "ERROR",
                "error": str(e),
            }

            results.append(error_result)

            print(json.dumps(
                error_result,
                ensure_ascii=False,
                indent=2,
            ))

    with open(
        RESULTS_JSON,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            results,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print("\nResultado guardado en:")
    print(RESULTS_JSON)


if __name__ == "__main__":
    main()
