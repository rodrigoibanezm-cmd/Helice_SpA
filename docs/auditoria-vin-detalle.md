# Auditoria VIN - detalle de revision

Este documento complementa:

- `docs/auditoria-vin-resumen.md`
- `docs/auditoria-vin-plan.md`

Objetivo: dejar trazabilidad de la auditoria manual, incluyendo lista completa de keys revisadas y detalle de los 37 errores VIN confirmados.

## Resultado final

- 37 errores de chasis / VIN confirmados.
- 1 imagen no procesable.
- 38 casos problematicos totales.

La imagen no procesable fue la guia `495320`.

## Regla de datos

No inventar datos.

Si falta el VIN correcto, marcar `PENDIENTE_CONFIRMAR`.
Si falta el VIN leido desde el JSON de Upstash, marcar `PENDIENTE_CONFIRMAR`.

## Lista completa de keys revisadas

```txt
helice:guia:numero:121556
helice:guia:numero:121767
helice:guia:numero:122406
helice:guia:numero:173544
helice:guia:numero:173810
helice:guia:numero:173842
helice:guia:numero:173840
helice:guia:numero:494287
helice:guia:numero:494332
helice:guia:numero:494531
helice:guia:numero:494492
helice:guia:numero:494550
helice:guia:numero:495089
helice:guia:numero:495322
helice:guia:numero:59515
helice:guia:numero:59546
helice:guia:numero:59630
helice:guia:numero:59632
helice:guia:numero:603622
helice:guia:numero:59710
helice:guia:numero:59725
helice:guia:numero:59674
helice:guia:numero:603623
helice:guia:numero:603862
helice:guia:numero:604011
helice:guia:numero:604028
helice:guia:numero:604029
helice:guia:numero:604034
helice:guia:numero:604035
helice:guia:numero:604057
helice:guia:numero:604113
helice:guia:numero:604228
helice:guia:numero:604391
helice:guia:numero:604401
helice:guia:numero:604400
helice:guia:numero:604800
helice:guia:numero:604542
```

## Comando Upstash usado como fuente

```redis
MGET helice:guia:numero:121556 helice:guia:numero:121767 helice:guia:numero:122406 helice:guia:numero:173544 helice:guia:numero:173810 helice:guia:numero:173842 helice:guia:numero:173840 helice:guia:numero:494287 helice:guia:numero:494332 helice:guia:numero:494531 helice:guia:numero:494492 helice:guia:numero:494550 helice:guia:numero:495089 helice:guia:numero:495322 helice:guia:numero:59515 helice:guia:numero:59546 helice:guia:numero:59630 helice:guia:numero:59632 helice:guia:numero:603622 helice:guia:numero:59710 helice:guia:numero:59725 helice:guia:numero:59674 helice:guia:numero:603623 helice:guia:numero:603862 helice:guia:numero:604011 helice:guia:numero:604028 helice:guia:numero:604029 helice:guia:numero:604034 helice:guia:numero:604035 helice:guia:numero:604057 helice:guia:numero:604113 helice:guia:numero:604228 helice:guia:numero:604391 helice:guia:numero:604401 helice:guia:numero:604400 helice:guia:numero:604800 helice:guia:numero:604542
```

## Tabla de 37 errores VIN confirmados

| numero_guia | key_upstash | vin_leido | vin_correcto | tipo_error | observacion |
|---:|---|---|---|---|---|
| 121556 | `helice:guia:numero:121556` | PENDIENTE_CONFIRMAR | PENDIENTE_CONFIRMAR | VIN_MAL_LEIDO | Error VIN confirmado; falta completar con JSON/foto. |
| 121767 | `helice:guia:numero:121767` | PENDIENTE_CONFIRMAR | PENDIENTE_CONFIRMAR | VIN_MAL_LEIDO | Error VIN confirmado; falta completar con JSON/foto. |
| 122406 | `helice:guia:numero:122406` | PENDIENTE_CONFIRMAR | PENDIENTE_CONFIRMAR | VIN_MAL_LEIDO | Error VIN confirmado; falta completar con JSON/foto. |
| 173544 | `helice:guia:numero:173544` | PENDIENTE_CONFIRMAR | PENDIENTE_CONFIRMAR | VIN_MAL_LEIDO | Error VIN confirmado; falta completar con JSON/foto. |
| 173810 | `helice:guia:numero:173810` | PENDIENTE_CONFIRMAR | PENDIENTE_CONFIRMAR | VIN_MAL_LEIDO | Error VIN confirmado; falta completar con JSON/foto. |
| 173842 | `helice:guia:numero:173842` | PENDIENTE_CONFIRMAR | PENDIENTE_CONFIRMAR | VIN_MAL_LEIDO | Error VIN confirmado; falta completar con JSON/foto. |
| 173840 | `helice:guia:numero:173840` | PENDIENTE_CONFIRMAR | PENDIENTE_CONFIRMAR | VIN_MAL_LEIDO | Error VIN confirmado; falta completar con JSON/foto. |
| 494287 | `helice:guia:numero:494287` | PENDIENTE_CONFIRMAR | PENDIENTE_CONFIRMAR | VIN_MAL_LEIDO | Error VIN confirmado; falta completar con JSON/foto. |
| 494332 | `helice:guia:numero:494332` | PENDIENTE_CONFIRMAR | PENDIENTE_CONFIRMAR | VIN_MAL_LEIDO | Error VIN confirmado; falta completar con JSON/foto. |
| 494531 | `helice:guia:numero:494531` | PENDIENTE_CONFIRMAR | PENDIENTE_CONFIRMAR | VIN_MAL_LEIDO | Error VIN confirmado; falta completar con JSON/foto. |
| 494492 | `helice:guia:numero:494492` | PENDIENTE_CONFIRMAR | PENDIENTE_CONFIRMAR | VIN_MAL_LEIDO | Error VIN confirmado; falta completar con JSON/foto. |
| 494550 | `helice:guia:numero:494550` | PENDIENTE_CONFIRMAR | PENDIENTE_CONFIRMAR | VIN_MAL_LEIDO | Error VIN confirmado; falta completar con JSON/foto. |
| 495089 | `helice:guia:numero:495089` | PENDIENTE_CONFIRMAR | PENDIENTE_CONFIRMAR | VIN_MAL_LEIDO | Error VIN confirmado; falta completar con JSON/foto. |
| 495322 | `helice:guia:numero:495322` | PENDIENTE_CONFIRMAR | PENDIENTE_CONFIRMAR | VIN_MAL_LEIDO | Error VIN confirmado; falta completar con JSON/foto. |
| 59515 | `helice:guia:numero:59515` | PENDIENTE_CONFIRMAR | PENDIENTE_CONFIRMAR | VIN_MAL_LEIDO | Error VIN confirmado; falta completar con JSON/foto. |
| 59546 | `helice:guia:numero:59546` | PENDIENTE_CONFIRMAR | PENDIENTE_CONFIRMAR | VIN_MAL_LEIDO | Error VIN confirmado; falta completar con JSON/foto. |
| 59630 | `helice:guia:numero:59630` | PENDIENTE_CONFIRMAR | PENDIENTE_CONFIRMAR | VIN_MAL_LEIDO | Error VIN confirmado; falta completar con JSON/foto. |
| 59632 | `helice:guia:numero:59632` | PENDIENTE_CONFIRMAR | PENDIENTE_CONFIRMAR | VIN_MAL_LEIDO | Error VIN confirmado; falta completar con JSON/foto. |
| 603622 | `helice:guia:numero:603622` | PENDIENTE_CONFIRMAR | PENDIENTE_CONFIRMAR | VIN_MAL_LEIDO | Error VIN confirmado; falta completar con JSON/foto. |
| 59710 | `helice:guia:numero:59710` | PENDIENTE_CONFIRMAR | PENDIENTE_CONFIRMAR | VIN_MAL_LEIDO | Error VIN confirmado; falta completar con JSON/foto. |
| 59725 | `helice:guia:numero:59725` | PENDIENTE_CONFIRMAR | PENDIENTE_CONFIRMAR | VIN_MAL_LEIDO | Error VIN confirmado; falta completar con JSON/foto. |
| 59674 | `helice:guia:numero:59674` | PENDIENTE_CONFIRMAR | PENDIENTE_CONFIRMAR | VIN_MAL_LEIDO | Error VIN confirmado; falta completar con JSON/foto. |
| 603623 | `helice:guia:numero:603623` | PENDIENTE_CONFIRMAR | PENDIENTE_CONFIRMAR | VIN_MAL_LEIDO | Error VIN confirmado; falta completar con JSON/foto. |
| 603862 | `helice:guia:numero:603862` | PENDIENTE_CONFIRMAR | PENDIENTE_CONFIRMAR | VIN_MAL_LEIDO | Error VIN confirmado; falta completar con JSON/foto. |
| 604011 | `helice:guia:numero:604011` | PENDIENTE_CONFIRMAR | PENDIENTE_CONFIRMAR | VIN_MAL_LEIDO | Error VIN confirmado; falta completar con JSON/foto. |
| 604028 | `helice:guia:numero:604028` | PENDIENTE_CONFIRMAR | PENDIENTE_CONFIRMAR | VIN_MAL_LEIDO | Error VIN confirmado; falta completar con JSON/foto. |
| 604029 | `helice:guia:numero:604029` | PENDIENTE_CONFIRMAR | PENDIENTE_CONFIRMAR | VIN_MAL_LEIDO | Error VIN confirmado; falta completar con JSON/foto. |
| 604034 | `helice:guia:numero:604034` | PENDIENTE_CONFIRMAR | PENDIENTE_CONFIRMAR | VIN_MAL_LEIDO | Error VIN confirmado; falta completar con JSON/foto. |
| 604035 | `helice:guia:numero:604035` | PENDIENTE_CONFIRMAR | PENDIENTE_CONFIRMAR | VIN_MAL_LEIDO | Error VIN confirmado; falta completar con JSON/foto. |
| 604057 | `helice:guia:numero:604057` | PENDIENTE_CONFIRMAR | PENDIENTE_CONFIRMAR | VIN_MAL_LEIDO | Error VIN confirmado; falta completar con JSON/foto. |
| 604113 | `helice:guia:numero:604113` | PENDIENTE_CONFIRMAR | PENDIENTE_CONFIRMAR | VIN_MAL_LEIDO | Error VIN confirmado; falta completar con JSON/foto. |
| 604228 | `helice:guia:numero:604228` | PENDIENTE_CONFIRMAR | PENDIENTE_CONFIRMAR | VIN_MAL_LEIDO | Error VIN confirmado; falta completar con JSON/foto. |
| 604391 | `helice:guia:numero:604391` | PENDIENTE_CONFIRMAR | PENDIENTE_CONFIRMAR | VIN_MAL_LEIDO | Error VIN confirmado; falta completar con JSON/foto. |
| 604401 | `helice:guia:numero:604401` | PENDIENTE_CONFIRMAR | PENDIENTE_CONFIRMAR | VIN_MAL_LEIDO | Error VIN confirmado; falta completar con JSON/foto. |
| 604400 | `helice:guia:numero:604400` | PENDIENTE_CONFIRMAR | PENDIENTE_CONFIRMAR | VIN_MAL_LEIDO | Error VIN confirmado; falta completar con JSON/foto. |
| 604800 | `helice:guia:numero:604800` | PENDIENTE_CONFIRMAR | PENDIENTE_CONFIRMAR | VIN_MAL_LEIDO | Error VIN confirmado; falta completar con JSON/foto. |
| 604542 | `helice:guia:numero:604542` | PENDIENTE_CONFIRMAR | PENDIENTE_CONFIRMAR | VIN_MAL_LEIDO | Error VIN confirmado; falta completar con JSON/foto. |

## Imagen no procesable

| numero_guia | key_upstash | estado | observacion |
|---:|---|---|---|
| 495320 | `helice:guia:numero:495320` | IMAGEN_NO_PROCESABLE | Caso separado de los 37 errores VIN. No contabilizar como VIN malo. |

## Pendiente para cierre fino

1. Pegar resultado completo del `MGET` de Upstash.
2. Extraer `vin_leido` desde cada JSON.
3. Revisar foto/documento original para completar `vin_correcto`.
4. Clasificar `tipo_error` con mayor precision si corresponde.
