# Flotu — Barranquilla (commercial micromobility)

**Research date:** 2026-11-16
**Status:** Commercial scooter and electric-bike rental platform,
public app and operator confirmed; **anonymous API and bike availability
not yet proven**. Research only; do not enable a GBFS adapter.
**Proposed system tag:** `flotu-barranquilla` (not registered)
**Company:** PIVVOT CONSULTING S.A.S / Flotu
**Country/timezone:** CO / America/Bogota

## Evidence that this service is real and technologically relevant

1. **Municipality's official 2025-01-13 authorization of scooter rental
   vendors**, including Flotu, Scooter del Río and Scooterland at six
   **shared** pickup locations across Gran Malecón:
   https://barranquilla.gov.co/desarrolloeconomico/tres-operadores-encargados-ofrecer-servicio-patinetas-gran-malecon
   - Crucial: these **six sites** are *joint municipal scooter-vendor
     pickup locations*, **not six independently verified Flotu
     bicycle-sharing stations**.
   - The associated 14:00–23:00 operator hours are for the 2025
     municipal scooter rental framework; do not directly publish
     as current Flotu bike hours.
2. Official rental site:
   https://flotu.com/
   https://flotu.com/alquiler-vehiculos
   - Currently advertises **electric bicycles**, e-scooters and
     tourist vehicles.
   - The site's marketing pages show no verified public station list,
     bike counts or GBFS endpoint.
3. Google Play Android app:
   https://play.google.com/store/apps/details?id=com.pivvot.FlotuApp
   - Android package `com.pivvot.FlotuApp`.
   - Updated **2026-09-15**; advertises bicycles and e-scooters.
   - Developer/publisher PIVVOT CONSULTING S A S, Barranquilla.
4. Official iOS app:
   https://apps.apple.com/es/app/flotu/id6446254367
   - Describes the ability to **view stations and available vehicles
     on a map**, including scooters and electric bikes.
   - App functionality is a reason to investigate, **not evidence of
     an anonymous API**.
5. Independent operating evidence: visitor reviews of the Barranquilla
   Malecón rental operation from April 2026, mainly describing
   scooters, not independently confirming specific live e-bike stock:
   https://www.tripadvisor.co/Attraction_Review-g297473-d24803540-Reviews-Flotu-Barranquilla_Atlantico_Department.html

## Public webpage/static JS investigation (no APK analysis)

**GitHub Actions run:**
https://github.com/ColombiaTransit/gbfs-colombia/actions/runs/43818876143

**Tool:**
`tools/research_flotu.py` and
`.github/workflows/research-flotu.yml`.

The run accessed only official *public HTML and static JS* from
`flotu.com` and `app.flotu.com`; no authentication, bookings,
private API requests or rider data were involved.

Verified HTTP responses:
- `https://flotu.com/`: **200**, public marketing page
- `https://flotu.com/alquiler-vehiculos`: **200**
- `https://app.flotu.com/`: **200**, page title **Flotu Admin Console**

The marketing site's public bundle
`/_components/v2/063be6fa5f4d16053ad380e52e6be66c9ee71bef.js`
mentions backend
`https://app.flotu.com/api/v1` (not yet a working public API).
The Admin Console also contains:
- `/api/v1`
- `/vehicles`
- `/vehicles/categories`

These references are visible in **static administration code** and
must **not** be assumed to provide public bike availability or
permission to redistribute provider/private inventory.

**Important:** `/vehicles` is a frontend route candidate; the asset
scan does not prove that a public unauthenticated GET at this path
returns a usable bicycle inventory. We deliberately did not probe
admin-only resource endpoints.

## GBFS feasibility

- Flotu mixes **electric bicycles**, **e-scooters** and tourist
  equipment. Restrict a bicycle-specific dataset to bona fide rentable
  bikes; never treat scooters or motorcycles as bicycles.
- Determine if bikes are available without reservation at multiple
  public pickup points (GBFS-compatible), or if this is only an
  advance-booking tourist rental business with attendant inventory.
- For stations: require publicly releasable IDs, WGS84 coords,
  vehicle types, operating hours, rentable availability and freshness.
- For free-floating bikes: need only legally/operationally publishable
  per-vehicle availability/location and meaningful timestamps. Avoid
  private GPS data.
- App shows vehicle/station inventory, but app screenshots and labels
  **do not establish current non-zero bike stock**.
- The Flotu **Admin Console is not a proper public scraping source**:
  do not create accounts to mine data, bypass authorization or
  expose private fleet/booking operations.

## Recommended follow-up

1. Search for an **official public read-only discovery/availability API
   or GBFS feed**, or contact Flotu about an export/integration.
2. Confirm e-bikes (not only scooters) are available to the public at
   specific Barranquilla stations during normal operating hours.
3. Ask the operator for aggregate/anonymous station-level
   availability, timestamps, rights and a stable schema. Avoid
   collecting accounts, personal information, booking histories or
   precise in-use rider locations.
4. On verified availability, implement a PyBikes-compatible adapter,
   validate the GBFS with MobilityData and enable the network
   explicitly in the registry/compose configuration.

**Decision:** Keep as **high-priority research lead**, not production
GBFS-ready. No active scraper or recurring polling job is justified yet.


## Full static JavaScript route inventory (2026-11-19)

Read-only GitHub Actions inspection of the **exact** public JS files:
https://github.com/ColombiaTransit/gbfs-colombia/actions/runs/44523641674

- Marketing site:
  https://flotu.com/_components/v2/063be6fa5f4d16053ad380e52e6be66c9ee71bef.js
  (1,549,277 bytes; 9,266 analyzed JS string literals)
- Admin console:
  https://app.flotu.com/main.605db60a5b2b7808.js
  (616,105 bytes; 2,619 analyzed JS string literals)
- Static analysis only, **no authenticated or unauthenticated API
  endpoints were invoked** and no account, payment or rider data
  was retrieved.

The marketing bundle contains these relevant URL/route references:
- \`https://app.flotu.com/api/v1\` — apparent API base
- \`/admin/login\` — website or administration route, not proven API
- \`/alquilar\` — public rental/website route, not proven API
- Several local marketing image assets associated with the customer
  rental app, operator map and fleet-manager dashboards — **not APIs**.

The administration JS contains **27 unique route/API-like strings**
(including \`/api/v1\`, \`/login\`, and a \`https://app.flotu.com\`
base reference). Relevant groups:

| Area | Literal strings found |
| --- | --- |
| Vehicle inventory | \`/vehicles\`, \`/vehicles/\${F}\`, \`/vehicles/categories\` |
| User records | \`/users\`, \`/users/\${F}\` |
| Operator records | \`/operators\`, \`/operators/\${F}\`, \`/operators/stats\` |
| Payments | \`/payments\`, \`/payments/\${F}\`, \`/payments/stats\` |
| Auth | \`/auth/login\`, \`/auth/logout\`, \`/auth/register\`, \`/auth/profile\`, \`/auth/refresh\`, \`/auth/token/refresh\`, \`/auth/forgot-password\`, \`/auth/reset-password\` |
| Leaderboards | \`/leaderboards/local/riders\`, \`/leaderboards/admin/riders\`, \`/leaderboards/admin/progression/riders\`, \`/leaderboards/admin/set-rider-score\`, \`/leaderboards/admin/simulate-rider\` |
| Bases/frontend | \`/api/v1\`, \`/login\`, \`https://app.flotu.com\` |

The \`\${F}\` interpolation is an internal minified-JS variable,
likely a record identifier, not a literal path segment. The static
inventory **does not establish HTTP methods, authorization rules or
working route responses**: some strings may denote frontend routing.
No explicit station availability, anonymous bike-count or GBFS
endpoint was found in these two specific bundles.

**Next sensible action:** look for an officially exposed **read-only
public** vehicle/station availability endpoint or ask Flotu to provide
a public feed. Do not probe the administrator's user/payment/operator
routes or assume \`/vehicles\` is anonymously accessible.


## Anonymous route/authentication probe (2026-11-19)

**User-requested limited investigation**, using public admin JS inspection
and unauthenticated **GET/HEAD** requests with redirects disabled.
No login, bypass, credentials, user records, vehicle identifiers,
locations, payment details, or individual vehicle payloads were
recorded. The bounded final probe read the API JSON only in memory
to report aggregate array length and top-level field names.

- Static inspection and initial status probe:
  https://github.com/ColombiaTransit/gbfs-colombia/actions/runs/44524458286
- Trailing-slash and final shape-only probe:
  https://github.com/ColombiaTransit/gbfs-colombia/actions/runs/44524906578
- Test script: \`tools/probe_flotu_public_auth.py\`
- Exact publicly served JS analyzed:
  \`https://app.flotu.com/main.605db60a5b2b7808.js\`

### What the public admin JS actually says

The bundle contains an HTTP interceptor that obtains
\`authService.getAccessToken()\` and, when present, appends
\`Authorization: Bearer <token>\` to requests. Token refresh logic
uses \`flotu_admin_refresh_token\`. Its dashboard route guard checks
\`authService.isAuthenticated()\` and \`authService.canAccessAdmin()\`;
non-authenticated users are redirected to \`/login\`. These are
**strong evidence that the admin interface is authenticated**;
they do not independently prove that **every** backend route rejects
anonymous GETs.

### Exact anonymous HTTP results

| Status-only request | Result |
| --- | --- |
| \`HEAD /api/v1/vehicles\` | 301 redirect to trailing slash |
| \`GET /api/v1/vehicles\` | 301 redirect to trailing slash |
| \`HEAD /api/v1/vehicles/\` | **200 application/json** |
| \`GET /api/v1/vehicles/\` | **200 application/json** |
| \`HEAD /api/v1/vehicles/categories\` | 301 redirect to trailing slash |
| \`GET /api/v1/vehicles/categories\` | 301 redirect to trailing slash |
| \`HEAD /api/v1/vehicles/categories/\` | **404 application/json** |
| \`GET /api/v1/vehicles/categories/\` | **404 application/json** |

Final bounded, shape-only inspection of **unauthenticated**
\`GET https://app.flotu.com/api/v1/vehicles/\` showed the
top-level fields **\`count\`, \`next\`, \`previous\`, \`results\`**.
The \`results\` value was a JSON list with **0 records**.
No error key was present. The aggregate \`count\` field's value
was not recorded; no contents of vehicle records were output.

**Interpretation:** The apparent vehicle listing route does not
universally return HTTP 401/403 to anonymous callers. But the only
anonymous snapshot yielded **no vehicle records**, so no public
rentable stock, GBFS feed or station-based availability can currently
be established. A zero-length \`results\` array does **not**
demonstrate that the operator has zero inventory; filtering,
account permissions, data availability and route semantics remain
unresolved.

**Decision:** Do not activate a Flotu scraper or infer that the
admin endpoint is a usable public feed. If revisited, prioritize
the actual public *customer* app or an operator-provided,
read-only availability feed. Avoid mining private/admin inventory.


## User-supplied Flotu XAPK 1.8.5 — static review, 2026-11-19

A user-supplied `flotu_1.8.5_APKPure.xapk` archive was inspected locally without installing or launching the app, account creation, emulator use, or private data access.

- XAPK manifest package `com.pivvot.FlotuApp`, version name `1.8.5`, version code `103`, minimum SDK 24, target SDK 36.
- XAPK SHA-256: `b3b5298b034d5a48b4790c57f02bf9861b78985564043bbdf622828ca3373fa1`.
- The base APK contains `assets/index.android.bundle` (5,955,744 bytes), a **compiled Hermes bytecode bundle**, not ordinary plain-text JavaScript. React Native/Expo modules are present. This makes naïve `strings`/regular-expression extraction ambiguous because different string-table values are packed together.
- Static bundle string-table leads include `https://app.flotu.com`, `/api/v1/vehicles/by-company/`, `/api/v1/marker-images/for-app`, `/categories-and-vehicles`, `/available_vehicles/fleet-list`, and UI concepts for `station`, `vehicle`, `availability`, and `location`. Treat these as **candidate literals only**. Their grouping in extracted bytes does not establish a complete request URL, HTTP method, authentication requirements, or response schema.
- These mobile-side leads support prioritizing the **public customer app vehicle discovery flow** over additional exploration of the admin console. Do not assume the admin `/api/v1/vehicles/` response (HTTP 200 with empty `results` in a previous test) is the customer-facing inventory source.
- No live vehicle ID, vehicle location, active station, rentable bike count or anonymous customer-app endpoint has yet been validated. A public GBFS feed is still **not ready**.

**One bounded next step (no more APKs needed):** use a proper Hermes bytecode disassembler (or a provider-documented public endpoint) to resolve how customer app request URLs are assembled and whether the app requests anonymous vehicle discovery; then test only a confirmed public-read request with no personal account, booking, tracking or admin functions. If the relevant route is authenticated, pause and ask the provider for read-only GBFS/public data access. Avoid inferring working endpoints solely from string concatenation.
