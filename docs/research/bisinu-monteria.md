# Bisinú — Montería, Córdoba, Colombia

Status: **research only; no validated public live data feed**
Checked: 2026-11-19; Android availability reconfirmed: 2026-11-19
Candidate PyBikes tag: `bisinu-monteria` (not enabled)
Location: Montería, Córdoba, Colombia
Timezone: America/Bogota

## Reachability

- Historic project website: https://bisinu.com.co/
  - **Not reachable** by the available web retrieval on 2026-11-15
    using either HTTPS or HTTP. This is an observed failure, **not**
    confirmation of DNS expiration or permanent closure.
  - Developer's privacy policy still refers to this host:
    https://sites.google.com/view/bisinu-privacy-policy/inicio
    and lists historical support email `contactanos@bisinu.com.co`;
    **email deliverability is not verified**.
- Public 2023 municipal article:
  https://www.monteria.gov.co/publicaciones/4104/con-moderna-aplicacion-bisinu-mas-facil-y-asequible-a-todos-los-monterianos/
  - The municipality reported 12 stations / 100 bicycles at that date.
    Riders could check bicycle availability via the app after
    registration; there is **no evidence that this data is anonymously
    available**.
  - This is **2023 data**, not a verified 2026 live operating roster.
- Old municipal portal URL `http://biciclick.co/bisinu/` is referenced in
  older municipal FAQ, but is **not verified current**:
  https://www.monteria.gov.co/publicaciones/2160/como-funciona/
- The 2020 Montería cycling handbook also refers to
  `bisinu.com/registro`; historical only:
  https://www.despacio.org/wp-content/uploads/2020/06/ManualMonteria20191204webOpt.pdf

## Applications and technology

- Historical Android app package: `com.devdvs.bisinu.bisinu`.
  Link: https://play.google.com/store/apps/details?id=com.devdvs.bisinu.bisinu
  - **Removed from Google Play**: third-party app-history index records
    delisting on **2025-06-24**, and the user confirmed on **2026-11-19**
    that the Android app is no longer available. This is a confirmed
    Android distribution status, **not proof that Bisinú has ceased**.
  - Historical listing/index: https://chrome-stats.com/d/com.devdvs.bisinu.bisinu
  - Do not recommend this Google Play URL as an installable app; keep
    the package ID only for historical technical research.
- iOS app:
  https://apps.apple.com/co/app/bisin%C3%BA/id1671247807
  - Publisher: Ingeniería, Desarrollo y Asesorías S.A.S. (IDEAS).
  - Last version listed: `1.0.2`, released **2023-07-16**.
- Software supplier / original developer:
  https://appideas.com.co/
- Developer's published privacy policy describes IDEAS,
  the municipality and MOVAI as participants in the original app.
  The service involves account, identity and personal data.
  Do not probe authenticated endpoints or access rider/loan histories
  in the pursuit of anonymous station availability.

## 2026 renewal announced, NOT confirmed delivered

- 2026 article:
  https://larazon.co/monteria-ampliara-bisinu-a-20-estaciones-con-bicicletas-electricas-en-2026/
  - The mayor announced replacing aged mechanical bikes, expanding
    **12 to 20 stations**, adding some electric-assist bicycles and
    transferring operations to **La Perla del Sinú**.
  - These are **projected changes**. Neither completion nor a new
    application/API was verified in this review.
- Do not confuse **Bisinú bicycle share** with **Businú river bus**;
  similarly named current municipal sources about riverboats do not
  establish bicycle network data.

## GTFS/GBFS feasibility

| Signal | Status |
| --- | --- |
| Bike-sharing scheme | Confirmed historic, modernization planned in 2026 |
| Old project domain | Unreachable at review |
| Historic Android app | **Removed from Google Play (2025-06-24; user reconfirmed 2026-11-19)** |
| Historic iOS app | Still listed; latest version 2023 |
| Public live station IDs/coordinates | Not confirmed |
| Anonymous live bikes per station | Not confirmed |
| New operating platform | No verified public endpoint |
| Scraper implementation | **Deferred** |

A static map of 2023 stations is not a compliant substitute for fresh
GBFS 3.0 station status. Do not publish a zero-bike count when live
data is unavailable.

## Follow-up triggers

1. Establish whether the announced 2026 handover to
   **La Perla del Sinú** and the 20-station modernization completed.
2. Identify whether a **replacement Android/iOS app**, public dashboard
   or documented API was launched by the new operator. The legacy Android
   package is no longer distributed through Google Play.
3. Verify the actually active station roster, coordinates and
   bicycle/vehicle-type availability, without rider credentials.
4. Confirm operating hours, update timestamps, attribution and
   permission to republish.
5. Only then implement `colombia_gbfs.scrapers.bisinu` and register
   its tag in `ENABLED_NETWORKS`.

**Decision:** keep Bisinú on the research list but do not create
an active scraper or repeatedly request the currently unavailable
legacy site.

## Targeted municipal/operator follow-up — 2026-11-19

- **Newer official evidence (2026-09-11):** https://www.monteria.gov.co/publicaciones/6359/alcalde-hugo-kerguelen-avanza-con-findeter-caf-y-el-programa-nuca-para-poner-en-marcha-proyectos-para-conectar-a-monteria-a-traves-de-corredores-verdes/ — the mayor explicitly describes proposed green corridors as complementing the Bisinú public bicycle system. This confirms continued inclusion in municipal mobility planning, **not verified public rental operation on the review date**.
- **September 2026 municipal recognition:** https://www.monteria.gov.co/publicaciones/6336/alcalde-hugo-kerguelen-recibe-en-espana-reconocimiento-internacional-por-la-apuesta-de-monteria-por-la-sostenibilidad-y-la-innovacion-urbana/ — Bisinú again cited among municipal sustainable mobility projects; also not an operational station roster.
- Original 2026 report on the intended **12-to-20 station expansion, electric-assist bikes and transfer to La Perla del Sinú** remains a future-plan source: https://larazon.co/monteria-ampliara-bisinu-a-20-estaciones-con-bicicletas-electricas-en-2026/.
- Checked the public La Perla del Sinú website/news and targeted searches for updated operator announcements, a new user-facing app, station counts, or a public GBFS/API. **No confirming handover announcement, commissioned 20-station roster, replacement app or working anonymous data feed was verified.**
- **Name collision warning:** November 2026 riverboat news concerns **Businú**, not **Bisinú**, and must not be used as evidence for public bicycle-share operations.
- Maintain status **modernization and operator transfer announced; current operations and digital access unconfirmed**. Do not enable a realtime GBFS feed, infer 24/7 actual operation from proposed plans, or spend effort on the delisted APK without a new provider lead.

