# BICIPP — Popayán, Cauca, Colombia

Status: **research only — not ready for a public GBFS scraper**
Reviewed: 2026-11-15
Proposed feed ID: `bicipp-popayan` (not registered or enabled)
Operator: Alcaldía de Popayán / Secretaría de Tránsito y Transporte
Country: CO
Timezone: America/Bogota

## Confirmed municipal sources

1. **2026 procurement notice**, process `MP-ST-MC-011-2026`, published
   2026-11-12, submissions scheduled to close 2026-11-18:
   https://www.temploapp.co/procesos/el-contratista-se-compromete-a-transferir-a-titulo-de-compraventa-la-entrega/da5bb8d2-04e3-48af-9d46-c3c0277a97c4

2. **Primary municipal procurement supporting study**, November 2026:
   https://community.secop.gov.co/Public/Archive/RetrieveFile/Index?DocUniqueIdentifier=&DocumentId=890445365&InCommunity=False&InPaymentGateway=False

3. **Primary procurement technical specifications**:
   https://community.secop.gov.co/Public/Archive/RetrieveFile/Index?DocUniqueIdentifier=&DocumentId=890445366&InCommunity=False&InPaymentGateway=False

4. **2017 municipality launch press release**:
   https://www.popayan.gov.co/Comunicaciones/Boletines%20de%20Prensa/Comunicado%20331%20Febrero%202017.pdf

5. **2026 project study referring to three station restorations**:
   https://community.secop.gov.co/Public/Archive/RetrieveFile/Index?DocUniqueIdentifier=&DocumentId=890445360&InCommunity=False&InPaymentGateway=False

## Verified facts

- Municipality received **50 bicycles in 2016** and **40 additional bicycles
  in 2020**. The 2026 procurement study reports **89 bicycles** remaining
  following the theft of one bicycle in 2023.
- Historically, BICIPP opened in 2017 with **two stations**:
  `Estación Banco de la República` and `Estación Parque Informático`.
  These are historical stations, **not a verified complete 2026 roster**.
- The 2026 restoration program proposes work on **three bike stations**
  and 89 bicycles. The third site is not identified in the reviewed sources.
  Do not infer that all three stations are already operational.
- The 2026 procurement study reports **861 active registered accounts**
  out of 1,400 registered. These are account counts, **not concurrent users,
  available bicycles, or a real-time feed**.
- Municipality states that legacy bicycle GPS tracking hardware is worn or
  obsolete. A new procurement for **89 GPS devices**, 4G connectivity,
  integration with BICIPP software and a GPS monitoring web/mobile app was
  published on 2026-11-12. **Contract publication does not mean deployment**.
- Technical specification requires a GPS monitoring solution accessible to
  the municipality, with bicycle IDs and QR codes. This is not evidence that
  geolocation or bicycle availability will be publicly released.
- There is a historical registration portal URL
  `http://bicipp.arcossoft.com` / `https://bicipp.arcossoft.com`
  cited in 2017 municipal press releases. It was not accessible using
  our web retrieval on 2026-11-15; current ownership, URL and operation
  must be reverified. The old portal collected identification documents:
  **do not access private user accounts, registrations or ride histories**.
- The project `Universicleta` at Universidad del Cauca also involved
  ArcosSoft historically, but must **not** be merged with municipal BICIPP
  unless an operator confirms common technical and operational scope:
  https://portal.unicauca.edu.co/versionP/noticias/proyecci%C3%B3n-social/unicauca-implementa-el-servicio-de-universicleta

## GBFS feasibility assessment

| Item | Status |
| --- | --- |
| Station model | Historical municipal records only |
| Current station IDs / coordinates | Not verified |
| Available bikes by station | No public source found |
| Public live station/API endpoint | Not found |
| New GPS system | Procurement in progress |
| Reuse as scraper now | **Not recommended** |

The 2026 technical procurement is promising as a **future research
trigger**, but GPS telemetry is not required to implement a
station-based GBFS feed and would include sensitive live asset locations
unless published legitimately. Favor anonymous per-station available
bike counts, if the operator provides them. Never expose live individual
bike location or personal user information merely because tracking
technology exists.

## Follow-up conditions

1. Check whether process `MP-ST-MC-011-2026` has been awarded and completed
   after 2026-11-18; do not assume success or public availability.
2. Identify the resulting software provider and the current official
   public-facing BICIPP site or app.
3. Check for a lawful, anonymous station API, stable station IDs, valid
   WGS84 coordinates, available bike counts, freshness and operating hours.
4. Verify operation and metadata of the third proposed station.
5. Seek redistribution permission if provider terms are unclear.
6. Only implement a PyBikes-compatible adapter in
   `colombia_gbfs/scrapers/` once a verified public data feed exists.

**Decision:** Do not activate `bicipp-popayan` in
`ENABLED_NETWORKS`. Revisit when the GPS/software procurement has
actually produced a public service, or when a different public source
is confirmed.
