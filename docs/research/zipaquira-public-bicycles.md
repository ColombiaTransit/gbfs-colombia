# Zipaquirá — Sistema Público de Bicicletas

- **Assessed:** 2026-11-16
- **Country/timezone:** CO / America/Bogota
- **Provisional network ID:** `zipaquira-bicicletas-publicas` — **not enabled**
- **Historical operator:** Alcaldía de Zipaquirá and Gobernación de Cundinamarca
- **Verdict:** public system documented in **2018** with a public-tourism adaptation reported about **2020**; **2026 operations unverified** and no public realtime status/API confirmed.

## Rollout and historical stations

Primary departmental 2018 launch:
https://www.cundinamarca.gov.co/noticias/bicicletas%2Bpara%2Breforzar%2Bla%2Bseguridad%2Ben%2Bcundinamarca

Regional launch began in **Zipaquirá, Chía and Cajicá**. It was described as an interconnected regional bicycle scheme with biometric user identification and an administration platform.

Official departmental project contractor management report, **2017**, confirms procurement scope:
https://fondecun.gov.co/download/371/2017/10496/informe-de-gestion-2017.pdf
- Central administrative technology platform, public kiosks, parking stations and bicycles.
- Two stations of 15 bikes each per municipality (legacy launch configuration).
- Zipaquirá names in that report: Centro Comercial La Casona and Biblioteca Pública Regional.
- **Source discrepancy**: 2018 local launch coverage describes **La Casona and Universidad Uniminuto** instead. This is unresolved and MUST NOT be silently combined as three simultaneous stations:
  https://extrategiamedios.com/puesta-en-marcha-para-el-sistema-de-bicicletas-publicas-en-zipaquira/

A subsequent local media report around 2020 describes a tourism-oriented reorganization of the original two stations: one remained near Universidad Minuto de Dios, while the **La Casona site was moved to Estación del Tren**:
https://extrategiamedios.com/turistas-podran-utilizar-servicio-de-bicicletas-publicas-en-zipaquira/

These are **past** reported locations and not currently verified. The local report is secondary reporting of a municipal source, not an up-to-date municipal inventory.

## 2026 status

Targeted public web searches for 2024–2026 municipal operation, active bike lending, public station maps, Android apps, official GBFS and live station API produced **no verified, current public-service source** during this round. Absence of indexed evidence **does not prove closure**.

- Current 2026 live station names/IDs: **unknown**
- Bikes available by station: **unknown**
- Valid current WGS84 coordinates: **unknown**
- Operating hours: **unknown**
- Anonymous provider status API: **not found**
- Whether it still uses the 2018 regional platform: **unverified**

## GBFS steps if new evidence surfaces

1. Ask the Zipaquirá mobility authority whether the inter-municipal program still operates.
2. Confirm whether the La Casona, Uniminuto and tourist-train station accounts refer to a relocated station, rather than multiple active stations.
3. Determine if an official public read-only endpoint (GBFS or anonymous station totals) exists.
4. Verify valid current stations, timestamps, available bikes, permissions and operating hours before implementing a PyBikes scraper.
5. Avoid authentication and rider-identification/biometric data; the 2018 platform's biometric login is not a route to public data access.

**Decision:** research only; no active system or cron job.
