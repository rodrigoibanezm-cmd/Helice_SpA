# Deuda Técnica

## Quiebres menores actuales

```txt
- algunos destinos todavía llegan parcialmente sucios
- endpoint JS legacy todavía existe
- mode=process y mode=move siguen separados manualmente
- no existe flujo automático correo -> Drive -> proceso
```

## Decisiones congeladas

```txt
- Python como runtime principal
- Google Drive como intake inicial
- Google Sheets como salida operacional
- OpenAI Vision para extracción
- Upstash Redis como respaldo estructurado
- procesamiento batch secuencial
- duplicados no escriben Sheets
```
