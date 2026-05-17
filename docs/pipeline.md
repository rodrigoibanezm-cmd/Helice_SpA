# Pipeline

## Pipeline actual validado

```txt
1. Usuario sube imagen a Google Drive
2. process-google.py lista archivos
3. descarga imagen
4. OpenAI Vision extrae datos
5. validate_data revisa extracción
6. review_data corrige si estado = REVISAR
7. normalize_result genera estructura final
8. Google Sheets recibe fila A:K
```

## Estado actual

Actualmente:

```txt
- procesa primera imagen encontrada
- escribe una fila
- no mueve archivos
- no controla duplicados
```

## Estado validado

Probado:

```txt
DERCO
GUIA DE DESPACHO ELECTRONICA
```
