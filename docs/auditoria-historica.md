# Auditoría histórica de guías

## Estado

Diseño aprobado. Pendiente implementación.

## Problema

El sistema ha procesado aproximadamente 165 fichas/guías. Algunas fueron reportadas con errores de extracción.

El problema no es solo detectar guías en estado `REVISAR`. Existen casos donde la extracción pudo quedar marcada como `OK`, pero contener errores reales al comparar contra la foto original.

## Objetivo

Crear un agente auditor que revise el historial completo de guías procesadas y determine:

1. Cuántas extracciones quedaron mal.
2. De las malas, cuántas pasadas de IA tuvieron (`stepsCount`).
3. Si existe un patrón de error.
4. Qué corrección debe aplicarse al extractor para evitar recurrencia.

## Alcance

El agente debe revisar todas las keys del namespace:

```txt
helice:guia:numero:*
```

No debe limitarse a un proveedor específico. La agrupación por `proveedor_layout` se hace después, en el resumen.

## Flujo esperado

El operador debe poder indicar:

```txt
audita
```

Y el agente debe:

```txt
1. Buscar keys helice:guia:numero:*
2. Tomar una key pendiente de auditoría
3. Si audit.estado ya existe, saltarla
4. Leer el envelope guardado en Upstash
5. Tomar la foto desde source.blob.url
6. Comparar foto original vs result.data
7. Opcionalmente comparar contra Google Sheets
8. Escribir el resultado de auditoría dentro de la misma key
9. Pasar a la siguiente key
10. Generar resumen final
```

## Regla de seguridad

El agente auditor no debe corregir datos extraídos.

No debe:

```txt
- modificar result.data
- modificar Google Sheets
- eliminar keys
- reescribir fotos
- reprocesar la guía como extracción nueva
```

Solo puede agregar o actualizar el campo:

```txt
audit
```

## Campo audit

Cada envelope debe poder recibir un bloque nuevo:

```json
{
  "audit": {
    "estado": "OK | ERROR | DUDA",
    "audited_at": "2026-06-09T00:00:00Z",
    "auditor_version": "full_audit_v1",
    "campos_auditados": [
      "numero_guia",
      "marca",
      "modelo",
      "chassis_serie",
      "posicion_lote_codigo",
      "destino_empresa",
      "destino_direccion",
      "destino_comuna",
      "origen",
      "tipo_guia"
    ],
    "errores": [],
    "patrones": [],
    "steps_count": 2,
    "review_applied": false,
    "requires_extractor_fix": false
  }
}
```

## Estados de auditoría

```txt
OK
- La foto coincide razonablemente con los datos extraídos.

ERROR
- Existe una diferencia clara entre la foto y los datos extraídos en un campo relevante.

DUDA
- La foto no permite validar con certeza, falta evidencia, o el campo no es legible.
```

## Campos críticos

```txt
numero_guia
chassis_serie
modelo
destino_empresa
destino_comuna
```

Errores en estos campos deben marcar `ERROR` salvo que la imagen sea ilegible, en cuyo caso debe marcar `DUDA`.

## Campos secundarios

```txt
marca
destino_direccion
origen
posicion_lote_codigo
tipo_guia
```

Errores en estos campos también se registran, pero el resumen debe distinguir severidad.

## Ejemplo audit OK

```json
{
  "audit": {
    "estado": "OK",
    "audited_at": "2026-06-09T00:00:00Z",
    "auditor_version": "full_audit_v1",
    "errores": [],
    "patrones": [],
    "steps_count": 2,
    "review_applied": false,
    "requires_extractor_fix": false
  }
}
```

## Ejemplo audit ERROR

```json
{
  "audit": {
    "estado": "ERROR",
    "audited_at": "2026-06-09T00:00:00Z",
    "auditor_version": "full_audit_v1",
    "errores": [
      {
        "campo": "chassis_serie",
        "valor_extraido": "JF2GU45M3TG086021",
        "valor_imagen": "JF2GU45M3TG086O21",
        "tipo_error": "OCR_0_O",
        "severidad": "CRITICO"
      }
    ],
    "patrones": ["OCR_0_O"],
    "steps_count": 2,
    "review_applied": false,
    "requires_extractor_fix": true
  }
}
```

## Resumen esperado

Al terminar, el agente debe entregar:

```txt
Total keys encontradas
Total auditadas
Total saltadas por audit existente
OK
ERROR
DUDA
Errores por campo
Errores por proveedor_layout
Errores por stepsCount
Errores con review_applied=true
Errores con review_applied=false
Patrones detectados
Corrección sugerida al extractor
```

## Patrones a detectar

```txt
OCR 0/O
OCR 1/I
OCR 5/S
OCR 8/B
G/6
Z/2
campo cortado
campo tomado desde zona equivocada
modelo incompleto
chassis_serie con largo distinto a 17
chassis_serie con caracteres inválidos
error concentrado por proveedor_layout
error concentrado por fecha/tamaño/resolución de imagen
```

## Relación con resolución de fotos

Existe una hipótesis pendiente: en algún momento se redujo la resolución de las fotos para evitar problemas de tamaño al guardar en Vercel Blob.

La auditoría debe permitir revisar si la tasa de error subió después de ese cambio.

La corrección posterior podría ser:

```txt
- usar imagen de mayor resolución para extracción
- comprimir solo después para Blob
- guardar metadata de tamaño/resolución
```

Pero esa decisión depende del resultado de la auditoría.

## Decisión de diseño

Primero se implementa auditoría histórica.

Después, con evidencia, se ajusta el extractor.

No se debe modificar el extractor antes de saber:

```txt
- cuántas fichas están malas
- qué campos fallan
- cuántas pasadas IA tenían
- si existe patrón repetible
```
