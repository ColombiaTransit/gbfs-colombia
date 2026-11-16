# Sincelejo se mueve en bici — Sincelejo, Sucre, Colombia

**Status (2026-11-16):** historically confirmed municipal public bicycle lending; operational status and live data in 2026 still require verification.
**Candidate network ID:** `sincelejo-se-mueve-en-bici` (not enabled).
**Operator:** Alcaldía de Sincelejo / Secretaría de Movilidad.
**Time zone:** America/Bogota.

## Primary sources

- Official 2019 municipal announcement:
  https://www.alcaldiadesincelejo.gov.co/NuestraAlcaldia/SaladePrensa/Paginas/SINCELEJO-CUENTA-CON-TRES-NUEVOS-PUNTOS-DE-BICICLETAS-P%C3%9ABLICAS.aspx
  - Eight stations, 210 bicycles at that time; two-hour loans; identification required.
  - These are 2019 totals, not 2026 availability.
- Municipal development plan **Acuerdo 346 of 2024**, page printed **328**,
  under “Infraestructura para bicicletas”:
  https://www.alcaldiadesincelejo.gov.co/Transparencia/Normatividad/ACUERDO%20No%20346%20DE%202024.pdf
  - States **269 public bicycles** and **8 station locations** at planning-baseline time:
    1. Alcaldía Municipal
    2. Plaza Cultural de Majagual
    3. Plaza Olaya Herrera
    4. CECAR
    5. Universidad de Sucre
    6. Barrio El Cortijo
    7. Urbanización Altos de la Sabana
    8. Corregimiento Las Huertas
  - **Note discrepancy**: older 2021 city report listed *Vereda Barro Prieto* instead of *Corregimiento Las Huertas* for the eighth location:
    https://www.alcaldiadesincelejo.gov.co/Conectividad/RendiciondeCuentas/INFORME%20DE%20RENDICI%C3%93N%20DE%20CUENTAS%20A%20LA%20COMUNIDAD%202021.pdf
    Do not merge these as a ninth active station without newer evidence.
- 2024-11-20 municipal mobility report:
  https://www.alcaldiadesincelejo.gov.co/NuestraAlcaldia/SaladePrensa/Paginas/SECRETAR%C3%8DA-DE-MOVILIDAD-PRESENT%C3%93-INFORME-AL-CONCEJO-DE-SINCELEJO.aspx
  - Mentions loaning public bicycles to rural schools under comodato.
  - This may affect network inventory. No exact realtime station counts.
- 2015 official origin/history:
  https://mintransporte.gov.co/publicaciones/4446/sincelejo-empieza-a-pedalear-con-100-bicis-entregadas-por-mintransporte/
  - Manual loans against identity check/forms; not evidence of a live digital API.

## Public data discovery

- Current website or mobile app displaying station-by-station available
  bicycles: **not verified**.
- Public JSON or GBFS API: **not found**.
- Historical process: manual lending points, forms and identity checking,
  which can still involve internal inventory software but does not
  imply public realtime data.
- No scraper should access users' identity documents, loans or accounts.

## GBFS assessment

- Network names and a 2024 list of eight locations are known, but
  stable station IDs, current coordinates, operational status,
  bike availability and timestamps are **unknown**.
- The 269 bicycles are a **2024 planning baseline** only. Do not publish
  as live count in 2026.
- A public GBFS feed requires accessible, redistributable per-station
  available bike counts; otherwise pursue a voluntary official export.
- Verify current operating sites, including the 2021 vs 2024 rural
  eighth-site discrepancy, before static station metadata is built.

**Decision:** Research register only; **not scraper-ready**.
