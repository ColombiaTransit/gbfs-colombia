# Cali — BiciMIO public bicycle pilot vs. bicycle parking vs. proposed public bike system

**Research date:** 2026-11-16
**Country / timezone:** CO / `America/Bogota`
**Decision:** **No confirmed operational citywide public bike-share system or anonymous real-time data source; do not build or enable a scraper.**
**Candidate network ID:** `cali-bicicletas-publicas` (research-only; do **not** register).

## Executive finding

In Cali, “BiciMIO” has been used for **different activities that cannot be
treated as the same live GBFS network**:

1. A **real but limited 2018 pilot** lending approximately 100 public
   bicycles among the `Universidades` MIO station and four southern
   universities.
2. **BiciMIO bike parking**: MIO riders park **their own bicycles** at
   transit terminals/stations. Those parking slots do **not** represent
   publicly rentable bikes.
3. A new citywide, automatic public bicycle program proposed in
   **Calinteligente (2020–2023)** and the **2024–2027 city development
   plan**. The current program is **not confirmed operational**.

The most important modern primary-source evidence is the final audit
dated **2026-10-28** by the `Contraloría General de Santiago de Cali`.
Its **2025 performance table** reports the development-plan metric
`Sistema de Bicicletas Públicas operando` at **0 of 1, 0%**. It also
records that the original **COP 1,000,000,000** program allocation was
reduced to **0** because prerequisite stages were incomplete.

Thus: **no operational municipal system was verified for 2025, and no
2026 commissioning or public GBFS/status source was found in this
research pass.** Absence of evidence is not proof that no later
pilot or private operator exists.

## 1. The historic 2018 BiciMIO bike-loan pilot

Contemporary reporting described a free lending pilot of **100 red
bicycles** connecting `Estación Universidades` with:

- Universidad Javeriana
- Universidad ICESI
- Universidad Libre (Valle del Lili)
- Institución Universitaria Antonio José Camacho

Original contemporary news:
https://www.elpais.com.co/cali/inicia-plan-piloto-de-bicicletas-publicas-del-mio-en-el-sur-de-sepa-como-usarlas.html

A 2026 review explicitly distinguishes the historical 2018 pilot
from the currently named BiciMIO bike-parking sites:
https://caliescribe.com/2026/09/07/cali-pedalea-hacia-una-movilidad-mas-sostenible-ciclorrutas-y-bicicletas-publicas-en-la-ciudad/

Historical pilot ridership and the 100 bicycles are **not** evidence
of a public active fleet in 2026. We found no current pilot station
API, app, current opening schedule or validated per-station availability.

## 2. BiciMIO transit cycle parking is not bikeshare

**Primary operator source, Metro Cali, 2022-11-21:**
https://metrocali.gov.co/el-mio-la-mejor-opcion-como-medio-alternativo-de-transporte-en-el-dia-sin-carro-y-sin-moto/

This explicitly says people arrive with **their own bicycles**
(`sus propias bicicletas`) and use **cicloparqueaderos denominados
BiciMIO** at:

- Terminal Menga
- Terminal Paso del Comercio
- Terminal Andrés Sanín
- Terminal Calipso
- Terminal Simón Bolívar
- Terminal Cañaveralejo
- Estación Universidades

The reported **929 spaces** are **bike-parking capacity**, not
929 public bicycles available for rent.

A later 2026 account agrees that the present BiciMIO sites are mainly
intermodal bike-parking/infrastructure:
https://caliescribe.com/2026/09/07/cali-pedalea-hacia-una-movilidad-mas-sostenible-ciclorrutas-y-bicicletas-publicas-en-la-ciudad/

**Never create `station_information`, `station_status` or
`num_bikes_available` for ordinary parking facilities.**

## 3. Proposed citywide public system — not implemented in 2025

**2020–2023 Calinteligente official proposal:**
https://www.cali.gov.co/calinteligente

Advertised **550 public bicycles** and **46 modular stations**,
including standard, tandem and cargo-style bicycles, a digital
app/card interface and realtime occupancy. All figures use future
tense. They are **project goals**, not observed public bike inventory.

**2024–2027 district development-plan indicator 62010030024:**

The technical annex described:
- `Sistema de Bicicletas Públicas operando`
- baseline **0**; target **1** operating system
- initial scope of **20 stations** and about **250 bikes**
- proposed initial central-city area from Chipichape toward the
  Canchas Panamericanas

Public copy of the governmental technical annex:
https://caliescribe.com/wp-content/uploads/2024/05/Anexo-14.-Descripcion-de-los-indicadores-de-producto-CONVENCIONES.pdf

Governmental development plan PDF:
https://ogpt.valledelcauca.gov.co/storage/Clientes/ogpt/principal/imagenes/contenidos/4757-76001-plan%20de%20desarrollo%20territorial%202024%20-%202027.pdf

**Most recent decisive government oversight source:**

Contraloría General de Santiago de Cali, final audit of fiscal-year
2025 municipal sustainable mobility implementation, dated
**2026-10-28**, printed **pp. 42 and 45–46**:

https://archivos.contraloriacali.gov.co/colecciones/download/%5B%26quot%3BIF_AC_Prog_Mov_SS_vig_2025_def.pdf%26quot%3B%2C%26quot%3BIF_AC_Prog_Mov_SS_vig_2025_def%26quot%3B%2C%26quot%3Bpdf%26quot%3B%2C%26quot%3B162%26quot%3B%2C%26quot%3B6ae36de2a679a%26quot%3B%5D

Relevant audited numbers:
- `Sistema de Bicicletas Públicas operando`, 2025 goal **1**,
  achievement **0** (**0%**).
- Original 2025 budget **COP 1,000,000,000**;
  final budget **COP 0**, commitment **COP 0**.
- Audit explains the appropriation was withdrawn because
  prerequisite phases for execution were not finished.
- This audit **does not, by itself, establish 2026 current
  status**. No later commissioning was verified in this pass.
- Audit separately says **434 bicycle-parking spaces** were installed,
  not that 434 public bicycles became rentable.

An independent contemporaneous report dated 2023-11-21 also states
that an earlier planned citywide public system was abandoned for lack
of resources:
https://www.elpais.com.co/cali/calenos-se-quedaron-esperando-el-sistema-de-bicicletas-publicas-para-la-ciudad-ya-no-se-ejecutara-este-ano-2026.html
(The URL contains 2026, but the visible article publication date is
**2023-11-21**; do not treat it as a 2026 launch/update.)

## 4. Independent private operators

No verified **Cali, Colombia** citywide docked or dockless public
shared-bicycle operator with public realtime data was found in this
research pass.

**Do not falsely identify “Cali E-Bikes” as local to Cali, Colombia**:
https://play.google.com/store/apps/details?id=com.velvioo.calibike
is a generic `Velvioo LLC` application linked to the `anivride.com`
micromobility franchising platform. It lacks verified operations
within Santiago de Cali. An English/Spanish marketing description
containing the word “Cali” is not enough to establish local operation.

Tourist bicycle rentals, guided rides, bike repair shops, and
`Ciclovida` recreational events are **not necessarily GBFS
bike-share networks**. Avoid silently substituting them for
a station-based system.

## 5. GBFS feasibility assessment

| Requirement | Status |
| --- | --- |
| 2018 limited public bike-lending pilot | Historically confirmed |
| Current 2026 citywide operator | **Not verified** |
| 2025 municipal citywide system | Audited **0% operating** |
| 2026 public stations and stable station IDs | **Unknown** |
| Anonymous live per-station availability feed | **Not found** |
| Verified live bike counts and last-updated time | **Not found** |
| Valid rights/permissions to republish | **Not verified** |
| PyBikes/GBFS implementation justified now | **No** |

### Reopen research only if

1. The Secretaría de Movilidad or Metro Cali publishes a **dated 2026
   commissioning notice** for a new genuinely public bicycle-share
   program, independent of parking and the 2018 pilot.
2. An official app, portal, open-data API or GBFS feed is identified
   with per-station bike availability, station IDs and reliable
   timestamps (no account/identity scraping).
3. WGS84 coordinates, operating days and capacity can be validated.
4. Provider authorizes redistribution and MobilityData GBFS validation
   succeeds.

**Decision:** Preserve this documentation, do not write a scraper,
do not add `cali-bicicletas-publicas` to `ENABLED_NETWORKS`,
and do not schedule API polling on nonexistent endpoints.
