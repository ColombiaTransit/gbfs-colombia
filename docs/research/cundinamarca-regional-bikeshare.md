# Cundinamarca regional bikeshare: Chía, Cajicá, Zipaquirá

**Joint research:** 2026-11-16
**GBFS status:** **No operational three-city shared feed established**.

## Why these three were researched together

The Cundinamarca government launched a regional public bicycle initiative
on **2018-02-12**, initially covering **Zipaquirá, Chía and Cajicá**,
with biometric registration and intended cross-municipality use.

Departmental announcement:
https://www.cundinamarca.gov.co/noticias/bicicletas%2Bpara%2Breforzar%2Bla%2Bseguridad%2Ben%2Bcundinamarca

The 2017 FONDECUN management report identifies an integrated regional
procurement that included **one administrative technology platform**,
kiosks, bicycle parking stations and bicycles:
https://fondecun.gov.co/download/371/2017/10496/informe-de-gestion-2017.pdf

**Scope limitation:** the 2017/2018 common procurement is evidence of a
*historical shared platform*, **not** of a common technical backend,
software operator or consolidated live vehicle feed in 2026.
Do not create a combined GBFS network unless present operations
and feed data genuinely share one system ID and the operator authorizes
it. Otherwise publish separate actual systems.

## Comparison as of 2026-11-16

| Municipality | Service evidence | Public anonymous station availability | Status |
| --- | --- | --- | --- |
| Chía | **914 actual public bicycle loans in 2025** (municipal annual report published 2026); 2026 service-support contracts listed | Not found | Active in 2025, prospective provider outreach |
| Cajicá | **2024 internal audit**: loans restricted to staff, 38 bikes at Parque La Estación, Chuntame parking empty; overdue agreement renewal prevented lending | Not found | **Not confirmed publicly operational**; deprioritize |
| Zipaquirá | 2018 launch and ~2020 tourism station relocation | Not found | **2026 activity unverified**; research only |

Chía source:
https://chia-cundinamarca.gov.co/2026/PLANEACI%C3%93N/Informes%20de%20gesti%C3%B3n%2C%20evaluaci%C3%B3n%20y%20auditor%C3%ADa/Informe%20de%20gesti%C3%B3n%20vigencia%202025.pdf

Cajicá decisive 2024 audit (PDF printed pp. 12–13):
https://cajica.gov.co/docdown/archi/2024/Informe/NFORME%20FINAL%20AUDITORIA%20GESTI%C3%93N%20DE%20TR%C3%81NSITO%2C%20TRANSPORTE%20Y%20MOVILIDAD.pdf

Zipaquirá historical relocation:
https://extrategiamedios.com/turistas-podran-utilizar-servicio-de-bicicletas-publicas-en-zipaquira/

## Recommended next action

1. **Chía first**: ask Secretaría de Movilidad whether its current lending
   system can expose anonymous station counts (or official GBFS 3.0),
   valid IDs, lat/lon, status, last updated and redistribution permission;
   current portal: https://movilidad.chia-cundinamarca.gov.co/.
2. **Cajicá**: only revisit if an official post-2024 document confirms
   reopening public access; the old marketing page is not sufficient.
3. **Zipaquirá**: validate current operations and the status of the
   tourist-train relocation before any technical investigation.

### GTFS/GBFS design safeguards

- Do not confuse bicycle **parking** with bicycle **sharing**.
- Do not confuse historical total rentals with simultaneous stock.
- Do not scrape registration forms, identities, biometrics or borrowing
  history: only publicly accessible **aggregate station availability**.
- Do not invent station IDs, coordinates, currently open stations or
  vendor API domains.
- No production PyBikes adapters are enabled; no new Actions job is
  justified without a verified public data endpoint.
