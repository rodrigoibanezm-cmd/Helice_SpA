# Architecture

## Arquitectura actual validada

```txt
Google Drive
    ↓
process-google.py
    ↓
OpenAI Vision
    ↓
Normalización
    ↓
Google Sheets
```

## Componentes principales

```txt
api/dev/process-google.py
```

Responsable de:

```txt
- leer Drive
- descargar imágenes
- ejecutar extracción
- ejecutar validación
- ejecutar review
- normalizar resultado
- escribir Sheets
```

## Flujo IA

```txt
guia_ai.py
```

Contiene:

```txt
extract_data()
validate_data()
review_data()
```

## Normalización

```txt
guia_schema.py
```

Responsable de:

```txt
- estados válidos
- estructura final
- defaults
- normalización
```

## Prompts

```txt
guia_prompts.py
```

Contiene prompts de:

```txt
- extracción
- validación
- review
```
