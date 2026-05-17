# Operations

## Flujo operativo actual

```txt
1. operador sube imágenes a carpeta pendientes
2. endpoint process-google.py procesa todas las imágenes secuencialmente
3. Upstash guarda respaldo estructurado por guía
4. Google Sheets recibe solo guías nuevas
5. operador revisa resultado
```

## Endpoint operativo

```txt
GET /api/dev/process-google.py
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

Prueba validada:

```txt
mode=list
totalImages=5
files:
- guia_04.jpg
- guia_03.jpg
- guia1.jpeg
- guia_01.jpg
- guia_02.jpg
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

Se usa una Redis existente con namespace:

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

El endpoint procesa todas las imágenes encontradas en pendientes.

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

## Pruebas validadas

Primera corrida individual:

```txt
duplicate=False
storageKey=helice:guia:numero:492060
upstashSaved=True
sheetWritten=True
```

Segunda corrida individual:

```txt
duplicate=True
storageKey=helice:guia:numero:492060_resp
upstashSaved=True
sheetWritten=False
```

Batch duplicado limpio:

```txt
totalImages=5
processed=5
written=0
duplicates=5
errors=0
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
