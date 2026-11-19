# MegaBici — Pereira, Risaralda, Colombia

**Research date:** 2026-11-16  
**GBFS status:** active municipal system; **no confirmed public realtime API**  
**Proposed network ID:** `megabici-pereira` (not activated)  
**Operator:** Instituto de Movilidad de Pereira / Alcaldía de Pereira  
**Country / timezone:** CO / `America/Bogota`

## Current primary source and fleet scope

Municipality's early-November 2026 announcement of the reopening:
https://www.pereira.gov.co/publicaciones/11470/pereira-reactiva-siete-estaciones-de-megabici-para-impulsar-la-movilidad-sostenible/

- Municipal operator reactivated the network following a temporary
  suspension associated with the earthquake of 2026-08-10.
- Current reopening includes **seven publicly operating stations**:
  1. Plaza de Bolívar
  2. Parque de La Libertad
  3. Parque Olaya Herrera
  4. Calle del Encuentro
  5. La 40
  6. Universidad Tecnológica de Pereira (UTP)
  7. El Lago
- **101 bicycles** initially in service at reopening, with **33 more
  planned**. These are network totals, **NOT live availability at each
  station**, and the planned bicycles must not be counted as present.
- Announced public service hours **07:00–17:00**; exact days of week
  require current operator verification (the March 2026 UTP publication
  described Monday–Friday, which predates the reopening).
- Service is **free**. Users visit a staffed location and present
  identity/registration details to the attendant. Bikes may be returned
  at a different station. **Do not collect identity data or loan records.**

Confirmed 2026-11-04 operator social post, as mirrored by a public
operator page:
https://www.govserv.org/CO/Pereira/383323465192154/Instituto-de-Movilidad-de-Pereira

Coverage of 2026-11-10 operation (seven active of nine listed stations,
report of 30 additional bicycles):
https://noticiasunoa.com/2026/11/10/megabici-fortalece-la-movilidad-sostenible-en-pereira-con-30-bicicletas-nuevas/

**Do not add the announced 33 and the reported 30 together** until the
operator confirms whether they are the same procurement batch.

## Historical network descriptions — do not mistake for current roster

UTP university news 2026-03-20 listed **nine** stations before the
temporary closure:
https://comunicaciones.utp.edu.co/105996/rectoria/ya-usas-megabici-recuerda-que-esta-disponible-en-la-utp-para-toda-la-comunidad-universitaria/

Earlier locations included Intercambiador de Cuba and Arboleda. These
are **not among the seven reopened locations** in November 2026.
Do not automatically include them in a live feed.

The university reports station staff and manual registration by ID /
phone. March 2026 operating hours were Monday–Friday 07:00–17:00,
with a one-hour loan period. Verify this schedule after the restart.

2023 municipal historic details:
https://www.pereira.gov.co/publicaciones/6252/en-2022-el-sistema-megabici-registro-mas-de-12-mil-prestamos-a-biciusuarios/

## Technical source investigation

- The November 2026 municipal notice contains the station roster, hours
  and fleet total, but **no machine-readable real-time station feed**.
- Public search for `MegaBici Pereira` Android apps, public bike availability
  dashboards, documented GBFS feeds and API endpoints yielded **no
  verified provider URL** in this research pass.
- The service uses **staffed stations and attendant-managed loans**.
  The existence of administrative loan software is not evidence that
  its contents are published anonymously or that its operational count
  can be retrieved by a public scraper.
- GPS-equipped `Mujer Segura` bikes are mentioned in recent press.
  This does **not** establish a public GPS or station availability API.
  Do not seek to redistribute individual riders' positions.
- Avoid inventing endpoint paths, per-station bicycle counts, station
  coordinates or availability timestamps.

## Feasibility

| Requirement | Status |
| --- | --- |
| Operator activity in November 2026 | **Confirmed** |
| Seven active station names | **Confirmed** |
| Coordinates and stable station IDs | To obtain/verify |
| Live available-bicycle counts per station | **Not found** |
| Public anonymous API | **Not found** |
| Permission to republish operational data | To clarify |
| Safe to activate production GBFS | **No** |

### Suggested next steps

1. Ask the Instituto de Movilidad de Pereira whether their station
   loan-management platform exposes a **public read-only aggregate
   available-bike count per station**, or can export a GBFS feed.
   Suggested contact: `contactenos@movilidadpereira.gov.co`
   (from official institutional material; verify before sending).
2. If an API is offered, record stable IDs, WGS84 coordinates,
   availability counts, valid timestamps, operational status, and
   current operating days, without collecting personal records.
3. Validate distinction between seven open stations and nine historical
   stations; confirm the 30/33 bicycle expansion counts.
4. Only then build a PyBikes-compatible scraper and validate GBFS.

**Decision:** Store as active service but not scraper-ready. Do not
activate `megabici-pereira` in the Docker deployment.

## Targeted follow-up — 2026-11-19

Following Rueda por Ibagué, existing MegaBici research was reviewed before doing any new work. A targeted search of current official Pereira/Instituto de Movilidad announcements, station maps, availability dashboards and documented API/GBFS sources **did not establish a public machine-readable station-availability endpoint**. The already-recorded 2026-11-05 reopening notice and 2026-11-10 fleet update remain the relevant current operational sources. Do not count 101 total bikes or planned 30/33 additions as live station inventories.

**Decision:** No APK acquisition, emulator, reverse engineering or speculative endpoint probing is justified: the municipal service is staffed, and no rider-facing app exposing live station counts has been verified. The actionable dependency is operator confirmation of a public read-only aggregate station feed or permission for a simple export. Keep `megabici-pereira` off production GBFS until that exists. No need to repeat the existing seven-station/fleet research.
