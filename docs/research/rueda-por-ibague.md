# Rueda por Ibagué — source and feasibility register

Status: **research only / no scraper enabled**  
Checked: 2026-11-15  
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
- [ ] If needed, statically examine the public Android APK for non-secret domain and endpoint references; do not collect real user tokens, identity documents, or private ride history.
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
