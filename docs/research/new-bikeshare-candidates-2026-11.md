# Colombian public bikeshare — new candidates, November 2026

**Assessed:** 2026-11-20  
**Scope:** Research candidates *not already covered by the existing individual research files* in this repository. This is a source-discovery register, **not** a list of enabled GBFS feeds.

## New candidates

| Provisional ID | Municipality | Evidence of recent public-program activity | Public anonymous real-time station data | Priority | Detailed research |
| --- | --- | --- | --- | --- | --- |
| `vibobici-carmen-de-viboral` | El Carmen de Viboral, Antioquia | Municipal 2026 relaunch announcement; bike maintenance contract in Jan 2026 | **Not verified**; iOS app listing exists, but 2024 manual operation contract is a caveat | High | [ViboBici](vibobici-el-carmen-de-viboral.md) |
| `biciceja-la-ceja` | La Ceja, Antioquia | Municipality site includes BiciCeja registration; Sep 2026 operations contract and 2026 facilitators | **Not verified**; registration website is not an availability feed | High | [BiciCeja](biciceja-la-ceja.md) |
| `santa-rosa-en-bici` | Santa Rosa de Cabal, Risaralda | Sep–Oct 2026 coordination, parking-support and fleet-vehicle contracts | **Not verified**; source mentions historic operations-center software, but no public endpoint | Medium-high | [Santa Rosa en Bici](santa-rosa-en-bici.md) |
| `masbici-el-retiro` | El Retiro, Antioquia | 2025–2026 program funding/implementation contracts | **Not verified** | Medium | [MásBici](masbici-el-retiro.md) |

**Acceptance checklist for all:** public-lending confirmation; actual station IDs; accurate WGS84 coordinates; anonymized available bikes/docks and timestamp; reliable refresh; operator, hours, license/redistribution; GBFS 3.0 validation; offline scraper tests before registration. No inferred availability from historical fleet totals or from bike-parking visits.

## Not new / do not re-research without new evidence

Existing individual notes cover EnCicla, Tembici Bogotá, BiciRío, Rueda por Ibagué, MegaBici, PalmiBici, Bisinú, BiciPP, UrkuBici and a number of other municipal systems, including VillaBici, Chía, Cajicá and Zipaquirá. Their current evidence and decisions belong in those existing files, not duplicate registrations.

Additional systems surfaced during review **but not current targets**:

- **CLOBI Bucaramanga:** ceased operation in November 2023; multiple 2025/2026 reports confirm closure and dismantling. Do not enable from an outdated Metrolínea page:
  https://caracol.com.co/2026/06/04/las-bicicletas-publicas-desaparecieron-en-bucaramanga-que-paso/
- **Manizales en Bici:** a June 2026 civil-society report based on a 2026 municipality response addresses closure/condition of this historical network. No verified current service; not a GBFS target:
  https://www.corporacioncivicadecaldas.com/2026/06/que-paso-con-manizales-en-bici-y-cual-es-el-estado-actual-de-las-bicicletas-y-estaciones-del-sistema/
- **Apartadó pilot:** 2023 procurement covered bikes for a *pilot*; no evidence collected here of a current open service. Not a new active feed:
  https://colfirma.com/empresa/corporacion-correcaminos-830505764

## Work order

1. **ViboBici:** establish current manual-vs-digital operation; evaluate public (unauthenticated) app/site data without using personal accounts.
2. **BiciCeja:** inspect public `movilidadlaceja.com.co` BiciCeja-specific links for any aggregate station endpoint. Ignore private registration/vehicle-record functions.
3. **Santa Rosa en Bici:** establish whether operator software publishes a public station map rather than private operations data; distinguish parking, rentals, and balancing.
4. **MásBici:** identify the app/vendor, actual rental stations, and operator's data availability.

**Implementation rule:** Do not add anything to `config/scrapers.json`, `ENABLED_NETWORKS` or production until a lawful, verified, timestamped station-level source exists.
