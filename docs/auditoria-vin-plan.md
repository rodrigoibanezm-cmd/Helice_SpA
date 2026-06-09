# Auditoria VIN - plan de correccion

Este documento define QUE debe cambiar despues de la auditoria manual.

No define implementacion detallada. Define objetivos y decisiones.

## Decision principal

Neon pasa a ser la fuente operativa.

Upstash queda como historico temporal.

## Nuevo proceso

Foto
-> extraccion principal
-> validacion VIN
-> verificacion automatica si hay riesgo
-> Neon
-> Sheets

## Reglas duras VIN

- VIN obligatorio.
- VIN debe tener 17 caracteres.
- VIN no puede contener I, O, Q.
- VIN debe normalizarse a mayusculas.
- Eliminar espacios y simbolos.
- Si extractor y verificador discrepan, no puede quedar OK.
- Si no se puede leer el VIN, no procesar.

## Estados

- OK
- PROBLEMA_VIN
- IMAGEN_NO_PROCESADA
- DUPLICADO
- REQUIERE_REVISION

## Neon

Tabla principal sugerida:

guides

Campos:

- id
- numero_guia
- source_blob_url
- proveedor_layout
- marca
- modelo
- vin_extractor
- vin_verifier
- vin_final
- estado
- issue_type
- confidence
- raw_json
- created_at

Tabla de problemas:

guide_audit_issues

Campos:

- id
- numero_guia
- issue_type
- vin_extractor
- vin_verifier
- vin_correcto
- descripcion
- source_blob_url
- confirmed_at

## Google Sheets

Crear pestañas separadas:

- Guias OK
- Guias con problema
- Imagen no procesada

La pestaña de problemas debe contener solo problemas reales de validacion.

La foto mala debe quedar aparte.

## Front Lovable

Decision: traer el front al repo.

Motivos:

- controlar compresion;
- controlar payload;
- controlar calidad de imagen;
- controlar estados;
- evitar dependencias externas.

Ubicacion sugerida:

frontend/

## Problema detectado

La camara capturaba una imagen mejor que la imagen finalmente procesada.

Lovable estaba reduciendo calidad y resolucion para evitar errores 413.

Eso probablemente contribuyo a errores finos de VIN.

## Nueva regla de imagen

No procesar imagen degradada.

Procesar imagen con calidad suficiente.

Guardar una copia comprimida para auditoria.

## Error 413

Evitar enviar imagen pesada al backend.

Flujo objetivo:

Front -> Blob
Backend recibe blob_url
Backend procesa desde Blob
Backend guarda en Neon

## Mensaje obligatorio para foto mala

Tomar otra vez la foto. Imagen no procesada.

## Objetivo final

Ninguna guia con VIN incorrecto debe quedar marcada como OK.
