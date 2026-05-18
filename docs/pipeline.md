# Pipeline

## Pipeline actual validado

```txt
1. Operador sube imágenes a Google Drive / pendientes
2. process-google.py lista todas las imágenes
3. procesa batch secuencialmente
4. descarga cada imagen
5. OpenAI Vision extrae datos
6. validate_data revisa extracción
7. review_data corrige si estado = REVISAR
8. normalize_result genera estructura final
9. Upstash guarda envelope por guía
10. Google Sheets recibe fila A:K solo si no es duplicado
11. mode=move mueve pendientes a procesadas
```

## Estados validados

```txt
- procesa N imágenes
- no cae todo el batch si una imagen falla
- detecta duplicados por numero_guia
- duplicados no se escriben en Sheets
- duplicados sí se guardan en Upstash con sufijo _resp
- bitácora append-only en Upstash
- mueve imágenes desde pendientes a procesadas
```

## Modos operativos

```txt
mode=list          -> lista pendientes sin OpenAI
mode=process       -> procesa batch completo
mode=move-dry-run  -> muestra qué movería sin mover
mode=move          -> mueve pendientes a procesadas
```

## Pruebas validadas

```txt
mode=list
totalImages=5
```

```txt
mode=process
totalImages=5
processed=5
written=0
duplicates=5
errors=0
```

```txt
mode=move-dry-run
plannedMoves=5
```

```txt
mode=move
moved=5
errors=0
```
