# Helice SpA

MVP de captura y procesamiento de guías de despacho para Helice SpA.

El sistema recibe imágenes de guías, extrae datos con OpenAI Vision, normaliza el resultado, guarda respaldo estructurado en Upstash Redis, conserva la foto original en Vercel Blob y escribe filas limpias en Google Sheets según el formato solicitado por el cliente.

Este README es solo el mapa ejecutivo. La verdad técnica vive en `docs/`.

## Principio central

```txt
Front/Lovable recibe imagen.
Vercel Blob guarda la foto original.
Python procesa la guía.
OpenAI extrae y valida.
Upstash guarda respaldo y bitácora.
Google Sheets recibe filas A:K solo para guías nuevas.
```

## Estado operativo actual

Flujo principal validado:

```txt
Lovable / PowerShell
→ POST upload-and-process.py
→ imagen base64
→ Vercel Blob guarda foto original
→ backend procesa archivo temporal
→ OpenAI Vision extrae y valida
→ normalización
→ Upstash guarda envelope por numero_guia
→ Google Sheets escribe si no es duplicado
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
- bitácora append-only en Upstash
```

## Endpoint principal para front

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

Respuesta corta esperada:

```json
{
  "ok": true,
  "estado": "OK",
  "numeroGuia": "164468",
  "duplicate": false,
  "sheetWritten": true,
  "storageKey": "helice:guia:numero:164468",
  "blobUrl": "https://...",
  "blobPathname": "guias/...jpg"
}
```

## Endpoint batch legacy

```txt
GET /api/dev/process-google.py
```

Wrapper legacy de:

```txt
api/dev/process_google.py
```

Uso actual:

```txt
- flujo Drive antiguo/manual
- pruebas batch
- respaldo operativo si se suben imágenes manualmente a Drive / pendientes
```

Modos disponibles:

```txt
mode=list          -> lista pendientes sin OpenAI
mode=process       -> procesa batch completo
mode=move-dry-run  -> muestra qué movería sin mover
mode=move          -> mueve pendientes a procesadas
```

## Reglas actuales

```txt
- upload unitario no usa Drive
- Drive queda solo para batch legacy
- Vercel Blob conserva evidencia original
- Upstash decide duplicados por numero_guia
- Google Sheets solo recibe guías nuevas
- duplicados no se escriben en Sheets
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

## Variables de entorno aprobadas

Flujo principal:

```txt
OPENAI_API_KEY
GOOGLE_CLIENT_EMAIL
GOOGLE_PRIVATE_KEY
GOOGLE_SHEET_ID
KV_REST_API_URL
KV_REST_API_TOKEN
UPLOAD_PROCESS_TOKEN
BLOB_READ_WRITE_TOKEN
```

Flujo batch legacy Drive:

```txt
GOOGLE_DRIVE_FOLDER_ID
GOOGLE_DRIVE_PROCESSED_FOLDER_ID
GOOGLE_DRIVE_ERROR_FOLDER_ID
```

## Runtime

```txt
Python para el flujo principal.
Node.js solo queda para pruebas antiguas/dev.
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
