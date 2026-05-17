# Data Model

## Resultado normalizado

```json
{
  "proveedor_layout": "DERCO",
  "data": {
    "correlativo": "",
    "tipo_guia": "GUIA DE DESPACHO ELECTRONICA",
    "numero_guia": "492060",
    "marca": "SUZUKI",
    "modelo": "SWIFT",
    "chassis_serie": "MBHZCEES9TG411604",
    "posicion_lote_codigo": "0004758665",
    "destino_empresa": "Sergio Escobar SPA",
    "destino_direccion": "Av. Américo Vespucio 1155",
    "destino_comuna": "Huechuraba",
    "origen": "Lo Boza",
    "comentarios": "",
    "tipo_factura": ""
  },
  "estado": "OK"
}
```

## Envelope Upstash

Cada guía se guarda como envelope:

```json
{
  "numero_guia": "492060",
  "storage_key": "helice:guia:numero:492060_resp",
  "duplicate": true,
  "duplicate_of": "helice:guia:numero:492060",
  "saved_at": "2026-05-17T...",
  "source": {
    "drive_file_id": "...",
    "filename": "guia_04.jpg"
  },
  "result": {}
}
```

## Bitácora

Eventos guardados en:

```txt
helice:bitacora
```

Formato:

```json
{
  "event": "guia_processed",
  "numero_guia": "492060",
  "storage_key": "helice:guia:numero:492060_resp",
  "duplicate": true,
  "estado": "OK"
}
```

## Estados válidos

```txt
OK
REVISAR
ERROR
```
