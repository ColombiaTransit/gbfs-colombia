# BiciCeja — La Ceja, Antioquia

**Reviewed:** 2026-11-20  
**Research status:** strong evidence of 2026 municipal operation; no confirmed public station-status API.  
**Provisional GBFS system ID:** `biciceja-la-ceja` (research only, disabled)  
**Operator:** Municipio de La Ceja del Tambo / Secretaría de Movilidad.  
**Country/time zone:** CO / America/Bogota.

## Sources and confidence

- Current municipality mobility website includes the specific entry **“¡Súbete a BiciCeja!”** and an **“Iniciar registro”** call-to-action:
  https://www.movilidadlaceja.com.co/
  A registration page is *not* a station-availability API.
- Municipality contract dated **2026-09-23** for operational support and promotion of the public BiciCeja system:
  https://colombialicita.com/licitacion/312305209
- Public contractor record shows facilitator duties **2026-08-01 through 2026-12-31**:
  https://www.funcionpublica.gov.co/dafpIndexerBHV/hvSigep/detallarHV/S5142662-0682-5
- 2022 launch documented two stations near the transport terminal and Iglesia de la Santa Cruz, with expansion discussed but not verified:
  https://entrecejayceja.co/la-ceja/biciceja-se-inauguro-el-sistema-publico-de-bicicletas-de-la-ceja/
  These are **historical**, not a 2026 validated station roster.

## Technical investigation begun

- Public homepage was found and inspected through indexed content, but readable web retrieval of its HTML did not expose an anonymous station map, JSON endpoint or station bike counts.
- The portal also offers unrelated citizen/vehicle services. Do **not** treat its vehicle or identification-number functions as bicycle station endpoints; do not test private registration, profile or personal data APIs.
- User registration and facilitator-supported issue/return suggest station management may be private or manual; this is a hypothesis, **not a finding**.
- No verified station_id, station_status, station_information, or GBFS feed URL yet.

## Next steps

1. Inspect **public** BiciCeja-specific links/assets on the mobility website and look for a non-authenticated aggregate stations view.
2. Confirm live station locations, bike inventory/status and what attendants use to record a rental; ignore unrelated motoring services.
3. Ask Secretaría de Movilidad for public read-only station status or official GBFS, stable IDs, lat/lon, `last_updated`, operating hours and redistribution permission.
4. Once source quality is verified, create an adapter with offline tests and run GBFS 3.0 validation.

**Decision:** High-priority follow-up; **do not publish** unverified historical station counts.
