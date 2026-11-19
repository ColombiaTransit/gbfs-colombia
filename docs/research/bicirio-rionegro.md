# BiciRio (Rionegro) — GBFS source investigation

**State:** Research verified, public station API found; **do not enable live GBFS yet**  
**Observed:** 2026-11-15 (Sunday), GitHub Actions runner  
**Operator:** SOMOS Movilidad Rionegro S.A.S. / municipality of Rionegro, Antioquia, Colombia  
**Candidate network tag:** `bicirio-rionegro` (not registered)  
**Country:** CO; time zone: `America/Bogota`

## Official sources

- Operator system overview and FAQ:
  https://somosmovilidad.gov.co/sistema-de-bicicletas-bicirio/
- Operator questions and answers:
  https://somosmovilidad.gov.co/preguntas-frecuentes/
- Official public web application:
  https://bicirio.somosmovilidad.gov.co/
- Android app:
  https://play.google.com/store/apps/details?id=co.gov.somosmovilidad.bicirio
  (updated 2026-09-01)
- iOS app:
  https://apps.apple.com/co/app/bicirio/id6798346481
- Operator 2024 management report (contains history of platform
  migration and technical constraints):
  https://somosmovilidad.gov.co/wp-content/uploads/2025/04/Informe_Gestion_Junta_Directiva.pdf

The operator reports **18 public stations**, naming Palos Verdes, San
Antonio, El Faro, Edificios, El Porvenir, La Cuarta, San Nicolás, Unidad
Deportiva, Santa Ana, Plaza de la Libertad, San Francisco, Hospital,
Cuatro Esquinas, Barro Blanco, Porvenir 50, Villa Camila, Quebrada
Arriba and Zona Franca. The last two are virtual stations in the 2025
expansion. The operator describes public station screens with capacity,
available bicycles and available docks.

Published operating hours (verify current changes before GBFS publication):
- Monday–Friday: 06:00–18:00
- Saturday: 06:00–16:00
- Sunday: San Antonio-only 09:00–16:00, **temporarily suspended**
- Zona Franca virtual: Monday–Friday 06:00–16:00

## Verified public web application and data API

The public Angular frontend loads as HTML and JavaScript from
`bicirio.somosmovilidad.gov.co`. Its app bundle
`main-YSAWJGXJ.js` and lazy module `chunk-LJOODKNY.js`
were inspected without user accounts or credentials.

JavaScript sets `baseUrl: "/api/v1"` and explicitly provides:
- `GET /free_access/stations/get_all`
- `GET /free_access/bicycles/get_all_by_station/{station_id}`
- `GET /stations/public/get_all` (requires separate authentication
  assessment; **not** probed)

**Confirmed public read-only endpoint:**

```text
https://bicirio.somosmovilidad.gov.co/api/v1/free_access/stations/get_all
```

Response from GitHub Actions runner: HTTP 200, `application/json`,
**18 station records** (~4,777 bytes) with fields:

```text
id, name, address, altitude, confirmed, connectionState,
details, latitude, longitude, state, stationType
```

Second endpoint as implemented in the JS service:

```text
https://bicirio.somosmovilidad.gov.co/api/v1/free_access/bicycles/get_all_by_station/{id}
```

Read-only GET tests on 2026-11-15:

| Station ID | Name | HTTP | Response |
|---|---|---|---|
| 37 | Palos Verdes | 200 | empty JSON array `[]` |
| 21 | El Faro | 200 | empty JSON array `[]` |
| 36 | San Antonio | 200 | empty JSON array `[]` |

**Important:** empty responses do not establish permanently zero
bicycles or a broken endpoint. Sunday service is restricted, and
the provider may be offline. Recheck on an operating weekday before
treating bicycle availability as reliable.

### Data quality issues that block automatic publishing

1. **Latitude/longitude inconsistent:** Most API records use latitude
   for a longitude around -75.3 and longitude for a latitude around
   +6.1. However, El Faro (ID 21) has conventional order:
   `latitude=6.147648`, `longitude=-75.39029`.
   The parser must validate **each record** against Rionegro's
   geographic bounding box, correct swapped pairs and flag ambiguity.
2. **Invalid location:** ID 40 named `Virtual` has lat/lon `0,0`;
   do not publish this as a GBFS station without a verified location.
3. **Internal station records:** ID 38 named `Bodega` has
   `state=On_Maintenance` and is not on the operator's public 18-station
   list; it may be a depot. Keep excluded pending confirmation.
4. **Discrepancy:** The API's 18 records include `Virtual` and
   `Bodega` but do **not** contain operator-listed **Quebrada Arriba**
   or **Zona Franca**. It cannot be treated as a complete public
   network roster yet.
5. **Possible coordinate collisions:** La Cuarta (ID 31),
   Porvenir 50 (ID 24), and El Faro (ID 21) resolve to the same
   `6.147648, -75.39029` location after field correction.
   Check each against an independently verified station position.
6. **Unverified operational states:** 11 records report `Open`,
   6 `Closed`, and 1 `On_Maintenance` in this single snapshot.
   All 18 have `connectionState=false`. The semantic meanings and
   freshness of these fields are not yet established; do not use
   as `is_renting`/`is_returning` without further testing.
7. **No verified real-time bicycle supply:** the three tested public
   bicycle lists were empty. Do not invent available-bicycle counts or
   set empty to zero in a public feed until runtime behavior is verified.

### TLS / reliability blocker

Normal HTTPS validation from the GitHub Actions runner produces
`CERTIFICATE_VERIFY_FAILED: unable to get local issuer certificate`
for `bicirio.somosmovilidad.gov.co`.

To conduct *public static-code research only*, the isolated
`tools/research_bicirio.py` GitHub Actions job uses a narrowly scoped,
explicit TLS-verification fallback on the exact BiciRio host, with
**no account credentials** and **GETs to known public endpoints only**.
Never carry this bypass into a production scraper. Fix the upstream
certificate chain (or get a secure official endpoint) before
publishing GBFS.

Research job (station JSON and the three availability tests):
https://github.com/ColombiaTransit/gbfs-colombia/actions/runs/43748354326

## Next milestone / acceptance conditions

- [ ] Weekday verification: obtain a nonempty public bicycle response,
      with public bicycle type/status fields sufficient to calculate
      rentable station-level availability; otherwise determine if the
      endpoint is empty by design or temporarily out of service
- [ ] Confirm valid HTTPS certificate chain without bypass
- [ ] Reconcile internal API station IDs and all 18 public stations;
      exclude depot and 0,0 placeholders
- [ ] Verify lat/lon order **per record** and independent coordinates for
      ambiguous or duplicated sites
- [ ] Establish interpretation and freshness of `state`,
      `connectionState`, `confirmed` and station type
- [ ] Verify permission/terms for publishing provider data
- [ ] Only then implement `colombia_gbfs.scrapers.bicirio`, add
      tests/GBFS validator checks and enable via `ENABLED_NETWORKS`

**Do not run an automatic public GBFS feed yet.**

## One-time weekday retest (2026-11-16)

GitHub Actions workflow:
https://github.com/ColombiaTransit/gbfs-colombia/actions/workflows/bicirio-weekday-check.yml

- Target: Monday 2026-11-16 at 09:15 in Colombia (14:15 UTC, 15:15 CET).
- Tests only publicly documented BiciRio free_access GET endpoints.
- Fetches station roster and up to 12 open, geolocated, non-depot stations.
- Counts bicycle records without recording per-bike identifiers or rider data.
- Reports station names and IDs, coordinate orientation, and whether TLS validation succeeded.
- Formerly reported empty bicycle responses as failed runs; fixed on 2026-11-17. Valid empty JSON is now an observation (successful test) while actual API/network failures still fail.
- Artifact: bicirio-weekday-2026-11-16 (7-day retention).
- After the scheduled execution, the workflow disables itself to prevent annual recurrence.
- GitHub Actions scheduling is best-effort: execution may be delayed or missed.

Even a nonempty response is not sufficient for production GBFS: bike status,
operator station-list discrepancies and a valid HTTPS certificate still need verification.

## Results of 2026-11-16 scheduled checks (reviewed 2026-11-17)

The intended target was 09:00–09:15 Colombia. GitHub executed the
two redundant scheduled checks **much later**, at 18:08 and 18:24
Colombia time (23:08 and 23:24 UTC). Therefore the test **did not
verify daytime bike availability**.

- https://github.com/ColombiaTransit/gbfs-colombia/actions/runs/43976555952
- https://github.com/ColombiaTransit/gbfs-colombia/actions/runs/43978970535
- Both runs fetched **18 station records** and checked **12 eligible stations**.
- **Zero nonempty bicycle responses**, **zero bicycle records**.
- BiciRio's TLS chain was **not verifiable** in the research environment;
  the narrowly scoped research-only fallback was needed.
- Reports were successfully stored as artifacts despite the jobs
  finishing with exit code 1, because the script had incorrectly
  treated any valid empty bicycle response as a CI failure.
- This is a **data-availability uncertainty**, not evidence that
  the Docker container build or GHCR publication is broken.
- The separate official-site research run
  https://github.com/ColombiaTransit/gbfs-colombia/actions/runs/43976187120
  succeeded; the latest container publish run
  https://github.com/ColombiaTransit/gbfs-colombia/actions/runs/43870811435
  also succeeded.

**Remediation:** Consolidated BiciRio availability checks into one
manual workflow `.github/workflows/bicirio-availability.yml` and
removed obsolete duplicate one-time schedules. An empty but otherwise
valid public result no longer sends false failure notifications;
actual upstream API or parse errors still fail. The public
station/script research workflow remains manual.

## Breakthrough: public bicycle records returned on 2026-11-19

Manual research run:
https://github.com/ColombiaTransit/gbfs-colombia/actions/runs/44509243002

- **Successful at 10:50 UTC / 05:50 Colombia time**, before the
  planned 08:00–12:00 research window (and shortly before the
  operator's published 06:00 weekday start).
- The publicly accessible stations endpoint returned **18 records**.
  **12 open, geolocated, non-depot stations** were selected for
  read-only bicycle API checks.
- **9 of 12** checked stations returned nonempty bicycle arrays:
  **16 bicycle objects total**. No bicycle API request failed.
- All **12 checked stations** reported `connectionState=true`. This
  differs from the earlier 2026-11-15 sample where all 18 stations
  reported `false`. Exact semantics remain unverified.
- Coordinate classification in the 18 station records: **16 swapped**,
  **1 correct**, **1 invalid/unknown**.
- Nonempty bicycle objects have the fields `bicycleState`,
  `details`, `id`, `model`, `registerDate`, `serial`,
  `stationName`. **Only field names and aggregate counts were
  retained; not bicycle IDs, serials, or per-bike values.**
- **TLS certificate chain is still not verifiable** from GitHub Actions.
  The research-only exception is **not** suitable for production.

### Station-by-station object counts (NOT confirmed rentable bikes)

| Station ID | Name | State | Connection | Bike objects |
| --- | --- | --- | --- | ---: |
| 21 | El Faro | Open | true | 1 |
| 22 | Villa Camila | Open | true | 3 |
| 23 | San Francisco | Open | true | 1 |
| 24 | Porvenir 50 | Open | true | 2 |
| 25 | Barro Blanco | Open | true | 0 |
| 26 | Unidad Deportiva | Open | true | 2 |
| 27 | Santa Ana | Open | true | 2 |
| 28 | Hospital | Open | true | 0 |
| 29 | San Nicolas | Open | true | 2 |
| 30 | Los Edificios | Open | true | 2 |
| 32 | El Porvenir | Open | true | 1 |
| 33 | Plaza de la Libertad | Open | true | 0 |
| | **Total** | | | **16** |

Full aggregate-only report:
https://github.com/ColombiaTransit/gbfs-colombia/actions/runs/44509243002/artifacts/14520498523
(artifact retention: 7 days).

**Significance:** This conclusively demonstrates that BiciRio's
unauthenticated read-only per-station endpoint sometimes returns bike
objects. Previous empty results were temporary observations and must
not be treated as proof the endpoint is unusable.

**Still not GBFS-ready:** Inspect public, non-personal values of
`bicycleState` (prefer a non-identifying aggregate distribution) to
determine which count as rentable, independently verify ambiguous
station coordinates and missing public stations, and fix the upstream
TLS certificate chain. Confirm permission for data redistribution
before enabling the scraper. **Do not activate the network solely
because the endpoint returned 16 objects.**



## TLS chain verified independently from a GitHub Ubuntu runner (2026-11-19)

A dedicated **read-only TLS handshake** (no user data, credentials or
certificate verification bypass) confirmed the difference between the
browser's valid leaf certificate and the certificate chain the server
actually presents:

- Diagnostic action:
  https://github.com/ColombiaTransit/gbfs-colombia/actions/runs/44510522405
- Runner: Ubuntu 26.04, OpenSSL 3.5.5, default CA store with 120 CA certs.
- `openssl s_client -connect bicirio.somosmovilidad.gov.co:443
  -servername bicirio.somosmovilidad.gov.co -showcerts
  -verify 5 -verify_return_error` received **ONE certificate only**:
  the leaf `CN=bicirio.somosmovilidad.gov.co`, issued by
  **Go Daddy Secure Certificate Authority - G2**.
- OpenSSL: **exit code 1**, `Verify return code: 20
  (unable to get local issuer certificate)`.
- Python standard-library HTTPS: `SSLCertVerificationError`,
  **verify code 20**.
- `curl --head` (default certificate verification): **exit code 60**.
- User's Windows browser certificate viewer showed the leaf cert
  valid from **2025-11-16** to **2026-12-18**. This establishes
  expiration/issuer information about the leaf, **not** that the
  server transmits its missing intermediate certificate.

**Diagnosis:** The observed TLS server response omits the
intermediate CA certificate required by these Linux trust chains.
Browsers may fill in an intermediate from their certificate cache
or AIA fetching. Ask the operator to configure the correct
server certificate **fullchain** (leaf + appropriate intermediate,
with trusted root already on the client). Do not disable TLS
verification in a production GBFS scraper. Different edge/server
nodes could behave differently; the result is from GitHub's runner.

## Public bicycleState category investigation (2026-11-19)

An additional bounded aggregate-only research run succeeded:
https://github.com/ColombiaTransit/gbfs-colombia/actions/runs/44510927092

- Local unit tests: **9 passed**.
- **18** stations returned, **12** eligible stations checked.
- **9** stations returned nonempty public bicycle arrays.
- **16** bicycle objects total, with **all 16** reporting
  **`bicycleState = "Ready"`** (no other state values observed).
- This observation was at **11:01 UTC / 06:01 Colombia time**,
  shortly after the reported weekday opening time.
- The research output only contains short aggregate state
  categories, not bike identifiers, serial numbers, timestamps,
  individual locations or user/rider data.
- Field semantics are **not yet formally verified**:
  `Ready` plausibly denotes a rentable bike, but requires
  confirmation from an official UI example or operator documentation;
  do not silently count all objects as GBFS rentable.
- The two previously identified public frontend JS bundles were
  inspected without authentication. Only the public station marker
  label `bikeCount bicicletas disponibles` was found near the
  status search, **not** a mapping that explicitly defines the
  `Ready` bicycle enumeration.

The observed `Ready` state is a strong lead for implementing a
candidate parser behind tests. **No production GBFS activation yet:**
the missing TLS intermediate, ambiguous/duplicated coordinates,
operator's public station roster discrepancy and explicit
availability semantics should be resolved first.
