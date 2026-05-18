# Operations

## Flujos operativos actuales

Existen dos flujos válidos.

---

## A. Upload unitario principal (Lovable/front)

Flujo oficial MVP.

```txt
1. front envía imagen base64
2. upload-and-process.py valida token
3. backend guarda foto original en Vercel Blob
4. backend crea archivo temporal
5. OpenAI Vision procesa imagen
6. normalización
7. Upstash guarda envelope por numero_guia
8. Google Sheets escribe si no es duplicado
9. backend devuelve resultado corto al front
```

Estado validado:

```txt
- upload unitario funciona end-to-end
- Vercel Blob guarda evidencia original
- OpenAI extracción OK
- OpenAI validación OK
- Upstash detecta duplicados
- Google Sheets escribe correctamente
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

Respuesta esperada:

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

---

## B. Batch Drive legacy

Flujo histórico/manual.

```txt
1. operador sube imágenes a Drive / pendientes
2. process-google.py procesa batch
3. Upstash guarda respaldo
4. Google Sheets recibe solo guías nuevas
5. operador mueve pendientes procesadas
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
mode=list
mode=process
mode=move-dry-run
mode=move
```

## Modo seguro sin OpenAI

```txt
GET /api/dev/process-google.py?mode=list
```

Solo:

```txt
- lista archivos Drive
- filtra imágenes
- devuelve metadata
```

No hace:

```txt
- OpenAI
- Sheets
- Upstash
```

---

## Vercel Blob

Uso:

```txt
- conservar foto original subida desde front
- evidencia técnica
- auditoría
```

Variable:

```txt
BLOB_READ_WRITE_TOKEN
```

## Google Sheets

Pestañas:

```txt
CAPTURA_ACTUAL
HISTORICO
```

Reglas:

```txt
- Sheets solo recibe guías nuevas
- duplicate=true → no escribe
- duplicate=false → escribe fila
```

## Upstash Redis

Namespace:

```txt
helice:
```

Variables:

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

Duplicados:

```txt
helice:guia:numero:{numero_guia}_resp
helice:guia:numero:{numero_guia}_resp_2
helice:guia:numero:{numero_guia}_resp_3
```

## Regla MVP

```txt
- duplicados sí se guardan en Upstash
- duplicados NO se escriben en Sheets
- Blob guarda evidencia original
- Upstash es la memoria de duplicados
```

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
