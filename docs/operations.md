# Operations

## Flujos operativos actuales

Existen dos flujos válidos.

### A. Batch Drive

```txt
1. operador sube imágenes a carpeta pendientes
2. endpoint process-google.py procesa todas las imágenes secuencialmente
3. Upstash guarda respaldo estructurado por guía
4. Google Sheets recibe solo guías nuevas
5. operador mueve pendientes procesadas a carpeta procesadas
6. operador revisa resultado
```

### B. Upload unitario (Lovable/front)

```txt
1. front envía imagen base64
2. upload-and-process.py valida token
3. sube la imagen a Drive / pendientes
4. procesa SOLO ese file_id
5. Upstash guarda respaldo estructurado
6. Google Sheets escribe si no es duplicado
7. mueve a procesadas o errores
8. devuelve resultado corto al front
```

## Endpoint batch

```txt
GET /api/dev/process-google.py
```

Wrapper legacy de:

```txt
api/dev/process_google.py
```

## Endpoint upload unitario

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

## Modo seguro sin OpenAI

Para listar pendientes sin gastar tokens ni tocar Sheets/Upstash:

```txt
GET /api/dev/process-google.py?mode=list
```

Este modo solo hace:

```txt
- lista archivos de Drive
- filtra imágenes
- devuelve totalFiles, totalImages y files[]
```

No hace:

```txt
- descarga de imágenes
- OpenAI
- escritura Sheets
- escritura Upstash
```

## Movimiento de archivos Drive

Carpetas:

```txt
GOOGLE_DRIVE_FOLDER_ID = pendientes
GOOGLE_DRIVE_PROCESSED_FOLDER_ID = procesadas
GOOGLE_DRIVE_ERROR_FOLDER_ID = errores
```

### Dry-run

```txt
GET /api/dev/process-google.py?mode=move-dry-run
```

### Move real batch

```txt
GET /api/dev/process-google.py?mode=move
```

### Movimiento upload unitario

```txt
upload-and-process.py mueve solo el file_id recién creado.
No lista pendientes.
No toca otras imágenes.
```

## Google Sheets

Pestañas existentes:

```txt
CAPTURA_ACTUAL
HISTORICO
```

Estado actual validado:

```txt
- Sheets recibe fila A:K solo si la guía no es duplicada
- duplicados NO se escriben en Sheets
- duplicados sí se guardan en Upstash
```

Objetivo operativo:

```txt
Sheets = operación limpia
Upstash = histórico técnico / auditoría
```

## Upstash Redis

Namespace:

```txt
helice:
```

Variables usadas:

```txt
KV_REST_API_URL
KV_REST_API_TOKEN
```

## Política de duplicados

Identificador:

```txt
numero_guia normalizado
```

Primera vez:

```txt
helice:guia:numero:{numero_guia}
```

Duplicado:

```txt
helice:guia:numero:{numero_guia}_resp
helice:guia:numero:{numero_guia}_resp_2
helice:guia:numero:{numero_guia}_resp_3
```

Regla MVP:

```txt
- no se bloquean duplicados
- se guardan con sufijo en Upstash
- no se escriben en Sheets
- se registra bitácora
```

## Batch

El endpoint batch procesa todas las imágenes encontradas en pendientes.

Reglas:

```txt
- procesamiento secuencial
- si una imagen falla, no cae todo el batch
- errors cuenta fallas aisladas
- processed cuenta imágenes procesadas exitosamente
- written cuenta filas efectivamente escritas en Sheets
- duplicates cuenta guías repetidas detectadas por numero_guia
```

## Bitácora

Bitácora append-only:

```txt
helice:bitacora
```

Se escribe con LPUSH.

## Runtime validado

```txt
Vercel Python runtime
```

## Dependencias runtime

```txt
openai
google-api-python-client
google-auth
```
