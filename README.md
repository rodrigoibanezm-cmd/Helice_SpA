# Helice SpA

MVP de captura y procesamiento de guías de despacho para Helice SpA.

El sistema toma imágenes de guías desde Google Drive, extrae datos con OpenAI Vision, normaliza el resultado y escribe una fila en Google Sheets según el formato solicitado por el cliente.

Este README es solo el mapa ejecutivo. La verdad técnica vive en `docs/`.

## Principio central

```txt
Drive recibe imágenes.
Python procesa guías.
OpenAI extrae y valida.
Google Sheets recibe filas A:K.
```

## Estado operativo actual

El flujo validado actualmente es:

```txt
Google Drive / pendientes
→ descarga primera imagen
→ extracción OpenAI Vision
→ validación
→ review si corresponde
→ normalización
→ escritura en Google Sheets
```

Está probado end-to-end con una guía DERCO.

## Endpoint operativo actual

```txt
GET /api/dev/process-google.py
```

Este endpoint:

```txt
- lee GOOGLE_DRIVE_FOLDER_ID
- descarga una imagen desde Drive
- procesa la guía
- escribe una fila en Google Sheets
- devuelve JSON de auditoría
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

```txt
OPENAI_API_KEY
GOOGLE_CLIENT_EMAIL
GOOGLE_PRIVATE_KEY
GOOGLE_SHEET_ID
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
