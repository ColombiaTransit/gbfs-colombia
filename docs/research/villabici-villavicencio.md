# VillaBici — Villavicencio, Meta, Colombia

**Status (2026-11-16):** historical service and a user-reported reachable website; **no confirmed public station availability/API**. Do not enable a GBFS scraper.
**Candidate network ID:** `villabici-villavicencio`
**Operator (historically):** Alborada E.I.C.E / Secretaría de Movilidad de Villavicencio
**Timezone:** America/Bogota

## Sources

- Official 2022 launch:
  https://villavicencio.gov.co/entro-en-funcionamiento-villabici-el-sistema-publico-de-bicicletas-de-villavicencio/
  - Seven original stations and 120 bicycles (100 manual, 20 electric assist).
  - The official site `https://www.villabici.net/` is explicitly described as a **user registration** channel.
- Official 2023 relaunch:
  https://villavicencio.gov.co/el-servicio-publico-de-bicicletas-villa-bici-vuelve-a-las-calles-de-villavicencio/
  - Eight stations and approximately 70 bicycles at the time.
  - Listed locations: Plaza de los Artesanos, Plaza Los Libertadores, Parque de los Estudiantes, Iglesia El Templete, Siete de Agosto, Cámara de Comercio de Villavicencio, Primavera Urbana, La Esperanza.
- 2023 Alborada management update:
  https://alboradaeice.com/noticias/villavicencio-avanza-hacia-una-movilidad-sostenible-con-el-%C3%A9xito-del-sistema-p%C3%BAblico-de-bicicletas-villabici-21
  - 8 active stations under contract 1951/2023, with plans for three more.
- Ministry of Transport 2024-09-25:
  https://mintransporte.gov.co/publicaciones/11837/villavicencio-en-movimiento/
  - Announced a **2025 relaunch**, but that announcement is **not** proof of 2025/2026 operations.
- Historical registration URL, referenced 2022:
  https://www.villabici.net/register.php
- City institution directory includes a public bicycle system email:
  https://villavicencio.gov.co/alcaldia/directorio-institucional/
  `bici.inteligente@alboradaeice.com`

## Website evidence / uncertainty

- On 2026-11-16, the user reported that `villabici.net` is **accessible from their connection** but exposes **no obvious public station map**.
- Our public web retrieval failed for that URL (502), which must **not** be interpreted as general downtime.
- Available primary-source descriptions of the website focus on registration and conditions of use, not live bicycle availability.
- **No public, read-only realtime station JSON or API URL is confirmed.**
- Do not confuse Colombian `villabici.net` with **Spanish `vilabici.com`**, an unrelated e-bike sharing operation.
- Avoid scraping registration forms, rider IDs or other private user data.

## GBFS follow-up

1. Verify live operation in 2026 and actual station list.
2. If a site operator makes public JS/JSON station data accessible, identify stable station IDs, GPS coordinates and **timestamped available bike counts**.
3. Otherwise ask Alborada for a public, anonymized station-status feed or direct GBFS output.
4. Do not publish historical fleet totals as live availability.

**Decision:** Lower-priority research candidate; no scraper, no periodic Action.
