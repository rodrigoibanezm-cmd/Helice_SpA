# Operations

## Flujo operativo actual

```txt
1. operador sube imagen a carpeta pendientes
2. endpoint process-google.py procesa imagen
3. Google Sheets recibe fila
4. Upstash guarda respaldo estructurado
5. operador revisa resultado
```

## Endpoint operativo

```txt
GET /api/dev/process-google.py
```

## Google Sheets

Pestañas existentes:

```txt
CAPTURA_ACTUAL
HISTORICO
```

Estado actual validado:

```txt
- Sheets recibe fila A:K
- duplicados también se escriben en Sheets
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
- se guardan con sufijo
- se escriben igual en Sheets
- se registra bitácora
```

## Bitácora

Bitácora append-only:

```txt
helice:bitacora
```

Se escribe con LPUSH.

## Prueba validada

Primera corrida:

```txt
duplicate=False
storageKey=helice:guia:numero:492060
upstashSaved=True
sheetWritten=True
```

Segunda corrida:

```txt
duplicate=True
storageKey=helice:guia:numero:492060_resp
upstashSaved=True
sheetWritten=True
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
