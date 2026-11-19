# Urkubici — Pasto, Nariño, Colombia

**Research status:** no verified public real-time station data endpoint; **do not activate a scraper**.
**Last checked:** 2026-11-15.
**Proposed PyBikes network tag:** `urkubici-pasto` (not registered).
**Timezone:** `America/Bogota`.

## Official public and institutional sources

1. City of Pasto, 2021-10-29 opening announcement:
   https://www.pasto.gov.co/index.php/noticias-transito/14408-en-funcionamiento-sistema-de-bicicletas-compartidas-urkubici-que-constituye-a-pasto-en-territorio-lider-en-movilidad-sostenible
   - The original program comprised **8 solar-powered docking/charging
     stations and 345 bicycles**, electric and mechanical, across public
     bodies, universities, and SENA. Those are **2021 launch figures**,
     not verified live operating capacity in 2026.
   - Beneficiaries included Secretaría de Tránsito, Secretaría de Gestión
     Ambiental, Universidad de Nariño (Torobajo and Centro), Universidad
     Cooperativa, Universidad Mariana, Escuela Normal Superior and SENA.
2. City of Pasto's **official 2023 administrative handover report**,
   page 22 (physical PDF page 22, 0-based index 21):
   https://www.pasto.gov.co/index.php/documentos-de-empalme-2020-2023/984-dimension-economica?download=28267%3Aacta-de-empalme-secretaria-de-transito-y-transporte
   - Reports **8 stations and 342 bicycles** in 2023.
   - Up to December 2023, the network was operated/maintained together.
     Beginning January 2024 **each institution was to take responsibility
     for its own station**.
   - Municipal transit department STTM's share: **16 bicycles**,
     14 electric and 2 mechanical.
   - The same meeting states a separate proposed **citywide public
     bikeshare system** had not been funded. Do not conflate that
     unimplemented project with the institutional Urkubici network.
3. October 2026 municipal maintenance procurement `IP-2026-110`:
   https://www.temploapp.co/procesos/minima-cuantia-alcaldia-de-pasto/84477c6c-cb3f-4c22-a176-c76d2582a0f6
   - Calls for diagnostic, electrical and mechanical maintenance of
     **14 Urkubici bicycles and one charging/parking station**.
   - Third-party procurement service indicates award **2026-10-30**
     to M&o Distribuciones y Tecnologia S.A.S.:
     https://www.lidecol.com/licitacion/contratista-compromete-municipio-pasto-realizar-acciones-diagnostico-11061901
   - **Procurement does not prove restoration, daily availability or
     continued operation at the other institutions.**
4. Background manual on the original Urkubici program:
   https://proyectoceela.com/wp-content/uploads/2024/12/Manual-Proyecto-Urkubici.pdf

## Software supplier and public apps

Original applications are published by **Bicico**, associated with
**Bicycle Capital / Neardental S.A.S.** Many apps are institution-specific:

| Institution | Android application ID | Public link |
| --- | --- | --- |
| Secretaría de Tránsito | `com.urkubici.app` | https://play.google.com/store/apps/details?id=com.urkubici.app |
| Secretaría de Gestión Ambiental | `com.urkubici.sambiente` | https://play.google.com/store/apps/details?id=com.urkubici.sambiente |
| Universidad de Nariño | `com.urkubici.udenar` | https://play.google.com/store/apps/details?id=com.urkubici.udenar |
| Universidad Cooperativa | `com.urkubici.cooperativa` | https://play.google.com/store/apps/details?id=com.urkubici.cooperativa |
| SENA | `com.urkubici.sena` | https://play.google.com/store/apps/details?id=com.urkubici.sena |

Further institution-specific apps appear in the publisher catalogue,
including **Universidad Mariana** and **Escuela Normal Superior**;
confirm exact Play package IDs before relying on them.

The legacy Urkubici apps' Google Play listings were last updated
**2023-09-08** for sampled apps, and describe a bicycle-sharing
service for each *institution*. These are **not evidence** of a
public no-login API or live status in 2026.

The supplier currently advertises customizable apps and private
dashboards for enterprise/campus shared fleets:

- https://bicyclecapital.co/
- https://bicyclecapital.co/vehiculos-de-uso-compartido/
- Public app from the same supplier, **BC Ride**:
  https://play.google.com/store/apps/details?id=com.bicyclecapital
  Updated **2026-08-11** according to current Play index.
  It advertises real-time locations of stations and racks; however
  there is **no demonstrated link that Urkubici has migrated to it**.
  Do not assume the same backend or copy BC Ride availability
  into an Urkubici feed.
- Public supplier support contact on Urkubici apps:
  `servicio@bicyclecapital.co`.

**Public web/API discovery result as of this review:** the supplier's
public site is a marketing website with platform descriptions and a
contact form. We did not identify an anonymous Urkubici station-status
dashboard, GBFS discovery URL, documented station API or JSON endpoint.
No APK was downloaded or reverse-engineered. No authentication,
institutional identity records or rider histories were accessed.

## GBFS implications and data-model decisions

1. **Do not publish historical fleet totals as live availability.** 345
   at launch, 342 in 2023, municipal 16 in 2024 and 14 bicycles mentioned
   for 2026 maintenance are different scopes/points in time.
2. **Federated operation:** since 2024 institutions have been
   independently responsible for individual stations. Determine whether
   the platform still operates as one logical network or whether
   independent institutions need separate GBFS `system_id` datasets.
   Don't combine unrelated inventories or duplicate bikes.
3. **Accessibility:** this was an institutional-access program, not
   necessarily freely rentable by anyone citywide. Verify station
   eligibility rules before advertising as a general-public system.
4. **Software:** Bicico's current configurable platform may contain
   per-station bike counts, but the public site alone provides no
   reusable anonymous data feed. Ask provider for an official read-only
   station/availability endpoint or GBFS export.
5. **No static workaround:** publication of stations without live
   availability is not a complete GBFS 3.0 operational feed. Never
   assign zero bikes simply because the live source is unavailable.

## Targeted next checks (without APK analysis)

- Ask **Bicycle Capital** whether the original Urkubici tenants still
  run on the 2026 platform and whether a public/read-only GBFS or
  station-status export is available.
- Confirm current maintenance and operation per institution, starting
  with the **STTM's 14-bike maintenance contract**.
- Obtain station IDs, WGS84 coordinates, daily hours, current number of
  rentable bicycles per dock/station, vehicle classes, timestamps and
  redistribution permission.
- Only if a public anonymous data source is available, implement
  a PyBikes adapter under `colombia_gbfs/scrapers/`, test
  the provider mapping and validate generated GBFS using MobilityData.

**Decision:** No active scraper, no container build and no periodic
research Action are justified yet. Retain for future provider/API
follow-up.


## Four user-provided Android APKs — static comparison, 2026-11-19

Four uploaded APKs were inspected locally as ZIP/DEX files. **No installation, emulator, authentication or personal data collection was required.** Their Java/Dalvik implementations share a common API path pattern, but the domain is separately configured for each institution.

| APK variant | File version | Production base/host found as a DEX string | Station endpoint (embedded literal) |
| --- | --- | --- | --- |
| Secretaría de Gestión Ambiental | 1.3 | `https://www.sambienteurkubici.com` | `https://www.sambienteurkubici.com/api/stations` |
| Secretaría de Tránsito | 1.11 | `https://stransitourkubici.co` | `https://stransitourkubici.co/api/stations` |
| Universidad Cooperativa de Colombia (UCC Pasto) | 1.4 | `https://www.ucooperativaurkubici.com` | `https://www.ucooperativaurkubici.com/api/stations` |
| Universidad Mariana | 1.2 | `https://www.marianaurkubici.com` | `https://www.marianaurkubici.com/api/stations` |

Other common paths confirmed in all four DEX builds: `/api/login`, `/api/register`, `/api/rides`, `/api/profile`, `/api/profile/update`, `/api/report`, `/api/openLock`; a `NearbyStationsFragment`, `Station` model, and `URL_STATIONS` identifier are present. A legacy `http://bogotabikesharing.co/api/openLock` string is also shared, but is **not evidence of the current station data host**. User-specific operations (profile, rides, unlock) are out of scope for anonymous GBFS.

APK SHA-256:
- Gestión Ambiental 1.3: `a750e567a35fa5eb69781c42937ee8c06c1e95da6dea3fb569ac1217a61439a5`
- Tránsito 1.11: `4f26ecee80534d682b5afa4febf1160d04c3a21d05b913c48e4235a757f471e6`
- UCC 1.4: `5e2fe564e2bdd52afeb576a99c1c594a6cb56e8c49701e76ebc866560a4c11ff`
- Mariana 1.2: `e529d1cb6414b3290f33d62a933394abbb509c33d9ac393838d3a2ad4ba28baa`

A public web retrieval attempt for the four `/api/stations` URLs could **not** retrieve a usable response. No HTTP status code, JSON station response, current inventory or anonymous-access status was verified. **Do not report an HTTP 200/401 or working GBFS source** until a real HTTP test succeeds.

**Next bounded action:** check HTTP GET status and (only on HTTP 200) the non-personal station JSON structure for these four endpoints. One reusable adapter can then cover the four tenants with separately configured hosts **if** the public response schema matches and is appropriate for redistribution. Avoid another APK download or an emulator for this step. The apps' presence is not proof that these institutional fleets remain active in November 2026.


## User-run API DNS tests — 2026-11-19

The user tested the four APK-derived HTTPS station endpoints from Windows PowerShell. **All four failed DNS resolution (host unknown), before any HTTP response could be received**:

| Endpoint | User-observed result |
| --- | --- |
| `https://www.sambienteurkubici.com/api/stations` | Host unknown |
| `https://stransitourkubici.co/api/stations` | Host unknown |
| `https://www.ucooperativaurkubici.com/api/stations` | Host unknown |
| `https://www.marianaurkubici.com/api/stations` | Host unknown |

These are DNS failures, **not HTTP 401, HTTP 404 or empty JSON**. They do not independently prove that all institutional bicycle programs are discontinued. All four APK-configured hosts may be obsolete, migrated or temporarily unavailable; no working replacement hostname is confirmed.

**Decision:** pause further probes and APK work for these four legacy tenants. Do not create/enable a GBFS adapter or publish synthetic station availability. Revisit only when Bicycle Capital / a participating institution supplies a current, resolvable, publicly readable station-data endpoint or other contemporary evidence of an active backend. Retain APK hostnames as historical technical evidence, not operational source URLs.
