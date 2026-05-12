# guia_prompts.py

import json


def extraction_prompt():
    return """
Extrae datos de esta guía de despacho.

Devuelve SOLO JSON puro. Sin markdown. Sin explicación.

Formato obligatorio:
{
  "proveedor_layout": "DESCONOCIDO",
  "data": {
    "correlativo": "",
    "tipo_guia": "",
    "numero_guia": "",
    "marca": "",
    "modelo": "",
    "chassis_serie": "",
    "posicion_lote_codigo": "",
    "destino_empresa": "",
    "destino_direccion": "",
    "destino_comuna": "",
    "origen": "",
    "comentarios": "",
    "tipo_factura": ""
  }
}

Reglas:
- no inventes datos.
- si no encuentras un dato, usa "".

- proveedor_layout debe ser:
  DERCO,
  ALAMEDA,
  INCHCAPE_AUTOMOTRIZ,
  INCHCAPE_COMERCIAL
  o DESCONOCIDO.

- correlativo debe quedar siempre "".
- origen debe quedar siempre "Lo Boza".
- tipo_factura debe quedar siempre "".

- posicion_lote_codigo:
  - si proveedor_layout es INCHCAPE_AUTOMOTRIZ, extrae Posición.
  - si proveedor_layout es INCHCAPE_COMERCIAL, extrae Lote.
  - si proveedor_layout es DERCO o ALAMEDA, extrae Código.

- no uses código modelo como posicion_lote_codigo.
- no uses cantidad como posicion_lote_codigo.
- no uses la palabra "lote" o "código"; usa el valor.

- comentarios:
  solo comentario ocasional explícito escrito para el cliente.
  NO incluir:
  - "por cuenta y orden"
  - "indicador de traslado"
  - texto legal
  - texto estructural
  - encabezados operacionales

  si no hay comentario humano claro, usar "".
"""


def validation_prompt(extracted_data):
    return f"""
Valida contra la imagen los datos extraídos.

Datos extraídos:
{json.dumps(extracted_data, ensure_ascii=False, indent=2)}

Devuelve SOLO JSON puro. Sin markdown. Sin explicación.

Formato obligatorio:
{{
  "estado": "OK",
  "campos_dudosos": [],
  "observaciones": []
}}

Estado:
- OK si los campos clave son claros.
- REVISAR si hay duda.

Campos clave:
- numero_guia
- marca
- modelo
- chassis_serie
- posicion_lote_codigo

Marcar REVISAR si:
- posicion_lote_codigo está vacío.
- posicion_lote_codigo es "lote", "posición" o "código".
- posicion_lote_codigo parece cantidad.
- posicion_lote_codigo parece código modelo.
- hay mezcla entre empresa/dirección/comuna.

No re-extraigas datos.
No modifiques campos.
Solo valida.
"""


def review_prompt(validated):
    return f"""
Revisa nuevamente SOLO los campos dudosos.

Campos dudosos:
{json.dumps(validated.get("campos_dudosos", []), ensure_ascii=False)}

Datos actuales:
{json.dumps(validated.get("data", {}), ensure_ascii=False, indent=2)}

Devuelve SOLO JSON puro. Sin markdown. Sin explicación.

Formato obligatorio:
{{
  "correcciones": {{}},
  "estado_final": "OK",
  "observaciones_finales": []
}}

Reglas:
- solo corregir campos dudosos.
- no modificar otros campos.
- si sigue dudoso, estado_final = "REVISAR".
"""