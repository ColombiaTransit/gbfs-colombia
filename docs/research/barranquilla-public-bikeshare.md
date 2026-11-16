# Barranquilla — public bikeshare research register

**Checked:** 2026-11-16
**Region:** Barranquilla, Atlántico, Colombia
**Timezone:** America/Bogota
**Conclusion:** municipal SIBAQ ended in 2017. No current municipal
bike-share system with a verified anonymous real-time feed was found.
A commercial micromobility provider, **Flotu**, remains an interesting
separate research lead; see [Flotu research](flotu-barranquilla.md).

## A. Historical municipal SIBAQ system — definitively discontinued

**Operator:** Alcaldía Distrital de Barranquilla / Secretaría de Movilidad
**Provisional historical ID:** `sibaq-barranquilla`; **NEVER activate
as current GBFS** without a new documented launch.

### Official launch and legal documentation

- Official launch on 2015-12-10/11:
  https://barranquilla.gov.co/transito/alcaldesa-y-ministra-de-transporte-presentaron-bicicletas-publicas-en-barranquilla
- National Transport Ministry launch coverage, 2015-12-10:
  https://mintransporte.gov.co/publicaciones/4651/barranquilleros-empiezan-a-pedalear-con-bicicletas-publicas/
- Decree **0813/2015**, adopting pilot:
  https://barranquilla.gov.co/documento/gaceta-no-415-3/?version=1.1
- Resolution **0175/2015**, regulating usage:
  https://barranquilla.gov.co/documento/gaceta-no-415-7/?version=1.1

The original launch promised **74** bicycles (49 delivered at the
launch), while other retrospective reports speak of **73**; figures
are different historical source snapshots, **not present-day stock**.
Original pilot had **three** staff-assisted stations:

1. **Catedral:** Carrera 45 con Calle 53 (northeastern corner)
2. **Alfredo Correa de Andréis:** Calle 61 con Carrera 46
   (northwestern corner)
3. **Coliseo:** Carrera 54 between Calles 54 and 55
   (northeastern corner)

A user had to register, then present their ID and printed/signed
application at a staffed station, and could borrow a bicycle for
up to one hour during published Monday–Saturday 06:30–18:30
**historical** service times.

**Legacy registration URL**:
`http://movilidad.ibaq.co:9090/inscripcion/bicicletas/`.
It contains (or contained) identity-registration workflows. Do not
crawl or collect user registrations, identification numbers or
user histories. The fact that a registration form was publicly
announced is **not** evidence of a public anonymous bike availability
API.

### Operation / shutdown history

- The first pilot operator contract ended on 2016-03-11, and the
  three stations closed starting 2016-03-12:
  https://www.elheraldo.co/local/2016/04/07/desde-el-12-de-marzo-el-distrito-rueda-sin-bicicletas-publicas-252943/
- The service was temporarily relaunched in December 2016
  (historical news reports about 75 bikes and some additional
  stations — **not a verified 2026 roster**):
  https://www.elheraldo.co/barranquilla/2016/12/03/bicicletas-publicas-ruedan-otra-vez-en-barranquilla-308008/
- **2017-07-06**: City discontinued the public bike pilot due to low
  ridership and high cost (reported usage around three loans per day):
  https://caracol.com.co/noticias/regionales/dejara-de-funcionar-el-programa-piloto-de-sistema-de-bicicletas-publicas-en-barranquilla/20170706/nota/3512764.aspx
- **2017-07-07**: local news explicitly reports the city abandoning
  SIBAQ:
  https://www.elheraldo.co/barranquilla/2017/07/07/por-que-no-funciono-el-programa-de-bicicletas-379619/
- A 2019 local media review confirms that the service had ended
  for good in July 2017:
  https://www.inravision.gov.co/elecciones-colombia-2019/chevere-pensar-en-voz-alta-elecciones-regionales-en-barranquilla
- The national mobility report also describes Barranquilla/Soledad
  as lacking a public bicycle system since 2017. This is retrospective
  corroboration, **not a 2026 inventory**:
  https://manglar.uninorte.edu.co/bitstream/handle/10584/10958/1234094457.pdf?isAllowed=y&sequence=1

**Do not infer that listing the old 2015 decree in today's legal
archive means SIBAQ operates in 2026.** We found no reliable
2024–2026 relaunch or current municipal service feed.

## B. Bike lanes, bikeshops and rental operators — distinct scope

- City cycling-infrastructure map, updated 2025-07-31:
  https://barranquilla.gov.co/transito/mapa-cicloinfraestructura-de-barranquilla
  The **63.10 km bicycle infrastructure** is not a public
  shared-bicycle fleet.
- Ciclopaseos/ciclovías and community recreational events (including
  photographs of branded rental bicycles) are **not proof of a
  permanent docked/dockless public system**.
- Tourist rental shops and per-hour rental, including on the Gran
  Malecón, should not automatically be represented as public
  GBFS unless they offer genuinely public transport rentals with
  verified availability.
- **Tembici operates Bogotá's citywide shared bicycle network**;
  no verified Tembici Barranquilla stations were identified. Do not
  treat event photos or application availability as evidence of
  deployment here.
- **Flotu** is the most promising contemporary commercial micromobility
  lead. Its platform advertises electric bicycle and scooter rental,
  and its iOS listing advertises a vehicle/station map. See separate
  research document.

## C. GBFS decisions

| Candidate | Live operation evidence | Public anonymous station/vehicle data | Decision |
| --- | --- | --- | --- |
| SIBAQ | Discontinued 2017 | No | Exclude |
| Flotu | App updated Sep 2026; formal scooter rental operator since 2025 | Not verified | Research only |
| Generic tourist rental shops | May rent bikes | No confirmed realtime feed | Do not equate with system |
| Tembici in Barranquilla | Not established | N/A | Do not add |

**No active Barranquilla GBFS network should be added to
`ENABLED_NETWORKS` yet.**

Revisit SIBAQ only if the City announces a new specific bike-share
launch and publishes an anonymous feed. Focus any near-term technical
research on the Flotu passenger app or an official developer API,
not admin-console or rider data.
