# PalmiBici (Palmira) — GBFS feasibility register

Status: **registration/login required in PWA (user-observed); no confirmed anonymous availability endpoint**  
Investigated: 2026-11-15  
Candidate GBFS tag: `palmibici-palmira` (not enabled)  
Location: Palmira, Valle del Cauca, Colombia  
Time zone: America/Bogota

## Sources and verified facts

- Official public website: https://palmibici.com.co/
  - Public station section lists **11 historical station names**:
    U. Nacional; Imder; Estación del Ferrocarril; Parque Bolívar;
    Sec. Tránsito y Transporte; Llano Grande; Sena; U. del Valle;
    Bosque Municipal; Parque la Factoría; Casa de la Cultura.
  - Grey station icons reportedly mark out-of-service stations, but no
    machine-readable or time-stamped live station-status feed was found.
  - Site advertises Monday–Friday 07:00–19:00, Saturday 08:00–12:00
    for bicycle stations; confirm with operator before GBFS publication.
- Municipality (2026): https://palmira.gov.co/palmira-dice-no-al-vandalismo-cuidemos-las-estaciones-y-bicicletas-de-palmibici/
  - Says system has **10 stations** and reports vandalism issues.
  - This supersedes any unverified assumption that all 11 named
    stations on the website are operational.
- The official site links to a JavaScript PWA for registration/management:
  - https://palmibici-pwa.web.app/
  - https://palmibici-pwa.web.app/register
  - https://palmibici-pwa.web.app/information
- Provider site: https://www.ims.com.co/bicicletas
  - Integrated Mobility Systems advertises bicycle-sharing technology.
  - Its public site is not evidence of a Palmibici live feed.
- Historical iOS app listings describe realtime station capacity and dock
  availability, but app listing is from 2020. This does not establish that
  the current service/API is available in 2026.
  - https://palmibici.appstor.io/

## Public PWA static-asset analysis (GitHub Actions)

Workflow: https://github.com/ColombiaTransit/gbfs-colombia/actions/runs/43746649541  
Tool: `tools/research_palmibici.py`  
No login, credentials, private API operations or user accounts used.

Verified via GitHub Actions runner:

- `/`, `/register`, `/information`: HTTP **200**;
  same HTML shell (~20,623 bytes), JavaScript-driven application.
- Same-origin public JavaScript includes:
  - `main.cc10eb63f52db515.js` (~468 KB)
  - `polyfills.f946d3779880c5da.js`
  - `runtime.f8e048c4e24279d7.js`
- The public `main` JS contains a production `API_URI` reference,
  backend host `https://back.palmibici.com.co/`, and `/api` string.
- Static UI labels include `Estaciones`, `Bicicletas`,
  `Bicicletas en prestamo` and a `disponib...` fragment.
- Simple unauthenticated GETs:
  - `https://back.palmibici.com.co/` -> HTTP **404**
  - `https://back.palmibici.com.co/api` -> HTTP **404**
- **Important:** 404 on these two root paths does not prove that no
  nested endpoints exist. Nor does UI text prove an anonymous public
  availability API. No usable anonymous station/availability response
  was established in these tests.

## Registration gate verified and scope decision (2026-11-19)

The user confirmed that opening the PalmiBici webapp leads to
**registration/login before accessing its functionality**.

The operator's public website separately documents a registration
process: existing users sign in with username and password;
new users register, then visit the operations centre for their
system card. Source: https://palmibici.com.co/

**Distinguish three separate facts:**
1. The PWA has a registration/login gate for the relevant user
   interface, as the user observed.
2. Its static JavaScript assets are publicly retrievable, and a
   backend hostname was previously discovered.
3. Neither fact establishes an **anonymous, publicly licensed,
   realtime availability API**. The only tested root backend
   URLs returned 404; no legitimate anonymous station-data
   endpoint has been confirmed.

**Decision:** Hold PalmiBici at research-only status; do not create
accounts solely for scraping, use another person's credentials,
invoke private/authenticated fleet endpoints, or register an active
GBFS adapter. Researching the existing public JavaScript may identify
an explicitly anonymous station endpoint in future; if one is not
available, seek an official read-only feed or operator permission.
Private authenticated customer views must not be treated as a
public feed.

## Next steps before implementing an adapter

1. Identify the exact station-list service calls in the minified Angular
   PWA without accessing login-only or user-data operations.
2. Determine if the endpoint offers anonymous, redistributable
   **live per-station bicycle counts** and stable station IDs.
3. Validate list and service status against the operator's current
   **10-station** operational network.
4. Verify WGS84 station coordinates, capacity, dock availability,
   `last_updated` and opening times.
5. Clarify redistribution permissions with Palmibici/IMS if needed.
6. Only then add a PyBikes adapter under
   `colombia_gbfs/scrapers/` and enable via `ENABLED_NETWORKS`.

Research conclusion: **promising but not yet feed-ready**. Do not
invent counts or treat the public marketing station list as realtime.
