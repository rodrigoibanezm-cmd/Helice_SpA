# Helice SpA

MVP de captura y procesamiento de guías de despacho para Helice SpA.

El sistema recibe imágenes de guías, extrae datos con OpenAI Vision, normaliza el resultado, guarda respaldo estructurado en Upstash Redis, conserva la foto original en Vercel Blob, escribe filas limpias en Google Sheets según el formato solicitado por el cliente y envía alerta por correo vía SendGrid cuando una guía nueva queda escrita.

Este README es solo el mapa ejecutivo. La verdad técnica vive en `docs/`.

## Principio central

```txt
Front/Lovable recibe imagen.
Vercel Blob guarda la foto original.
Python procesa la guía.
OpenAI extrae y valida.
Upstash guarda respaldo y bitácora.
Google Sheets recibe filas A:K solo para guías nuevas.
SendGrid envía alerta desde backend.
```

## Flujo operativo validado

```txt
Lovable / PowerShell
→ POST upload-and-process.py
→ imagen base64
→ Vercel Blob guarda foto original
→ backend procesa archivo temporal
→ OpenAI Vision extrae y valida
→ review IA si hay duda
→ normalización
→ Upstash guarda envelope por numero_guia
→ Google Sheets escribe si no es duplicado
→ SendGrid envía alerta si la guía nueva queda OK y escrita
→ respuesta corta al front
```

Estado validado:

```txt
- procesa 1 imagen por request
- guarda foto original en Vercel Blob
- detecta duplicados por numero_guia
- duplicados no se escriben en Sheets
- duplicados sí se guardan en Upstash con sufijo _resp
- guía nueva se escribe correctamente en Google Sheets
- guía nueva OK dispara mail vía SendGrid desde backend
- bitácora append-only en Upstash
- aiAudit informa por cuántos pasos IA pasó la guía
```

## Endpoint principal

```txt
POST /api/dev/upload-and-process.py?token=...
```

Body esperado:

```json
{
  "filename": "guia.jpg",
  "mimeType": "image/jpeg",
  "imageBase64": "..."
}
```

Mime types permitidos:

```txt
image/jpeg
image/png
```

Respuesta esperada:

```json
{
  "ok": true,
  "estado": "OK",
  "numeroGuia": "164468",
  "duplicate": false,
  "sheetWritten": true,
  "storageKey": "helice:guia:numero:164468",
  "emailSent": true,
  "emailError": null,
  "aiAudit": {
    "steps": ["extract", "validate"],
    "stepsCount": 2,
    "reviewApplied": false
  },
  "blobUrl": "https://...",
  "blobPathname": "guias/...jpg"
}
```

Si hubo review IA:

```json
{
  "aiAudit": {
    "steps": ["extract", "validate", "review"],
    "stepsCount": 3,
    "reviewApplied": true
  }
}
```

## Regla de revisión humana

```txt
estado = OK
→ no requiere revisión humana
→ campos_dudosos debe quedar []

estado = REVISAR
→ el front debe pedir validación humana
→ campos_dudosos debe volver informado
```

## Regla de mail

```txt
Proveedor único: SendGrid.
El front no decide destinatario.
El backend lee NOTIFY_TO_EMAIL.
El mail sale solo desde backend.
```

Se envía mail solo si:

```txt
estado = OK
duplicate = false
sheetWritten = true
```

No se envía mail si:

```txt
- la guía es duplicada
- la guía queda REVISAR
- la guía queda ERROR
- no se escribió en Google Sheets
```

## Reglas actuales

```txt
- upload unitario usa Vercel Blob
- Upstash decide duplicados por numero_guia
- Google Sheets solo recibe guías nuevas
- duplicados no se escriben en Sheets
- Vercel Blob conserva evidencia original
- SendGrid notifica guías nuevas OK escritas
- aiAudit queda guardado en Upstash dentro del result
```

## Formato aprobado de Google Sheets

Columnas A:K:

```txt
A correlativo
B tipo_guia
C numero_guia
D marca
E modelo
F chassis_serie
G posicion_lote_codigo
H origen
I destino
J comentarios
K tipo_factura
```

Destino se arma como:

```txt
destino_empresa - destino_direccion - destino_comuna
```

## Escritura en Google Sheets

```txt
CAPTURA_ACTUAL
- conserva encabezado fila 1
- limpia datos desde A2:K
- escribe la última guía en A2:K2

HISTORICO
- agrega cada guía nueva al final
```

## Variables de entorno aprobadas

```txt
OPENAI_API_KEY
GOOGLE_CLIENT_EMAIL
GOOGLE_PRIVATE_KEY
GOOGLE_SHEET_ID
GOOGLE_SHEET_URL
KV_REST_API_URL
KV_REST_API_TOKEN
UPLOAD_PROCESS_TOKEN
BLOB_READ_WRITE_TOKEN
SENDGRID_API_KEY
SENDGRID_FROM_EMAIL
SENDGRID_FROM_NAME
NOTIFY_TO_EMAIL
```

## Runtime

```txt
Python para el flujo principal.
```

## Documentación

```txt
docs/architecture.md
docs/pipeline.md
docs/google-setup.md
docs/data-model.md
docs/operations.md
docs/pendientes.md
docs/deuda-tecnica.md
```