# Valledupar Va en Bici — Valledupar, Cesar, Colombia

**Research date:** 2026-11-16
**Status:** historical operating public bicycle-loan program (2017–2019; reactivated 2023); **2026 operating status and a public real-time availability feed are not verified**.
**Prospective network ID:** `valledupar-va-en-bici` (research only, not enabled).
**Operator:** Alcaldía de Valledupar, Secretaría de Tránsito y Transporte.
**Country / timezone:** CO / America/Bogota.

## Primary operational evidence and dates

- **November 2023 reopening** (Radio Nacional de Colombia, November 15, 2023):
  https://www.radionacional.co/actualidad/salud/valledupar-reactiva-programa-de-bicicletas-publicas-como-participar
  - Two reactivated staffed lending locations; registration required.
  - Described weekday hours: Monday–Friday 07:30–18:30. **Historical hours**, not verified for 2026.
  - The municipality advertised the registration platform `www.valleduparvaenbici.com`.
- **November 26, 2023** public operating snapshot:
  https://www.elpaisvallenato.com/2023/11/26/cuarenta-bicicletas-naranjas-estan-dispuestas-en-dos-estaciones-en-valledupar/
  - **40 publicly available bicycles** at **two stations**:
    **SENA campus** and **Plaza Alfonso López**.
  - A **further 94 bikes** were announced for a second phase
    (134 planned total); **no evidence that those 94 were deployed**.
  - Free loan, preregistration and identity/health paperwork;
    software used to manage loan durations. Do not access any user records.
- **October 2023 restart announcement**:
  https://www.maravillastereo.com/reactivaran-el-programa-valledupar-va-en-bici/
  - Highlights a website for user registration and a software component
    for loan-time administration; **does not claim a public
    anonymous available-bicycle feed**.
- **Earlier distinct network (2019)**:
  https://interpolitico.com/inicio/bicicletas-publicas-empiezan-a-rodar-en-valledupar-desde-ocho-biciestaciones/
  - Eight historical lending locations:
    Plaza Alfonso López, Parque El Viajero, Biblioteca Rafael Carrillo Lúquez,
    Universidad Popular del Cesar (Sabanas), SENA, Galería Popular,
    Fundación Universitaria del Área Andina and terminal de transporte.
  - This was an older arrangement, **not the verified 2023/2026 roster**.
- **2026-08-20 works / expansion article**:
  https://revistaelcongreso.com/valledupar-a-la-vanguardia-de-las-obras/
  - Mentions existing `bici-estaciones` and an intention to have five more
    by year end. This does **not** confirm an active rental service,
    actual station status, live inventory, or deployment of the proposed
    five locations.
- **2024–2027 municipal development plan**:
  https://funcionarios.ccvalledupar.org.co/timeit/DocumentosPagina/9162Plan%20de%20desarrollo%20Valledupar%202024-2027_compressed.pdf
  - Lists implementation of a public bike system as a planning KPI.
    **Targets / progress metrics are not operational realtime records.**

## Website and technology leads

- `https://www.valleduparvaenbici.com/` — registration domain cited
  in November 2023 announcements. Our public web fetch on 2026-11-16
  returned an access error; status from users inside Colombia is unknown.
- Historic different spelling:
  `www.valleduparavanzaenbici.com` (2019),
  `www.valleduparavanzaenbici.com.co` (2018).
  These were registration sites in the historic program. Current
  domains/hosts and the link between generations are not verified.
- No confirmed live public map with station-level bike inventory;
  no verified public API, current JS app, GBFS endpoint, or Android app
  surfaced during this research round.
- Registration and loan-management software may exist without
  publishing anonymous aggregate availability.
- Do not attempt registration form scraping, login bypass, harvesting
  identification documents, user information or private loan histories.

## Explicitly unrelated 2026 bicycle procurement

**2026-07-01 procurement** (contract ID CMC-046-SGR-2026):
https://colombialicita.com/licitacion/306338019

Its actual purpose was **purchasing bicycles and personal protective
equipment for operational support to security agencies**. It is
**not evidence of public bikeshare expansion or continued operations**;
do not add any bicycles from this tender to the sharing network.

## GBFS feasibility and next step

| Criterion | Evidence |
| --- | --- |
| Historic public bike-share service | Yes (2017–2019 and 2023 reactivation) |
| Two 2023 lending locations | Confirmed historically |
| 2026 public operation | Not independently confirmed |
| Current station list, coordinates and stable IDs | Not established |
| Live public bike availability API | Not found |
| Official redistribution permission | Not established |
| Production scraper | **Not justified yet** |

A staff-operated bike-lending system could still support GBFS if the
operator voluntarily exposes anonymized station-level bike counts
with meaningful freshness timestamps. Suggested targeted follow-up:

1. Ask Secretaría de Tránsito Valledupar if the 2023 two-station
   operation remains in use in 2026, and whether the website was
   replaced/moved.
2. Ask for a publicly redistributable read-only station availability
   feed/official GBFS (not rider registrations).
3. Resolve whether the 2026 bike-station works are racks/parking,
   loan kiosks, or operational bikeshare stations.
4. Add an adapter to `colombia_gbfs/scrapers` **only when** an
   accessible current source with station IDs, locations, counts,
   status and timestamps has been confirmed. Validate through
   MobilityData before activation.

**Decision:** research archive only; keep Valledupar out of
`ENABLED_NETWORKS` and do not create periodic API Actions for
unverified endpoints.
