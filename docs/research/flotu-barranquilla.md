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
