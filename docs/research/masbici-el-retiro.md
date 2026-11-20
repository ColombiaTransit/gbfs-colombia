# MásBici — El Retiro, Antioquia

**Reviewed:** 2026-11-20  
**Research status:** ongoing public-program funding indicated by 2026 procurement; no verified public station availability API.  
**Provisional GBFS ID:** `masbici-el-retiro` (research only, disabled)  
**Operator/program owner:** Municipio de El Retiro / IMDER; funding cooperation with Corporación Correcaminos.  
**Country/time zone:** CO / America/Bogota.

## Evidence

- The system's 2022 introduction was reported as a public bike-sharing network:
  https://vivirenelpoblado.com/masbici-sistema-de-bicicletas-publicas-de-el-retiro/
- IMDER's 2025 funding/support contract for implementation of the MásBici program:
  https://ganacontratos.com/co/entidades/811007361
- A 2026 contract record for operating/promoting the MásBici program in El Retiro identifies an implementation period **2026-01-30 to 2026-12-31**:
  https://colfirma.com/empresa/corporacion-correcaminos-830505764
  Procurement/financial support does not alone establish that all public bicycle stations are currently issuing bikes.

## Technical assessment

- Searches did not establish a public mobile app, bike-status station map or anonymous GBFS/JSON API.
- Operator roles might involve manual collection and lending; not established.
- Do not substitute bike-to-school, bike club, sporting events, or cycling infrastructure for short-trip public bike rental inventory.

## Next actions

1. Ask IMDER/Corporación Correcaminos for current physical station list, service model and digital system.
2. Search public operator maps/apps for stable station IDs, coordinates, live availability and timestamps.
3. If manual operation, request aggregate read-only data feed rather than scraping account systems.
4. Implement GBFS only on confirmed station-level data with lawful redistribution.

**Decision:** Medium-priority exploration; **no active feed**.
