# Helice SpA

MVP de captura y procesamiento de guías de despacho para Helice SpA.

El sistema toma imágenes de guías desde Google Drive, extrae datos con OpenAI Vision, normaliza el resultado, guarda respaldo estructurado en Upstash Redis y escribe filas limpias en Google Sheets según el formato solicitado por el cliente.

Este README es solo el mapa ejecutivo. La verdad técnica vive en `docs/`.

## Principio central

```txt
Drive recibe imágenes.
Python procesa guías.
OpenAI extrae y valida.
Upstash guarda respaldo y bitácora.
Google Sheets recibe filas A:K solo para guías nuevas.
```

## Estado operativo actual

Existen dos formas operativas:

```txt
1. Batch Drive
   Procesa todas las imágenes existentes en Google Drive / pendientes.

2. Upload unitario
   Recibe una imagen desde front/Lovable, la sube a Drive / pendientes,
   procesa ese mismo file_id y la mueve a procesadas o errores.
```

## Endpoint batch

```txt
GET /api/dev/process-google.py
```

Wrapper legacy de:

```txt
api/dev/process_google.py
```

Modos disponibles:

```txt
mode=list          -> lista pendientes sin OpenAI
mode=process       -> procesa batch completo
mode=move-dry-run  -> muestra qué movería sin mover
mode=move          -> mueve pendientes a procesadas
```

## Endpoint unitario para front

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
  "numeroGuia": "492060",
  "duplicate": false,
  "sheetWritten": true,
  "storageKey": "helice:guia:numero:492060",
  "movedTo": "processed"
}
```

## Reglas actuales

```txt
- procesa N imágenes en batch
- procesa 1 imagen por request en upload unitario
- no cae el batch completo si una imagen falla
- detecta duplicados por numero_guia
- duplicados no se escriben en Sheets
- duplicados sí se guardan en Upstash con sufijo _resp
- bitácora append-only en Upstash
- upload unitario mueve solo el file_id recién creado
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

## Carpetas Drive

```txt
GOOGLE_DRIVE_FOLDER_ID = pendientes
GOOGLE_DRIVE_PROCESSED_FOLDER_ID = procesadas
GOOGLE_DRIVE_ERROR_FOLDER_ID = errores
```

## Variables de entorno aprobadas

```txt
OPENAI_API_KEY
GOOGLE_CLIENT_EMAIL
GOOGLE_PRIVATE_KEY
GOOGLE_SHEET_ID
GOOGLE_DRIVE_FOLDER_ID
GOOGLE_DRIVE_PROCESSED_FOLDER_ID
GOOGLE_DRIVE_ERROR_FOLDER_ID
KV_REST_API_URL
KV_REST_API_TOKEN
UPLOAD_PROCESS_TOKEN
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
