export const REQUIRED_DATA_FIELDS = [
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
];

export const VALID_STATES = new Set(["OK", "REVISAR", "ERROR"]);

export const VALID_LAYOUTS = new Set([
  "DERCO",
  "ALAMEDA",
  "INCHCAPE_AUTOMOTRIZ",
  "INCHCAPE_COMERCIAL",
  "DESCONOCIDO",
]);

export function emptyData() {
  return Object.fromEntries(REQUIRED_DATA_FIELDS.map((field) => [field, ""]));
}

export function normalizeData(data = {}) {
  const normalized = emptyData();

  for (const field of REQUIRED_DATA_FIELDS) {
    const value = data[field];
    normalized[field] = value === null || value === undefined ? "" : String(value).trim();
  }

  return normalized;
}

export function applyBusinessRules(data = {}) {
  return {
    ...data,
    correlativo: "",
    origen: "Lo Boza",
    tipo_factura: "",
    tipo_guia: "GUIA DE DESPACHO ELECTRONICA",
    comentarios: "",
  };
}

export function normalizeResult(result = {}) {
  const rawData = result.data || result;
  const data = applyBusinessRules(normalizeData(rawData));

  let proveedor_layout = result.proveedor_layout || "DESCONOCIDO";
  if (!VALID_LAYOUTS.has(proveedor_layout)) {
    proveedor_layout = "DESCONOCIDO";
  }

  let estado = result.estado || "REVISAR";
  if (!VALID_STATES.has(estado)) {
    estado = "REVISAR";
  }

  let campos_dudosos = Array.isArray(result.campos_dudosos)
    ? result.campos_dudosos
    : [];

  if (estado === "OK") {
    campos_dudosos = [];
  }

  return {
    proveedor_layout,
    data,
    estado,
    campos_dudosos,
    observaciones: Array.isArray(result.observaciones) ? result.observaciones : [],
  };
}

export function isOk(result = {}) {
  return result.estado === "OK";
}
