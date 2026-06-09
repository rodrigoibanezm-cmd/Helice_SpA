# Auditoria VIN - resumen operativo

Este documento deja el contexto de la auditoria manual de guias de Helice SpA.

## Resultado

- 37 errores de chasis / VIN confirmados.
- 1 imagen no procesable.
- 38 casos problematicos totales.

La imagen no procesable es un caso distinto: no es chasis malo; es una foto que debe tomarse otra vez.

## Diagnostico

El problema no fue solo OCR. Fue una mezcla de:

- compresion agresiva de imagen desde Lovable;
- falta de reglas duras para validar VIN;
- modelo marcando OK aunque el VIN estuviera mal;
- Upstash poco util para auditoria y busqueda;
- falta de Neon como fuente operativa auditable.

## Errores visuales repetidos

- B / 8
- S / 5
- T / 7
- O / 0
- C / 0
- J / I / U
- LL / L1
- omision de letras
- insercion de caracteres
- transposicion de caracteres

Dato clave: varios VIN malos tenian 17 caracteres. Validar solo largo no basta.

## Guias con error VIN confirmado

121556
121767
122406
173544
173810
173842
173840
494287
494332
494531
494492
494550
495089
495322
59515
59546
59630
59632
603622
59710
59725
59674
603623
603862
604011
604028
604029
604034
604035
604057
604113
604228
604391
604401
604400
604800
604542

## Imagen no procesable

495320

Mensaje esperado al usuario:

Tomar otra vez la foto. Imagen no procesada.

## Estructura de keys Upstash

Patron:

helice:guia:numero:<numero_guia>

Ejemplo:

helice:guia:numero:604542

Campos importantes del JSON:

- numero_guia
- storage_key
- duplicate
- duplicate_of
- saved_at
- source
- result

La foto se recupera desde:

source.blob.url

Los datos extraidos estan en:

result.data

Campos criticos:

- result.data.numero_guia
- result.data.marca
- result.data.modelo
- result.data.chassis_serie
- result.data.posicion_lote_codigo
- result.estado
- result.campos_dudosos
- result.observaciones
- result.ai_audit.reviewApplied

## Como rescatar fotos

1. Hacer GET o MGET de la key en Upstash.
2. Abrir el JSON.
3. Buscar source.blob.url.
4. Abrir esa URL en navegador.

## Keys para recuperar guias con problema

MGET helice:guia:numero:121556 helice:guia:numero:121767 helice:guia:numero:122406 helice:guia:numero:173544 helice:guia:numero:173810 helice:guia:numero:173842 helice:guia:numero:173840 helice:guia:numero:494287 helice:guia:numero:494332 helice:guia:numero:494531 helice:guia:numero:494492 helice:guia:numero:494550 helice:guia:numero:495089 helice:guia:numero:495322 helice:guia:numero:59515 helice:guia:numero:59546 helice:guia:numero:59630 helice:guia:numero:59632 helice:guia:numero:603622 helice:guia:numero:59710 helice:guia:numero:59725 helice:guia:numero:59674 helice:guia:numero:603623 helice:guia:numero:603862 helice:guia:numero:604011 helice:guia:numero:604028 helice:guia:numero:604029 helice:guia:numero:604034 helice:guia:numero:604035 helice:guia:numero:604057 helice:guia:numero:604113 helice:guia:numero:604228 helice:guia:numero:604391 helice:guia:numero:604401 helice:guia:numero:604400 helice:guia:numero:604800 helice:guia:numero:604542

Imagen no procesable:

GET helice:guia:numero:495320
