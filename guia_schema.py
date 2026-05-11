# guia_schema.py

REQUIRED_DATA_FIELDS = (
    "correlativo",
    "tipo_guia",
    "numero_guia",
    "marca",
    "modelo",
    "chassis_serie",
    "posicion_lote_codigo",
    "destino_empresa",
    "destino_direccion",
    "destino_comuna",
    "origen",
    "comentarios",
    "tipo_factura",
)

VALID_STATES = frozenset({
    "OK",
    "REVISAR",
    "ERROR",
})

VALID_LAYOUTS = frozenset({
    "DERCO",
    "ALAMEDA",
    "INCHCAPE_AUTOMOTRIZ",
    "INCHCAPE_COMERCIAL",
    "DESCONOCIDO",
})



def empty_data():
    return {
        field: ""
        for field in REQUIRED_DATA_FIELDS
    }



def normalize_data(data):
    normalized = empty_data()

    for field in REQUIRED_DATA_FIELDS:
        value = data.get(field, "")

        normalized[field] = (
            ""
            if value is None
            else str(value).strip()
        )

    return normalized



def apply_business_rules(data):
    data = dict(data)

    data["correlativo"] = ""
    data["origen"] = "Lo Boza"
    data["tipo_factura"] = ""
    data["tipo_guia"] = "GUIA DE DESPACHO ELECTRONICA"
    data["comentarios"] = ""

    return data



def normalize_result(result):
    data = normalize_data(
        result.get("data", result)
    )

    data = apply_business_rules(data)

    layout = result.get(
        "proveedor_layout",
        "DESCONOCIDO"
    )

    if layout not in VALID_LAYOUTS:
        layout = "DESCONOCIDO"

    estado = result.get(
        "estado",
        "REVISAR"
    )

    if estado not in VALID_STATES:
        estado = "REVISAR"

    campos_dudosos = result.get(
        "campos_dudosos",
        []
    )

    if estado == "OK":
        campos_dudosos = []

    return {
        "proveedor_layout": layout,
        "data": data,
        "estado": estado,
        "campos_dudosos": campos_dudosos,
        "observaciones": result.get("observaciones", []),
    }



def is_ok(result):
    return result.get("estado") == "OK"
