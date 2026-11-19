# Rueda por Ibagué — source and feasibility register

Status: **research only / no scraper enabled**  
Checked: 2026-11-19  
Proposed PyBikes network tag: `rueda-por-ibague` (not registered yet)  
Operator: INFIBAGUÉ (Instituto de Financiamiento, Promoción y Desarrollo de Ibagué)  
Location: Ibagué, Tolima, Colombia  
Country code: CO  
Time zone: America/Bogota

## Confirmed primary sources

- Government program landing page: https://www.infibague.gov.co/sistema-de-bicicletas-publicas/
  - Page still describes the older 8-station / 85-bicycle configuration.
  - Not authoritative for the latest network count.
- Latest operator update (2026-10-28): https://www.infibague.gov.co/descargue-la-app-rueda-por-ibague-y-use-gratis-el-sistema-publico-de-bicicletas-de-la-alcaldia/
  - **10 stations**, **105 bicycles** (mechanical and electric-assist), **free** service.
  - Names: Parque de Belén, Plaza de Bolívar, Panóptico, Fontainebleau, Unidad Deportiva de la 42, Universidad de Ibagué, Éxito de la 80, La Samaria, Centro Comercial La Estación, Centro Comercial Multicentro.
  - Hours stated: Monday–Friday 06:30–18:00; Sundays/holidays 08:00–13:00.
  - Saturday hours **need verification**: the October notice omits Saturday; January 2026 included Saturday 08:00–13:00. Do not assert a current Saturday timetable without verification.
- Official Android app: https://play.google.com/store/apps/details?id=com.ruedaxibaguex
  - Package: `com.ruedaxibaguex`.
  - Google Play describes live station/bicycle availability, station map, QR unlocking, ride history.
  - Updated 2026-07-31 (observed listing).
- Official iOS app: https://apps.apple.com/co/app/rueda-por-ibagu%C3%A9/id1671010265
  - The iOS listing likewise describes live station/bicycle availability.
- Standalone website listed by the Android app: https://ruedaporibague.com/
  - Page title observed: `Bicycle Dashboard`.
  - Static text extracted by web crawler: `CARGANDO` (Spanish for loading).
  - Public JSON/API URLs **not yet established**.
- Older official station and location FAQ: https://www.infibague.gov.co/preguntas-frecuentes/
  - Has eight legacy station entries with individual Google Maps links; **not a complete current 10-station geospatial registry**.
- 2026-08-02 introduction of the smart La Samaria station:
  https://www.infibague.gov.co/alcaldesa-johana-aranda-entrego-la-primera-estacion-inteligente-para-bicicletas-de-la-ciudad/

## GBFS potential

A station-based GBFS 3.0 feed seems feasible **if** the publicly viewable station map/API exposes live status without using rider credentials or personal data. Required information:

1. Stable station IDs and names, WGS84 station coordinates.
2. Current count of rentable bicycles by station, ideally split by manual vs electric-assist.
3. Availability timestamp (must not report stale values as fresh).
4. Station renting/returning status and verified opening hours.
5. Operator attribution, contact and data usage permissions.

The source describes a dockless smart-lock model with designated return stations. Do **not** assume physical docks or publish dock availability unless substantiated.

## API discovery checklist

- [ ] Inspect the **public website's** HTML/JavaScript network requests and identify its data API, if any.
- [ ] Check for a published official GBFS/open-data endpoint before reverse-engineering.
- [ ] Determine whether public map data is accessible **without account login**.
- [x] Statically examine user-supplied XAPK v2.0.1 for domain and endpoint references (see 2026-11-19 results below); no user credentials collected.
- [ ] Record anonymized example of public station response and field mapping.
- [ ] Resolve current Saturday opening hours and station IDs/coordinates.
- [ ] Verify redistribution terms or request permission from INFIBAGUÉ.
- [ ] Implement a PyBikes-compatible `colombia_gbfs.scrapers.rueda_por_ibague` adapter **only after** establishing a lawful, working public data source.
- [ ] Validate generated GBFS 3.0 against MobilityData before enabling in `ENABLED_NETWORKS`.

## Research decisions

- 2026-10-28 operator publication supersedes the older website's 8/85 network figures.
- The existence of real-time functionality in the mobile apps **does not prove a publicly accessible API**.
- No undocumented URLs, credentials, station coordinates or live bike counts should be invented.
- Keep discovery separate from the production runtime until tested; default system list stays `encicla,tembici-bogota`.

## APK acquisition attempt — 2026-11-19

- Static-only GitHub Actions workflow exists at `.github/workflows/research-ibague-apk.yml` with `tools/research_ibague_apk.py`.
- Runs [44468234890](https://github.com/ColombiaTransit/gbfs-colombia/actions/runs/44468234890) and [44468338786](https://github.com/ColombiaTransit/gbfs-colombia/actions/runs/44468338786) **completed successfully as research jobs but did not download an APK**. Do not mislabel them as successful APK decompilation.
- Uptodown download page `https://rueda-por-ibague.uptodown.com/android/descargar` responded with 157,873 bytes of HTML, but provided **zero directly extractable APK download links**. The page exposes a dynamic download button `detail-download-button` with `data-file-id=1069122012`; JavaScript `download.js` and Cloudflare Turnstile are present. No challenge bypass or unauthorized API access was attempted.
- Uptodown lists **historical 1.0.9**, dated **2025-07-22**, APK size **37.79 MB**, SHA-256 `291e3e82032c4f0a759b7fc3ce67f7499ae3de1191fa117da9eda6b7fb3711cc`. This is **not** the latest Play Store release.
- Google Play lists current app package `com.ruedaxibaguex`, version **2.0.0.1.50**, updated **2026-07-31**. Its listing explicitly advertises a station map and real-time bike availability. Source: https://play.google.com/store/apps/details?id=com.ruedaxibaguex
- Additional potentially relevant official domain appears in the iOS listing metadata: `https://ruedaporibague.gov.co/`. This is **not yet confirmed to expose a public map/API** and should be checked as a separate public-web investigation.
- Next reproducible step: obtain an APK through a legitimate downloadable source or a user-provided APK file, verify package/version/hash, then perform static manifest/DEX/resource inspection for non-secret public availability endpoints. Never upload an APK binary to the repo or log credentials.
- **No API endpoint or public GBFS availability was confirmed by this APK attempt.**

## User-provided XAPK and access tests — 2026-11-19

**Research status: paused — authenticated API identified, no public read-only station feed verified.** Do not activate a scraper or keep repeating APK acquisition attempts.

- User supplied `Rueda+por+Ibagué_2.0.1_APKPure.xapk` (version 2.0.1). This supersedes the previous need to obtain an APK; avoid redundant downloads, emulator setup, and geographic egress experiments.
- Preliminary static-analysis findings reported in the investigation: Flutter Android application; production base URL `https://api.ruedaporibague.gov.co/api/v1`; Keycloak realm `https://auth.ruedaporibague.gov.co/realms/rueda`, OAuth2 Authorization Code client `rueda-android`.
- Candidate app endpoint paths: `/stations/summary-stations`, `/bikes/bikes`, `/bikes/bikes-types`, `/stations/workshift-schedules`. App model/field hints include `stationGuid`, `latitude`, `longitude`, `capacity`, `totalBikes` and bicycle status `Disponible`. These are **static-analysis leads**, not confirmed public response schemas.
- User ran anonymous HTTP requests from the Netherlands against `GET /stations/summary-stations` and `GET /bikes/bikes-types`. **Both returned HTTP 401 Unauthorized**. This confirms the target host responds and rejects anonymous requests to these routes; it does *not* prove all station information is unavailable anonymously.
- Android app is region-restricted for installation from the Netherlands. User cannot install via the local Play Store. Do not make installation, emulator, VPN or Colombian VPS prerequisites for continuing the project.
- Previously referenced station coverage URL `https://ruedaporibague.gov.co/estaciones-y-cobertura/` returns HTTP 404 (user verified). Retain the 2026-10-28 INFIBAGUÉ operator article as the current network scope source.
- No verified live station IDs, coordinates, bicycle availability counts, access token or redistribution permission has been obtained. The mobile app's private/authenticated routes must not be treated as an open GBFS data source.

**Deferred only if revisited:** check the public `ruedaporibague.com` dashboard for a separate anonymous read-only map source, or ask the operator for documented public access / service credentials with redistribution permission. Do not collect rider credentials or publish private tokens. Next investigation priority: **MegaBici Pereira**, using its existing register to avoid repeating its earlier research.
