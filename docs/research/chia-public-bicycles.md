# Chía — Sistema Público de Bicicletas

- **Assessed:** 2026-11-16
- **Country/timezone:** CO / America/Bogota
- **Provisional GBFS system ID:** `chia-bicicletas-publicas` — **not enabled**
- **Owner/operator:** Alcaldía Municipal de Chía, Secretaría de Movilidad
- **Research verdict:** Public bicycle loans **confirmed during 2025**; 2026 support contracts listed; **no verified publicly accessible realtime station availability endpoint**.

## Strongest current evidence

The official municipality **2025 annual management report**, published 2026, states that the Sistema Público de Bicicletas operated during 2025 and registered **914 bicycle loans**. It separately reports use of public bicycle parking and the children's traffic-training park. **Do not confuse bicycle-parking visits with rented bikes.**

https://chia-cundinamarca.gov.co/2026/PLANEACI%C3%93N/Informes%20de%20gesti%C3%B3n%2C%20evaluaci%C3%B3n%20y%20auditor%C3%ADa/Informe%20de%20gesti%C3%B3n%20vigencia%202025.pdf

The municipality's public contracting list for **2026** contains multiple support-services contracts (`CPS-233-2026` to `CPS-240-2026`, with relevant entries) for executing and operating the municipal public bicycle/intermodal system. This supports ongoing institutional commitment but **is not a station-level live inventory or proof of exactly how many stations operate today**:

https://chia-cundinamarca.gov.co/web/contratacion/

Official 2025-09-12 municipal article also describes a free bicycle lending service, alongside free bicycle parking, bicycle instruction and policy initiatives. Keep the three services separate:

https://chia-cundinamarca.gov.co/web/2025/09/chia-fortalece-su-liderazgo-en-la-sabana-como-referente-regional-de-movilidad-sostenible/

## Historical stations — do not publish without 2026 verification

- 2023 municipal management report: **Parque Santander** and **Parque El Paraíso**, with trial service at Tíquiza reportedly unsuccessful:
  https://chia-cundinamarca.gov.co/2024/planeacion/Informe%20de%20Gesti%C3%B3n%20vigencia%202023.pdf
- 2024 management report describes **reactivation in October 2024**, locating bicycle lending at **Biblioteca Hoqabigá** and **Parque Paraíso**; the original descriptive wording includes calle 29 / calle 1B and Mercedes de Calahorra; interpret exact coordinates only with primary location verification:
  https://www.chia-cundinamarca.gov.co/2025/Planeacion%201/InfoGesti%C3%B3n2024.pdf
- The 2018 regional rollout used **Biblioteca Municipal** and **Centro Comercial Yumbo**, but both are *legacy stations* and not a 2026 roster:
  https://fondecun.gov.co/download/371/2017/10496/informe-de-gestion-2017.pdf

## Public web and software feasibility

- Current mobility website: https://movilidad.chia-cundinamarca.gov.co/
  Lists `Sistema público de bicicletas` as a service and has a citizen-contact address `contactenos@chia.gov.co`.
- The site's public HTML contains no confirmed live station status API or bike count service. No authenticated material was accessed.
- In 2017–2018, Chía was part of a regional implementation with **Cajicá and Zipaquirá**, including one procurement scope for an administrative IT platform, kiosks, stations and bicycles:
  https://www.cundinamarca.gov.co/noticias/bicicletas%2Bpara%2Breforzar%2Bla%2Bseguridad%2Ben%2Bcundinamarca
- The shared **2018** platform is historical. It is not evidence that Chía, Cajicá and Zipaquirá currently share any common operator, backend or API. Do not invent its domain, vendor name, station IDs or endpoint.

## Open gaps and acceptance

- Validate the actual 2026 station roster and WGS84 coordinates.
- Determine whether lending is administered only by attendants in spreadsheets/municipal records or by a computer platform with public aggregate availability.
- Request an anonymous read-only public station feed, bike counts, last-updated timestamp and redistribution permission from the Chía mobility department.
- If confirmed and compliant, create a tested PyBikes adapter with individual-station availability, run MobilityData GBFS validator, then optionally enable it. **Do not publish 914 historical loans as live bikes.**
- No active network ID, cron, scraper or Docker change at this point.

**Priority:** highest of the three municipalities for operator outreach and potential data partnership; **not yet technically scrape-ready**.
