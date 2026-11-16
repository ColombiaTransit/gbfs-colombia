# Neiva (Huila) — public bicycle lending / historical Biciclick source

**Research date:** 2026-11-16  
**Status:** historical municipal program verified (2019); **current operation and anonymous station availability unverified**.  
**GBFS:** research only, do not enable any scraper.  
**Provisional network tag:** `neiva-bicicletas-publicas` (not registered).  
**Timezone:** `America/Bogota`; country code `CO`.

## Official municipal sources (2019)

- Municipal article, 2019-07-12:
  https://www.alcaldianeiva.gov.co/NuestraAlcaldia/SalaDePrensa/Paginas/%C2%BFYa-usaste-las-bicicletas-p%C3%BAblicas.aspx
  - Free public bicycle loans via staff at `Centro Comercial Unicentro`
    and `Edificio Municipal / Alcaldía`, with **15 bikes at each**
    in July 2019.
  - Registration through `www.biciclick.com` or with a municipal
    attendant. Requirements included official ID, health coverage and
    utility bill. Never scrape user records, ID documents, registration
    forms or personal journey logs.
  - Announced *planned* additional points, including Parque Santander,
    Único, San Pedro Plaza, Banco Occidente; do not count these as
    verified stations in 2026.
- Municipal article, 2019-09-06:
  https://www.alcaldianeiva.gov.co/NuestraAlcaldia/SalaDePrensa/Paginas/Llegaron-m%C3%A1s-bicicletas-p%C3%BAblicas-a-Neiva.aspx
  - **30 additional bicycles** donated by BBVA, with a reported total
    fleet of **60 bicycles** by September 2019. This is historical
    supply, **not a current station-by-station inventory**.
- Municipal 2019-term summary:
  https://www.alcaldianeiva.gov.co/NuestraAlcaldia/SalaDePrensa/Paginas/Rodrigo-Lara-S%C3%A1nchez%2C-le-cumpli%C3%B3-a-los-neivanos-con-transparencia-y-resultados.aspx
  - Confirms municipal public bicycle program had **60 bicycles** and
    describes two points at administration close.
- Municipal article, 2026-04-10:
  https://www.alcaldianeiva.gov.co/NuestraAlcaldia/SaladePrensa/Paginas/As%C3%AD-avanza-el-d%C3%ADa-de-la-Bicicleta-en-Neiva.aspx
  - This is a **cycling promotion / safety day** (BiciMovilidad),
    **not a confirmation** of bicycle-share stations operating.

## Separate 120-bicycle shipment — do not conflate

Caracol Radio, 2022-08-08:
https://caracol.com.co/emisora/2022/08/08/neiva/1659961900_088799.html

Reports a **separate national programme of 120 bicycles** that
Neiva did **not** put into operation; municipality reportedly
declined to receive/operate them in July 2022. This number is **not**
the city's 2019 60-bike municipal operating inventory. Do not add
120 to the historical 60.

No newer operator statement confirming day-to-day public bikeshare
service in 2025/2026 was found in this research pass. Absence of a
report is **not proof that service has ceased**, but not enough to
publish a live GBFS system.

## Biciclick software / potential cross-city lead

- The 2019 official municipal source explicitly names
  `www.biciclick.com` as the registration platform.
- `https://biciclick.com/` now shows a **domain-for-sale page**.
  Do not use this domain as the current operator or API address.
- `https://biciclick.co/` is a *working* Biciclick S.A.S. website
  featuring free bicycle loans, registration, service hours,
  an advertised map, and mobile app section. The extracted public
  pages do **not** show a usable live station count/API:
  - https://biciclick.co/
  - https://biciclick.co/clientes/
- Historical municipal **Bisinú (Montería)** instructions also
  identify Biciclick as a registration provider, with a historical
  `http://biciclick.co/bisinu/` entry:
  https://www.monteria.gov.co/publicaciones/2160/como-funciona/
- This is a **cross-project operator/technology lead**, not proof
  that `biciclick.co` currently runs the Neiva or Bisinú systems.
  Do not merge the municipal networks or claim a shared current API.
- Biciclick terms identify a public business contact:
  https://biciclick.co/%C2%B7terminos-y-condiciones-%C2%B7/
  Contact email: `info@biciclick.co`. Any future outreach should ask
  specifically for a read-only aggregated **station availability**
  feed (or official GBFS), not private registration data.
- Independent evidence of continued Biciclick commercial activity
  in Bogotá in 2025 (different project; no connection asserted
  with present-day Neiva):
  https://parquearauco.modyocdn.com/uploads/3f289896-b203-451a-9de2-ca20e77da2ae/original/Memoria_2025_Parque_Arauco.pdf
  This **does not establish service status in Neiva**.

## GBFS scraper assessment

| Required data | Verification |
| --- | --- |
| Historical operator/fleet (2019) | Confirmed |
| Current 2026 operation | Unconfirmed |
| Valid current stations / coordinates | Unconfirmed |
| Anonymous station availability API | **Not found** |
| Live available bikes, timestamps, capacity | **Not found** |
| Redistribution terms | Unconfirmed |

### Resolution

1. Confirm directly with Neiva mobility authority whether any
   public bicycle loan stations are running in 2026.
2. Ask Biciclick if it still serves Neiva and/or Montería,
   and whether it offers a publicly redistributable read-only
   `station_information` / `station_status` equivalent.
3. Inspect **only public site pages and unauthenticated data
   sources**; no account data, private ride information or mass
   endpoint guessing.
4. If active and a public real-time provider is confirmed,
   add a tested PyBikes-compatible adapter and validate GBFS
   with MobilityData before enabling it.
5. Do not fabricate bike availability from the 2019 fleet total.

**Decision:** archive Neiva as historical/provisional, not ready
for automated public GBFS publication. Biciclick is a notable
cross-city technology lead.
