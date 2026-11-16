# Rueda por Cajicá — Cajicá, Cundinamarca

- **Assessed:** 2026-11-16
- **Country/timezone:** CO / America/Bogota
- **Provisional GBFS system ID:** `rueda-por-cajica` — **not enabled**
- **Operator:** Alcaldía Municipal de Cajicá, Secretaría de Tránsito, Transporte y Movilidad
- **Research verdict:** **2024 municipal audit reports public rentals were restricted to city employees and lending was suspended** pending an intergovernmental agreement; not a confirmed current public bikeshare.

## Original rollout and still-listed marketing page

- Original regional network began in 2018 with Chía and Zipaquirá:
  https://www.cundinamarca.gov.co/noticias/bicicletas%2Bpara%2Breforzar%2Bla%2Bseguridad%2Ben%2Bcundinamarca
- Historical launch press described two Cajicá locations, **Parque Principal** and **Colegio Pablo Herrera**, with 30 bikes:
  https://elperiodicodechia.com/region/cajica-de-los-primeros-municipios-de-cundinamarca-en-tener-sistema-publico-de-bicicletas/
- The municipality's 2020 page still promotes the `Rueda por Cajicá` program, application/identity verification and a promise of bicycle loans:
  https://cajica.gov.co/cajica-en-bici/
- Municipal `GTM-PR006` procedure of 2021 requires a registration form, ID copies, a contract and a pagaré:
  https://www.cajica.gov.co/docdown/archi/2021/Procedimiento/procedimiento%20prestamo%20de%20bicicletas%20.pdf

**Warning:** A marketing page and registration form that remain online in 2026 **do not demonstrate that public lending still happens**.

## Decisive municipal audit (2024)

Official **21 June 2024** final internal audit of Secretaría de Tránsito, Transporte y Movilidad, printed pp. 12–13 (PDF indexes 11–12):

https://cajica.gov.co/docdown/archi/2024/Informe/NFORME%20FINAL%20AUDITORIA%20GESTI%C3%93N%20DE%20TR%C3%81NSITO%2C%20TRANSPORTE%20Y%20MOVILIDAD.pdf

Findings:

1. Citizens declined the required pagaré, and the municipality **restricted bicycle lending to employees**; possible two-hour short loans or up to five days for employees.
2. A five-year `comodato` arrangement with the Cundinamarca government **expired 2023-11-23**.
3. The audit reported **38 bicycles** in Cajicá, kept at **Parque La Estación**; second parking location in **vereda Chuntame** was empty. These are **historical 2024 inventory and location statements**, not live rentable availability.
4. The agreement was still being renewed and the municipal auditor reported that the **bicycle-loan procedure could not be carried out at the time of the audit**.
5. The audit recommended restarting/improving the process.

This audit is **newer and more authoritative** for operating status than the 2020 website listing. As of our 2026-11-16 research, **no later reliable reopening proof is established**. Do not infer permanent termination, either.

## Technical source assessment

- The documented 2021 process used a **Google Forms registration and manual approval**, not a public realtime map.
- The original 2018 regional project had a shared administrative IT platform, but **no current anonymous status endpoint or common backend** was identified.
- Never collect Google Forms submissions, registration details, identification data or loan histories.
- The 2024 report suggests the network is not currently suitable for an open public GBFS scraper.

## Conditions for reconsideration

1. Find a **post-2024** official announcement or administrative evidence of resumed **public**, not employee-only, bike lending.
2. Confirm renewal of the departmental agreement, actual operational public stations and bike numbers.
3. Verify a safe public API or ask operator for read-only anonymized station availability, stable IDs, WGS84 coordinates, hours and fresh status data.
4. Only then implement and validate a GBFS adapter.

**Decision:** **exclude from active GBFS; low priority**, historical records preserved.
