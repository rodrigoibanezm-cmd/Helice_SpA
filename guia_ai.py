# guia_ai.py

from openai import OpenAI

from guia_config import (
    EXTRACT_MODEL,
    VALIDATE_MODEL,
    REVIEW_MODEL,
)

from guia_utils import (
    file_to_base64,
    clean_json,
)

from guia_prompts import (
    extraction_prompt,
    validation_prompt,
    review_prompt,
)

client = OpenAI()


def get_image_mime(image_path):
    suffix = image_path.suffix.lower()

    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"

    if suffix == ".png":
        return "image/png"

    raise ValueError(f"Formato no soportado: {suffix}")


def call_vision(image_path, prompt, model):
    b64 = file_to_base64(image_path)
    mime = get_image_mime(image_path)

    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": prompt,
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:{mime};base64,{b64}",
                    },
                ],
            }
        ],
    )

    return clean_json(response.output_text)


def extract_data(image_path):
    return call_vision(
        image_path=image_path,
        prompt=extraction_prompt(),
        model=EXTRACT_MODEL,
    )


def validate_data(image_path, extracted_data):
    return call_vision(
        image_path=image_path,
        prompt=validation_prompt(extracted_data),
        model=VALIDATE_MODEL,
    )


def review_data(image_path, validated_data):
    return call_vision(
        image_path=image_path,
        prompt=review_prompt(validated_data),
        model=REVIEW_MODEL,
    )
