# ViboBici — El Carmen de Viboral, Antioquia

**Reviewed:** 2026-11-20  
**Research status:** 2026 relaunch announced; public station-level feed **not confirmed**.  
**Provisional GBFS system ID:** `vibobici-carmen-de-viboral` (research only, not registered or enabled)  
**Municipal system:** El Carmen de Viboral; historical implementation/operation has involved EDUR.  
**Country/time zone:** CO / America/Bogota.

## Evidence, chronologically

1. 2022 launch described three automated stations (Florelba, Viboral and Mayoral Verde) and 70 bikes; these named station labels are **historical**, not confirmed as current 2026 station IDs:
   https://www.elcolombiano.com/amp/antioquia/en-julio-comenzaran-a-rodar-las-bicicletas-publicas-de-el-carmen-de-viboral-GK17847771
2. 2024 municipality-linked health assessment recorded three sites: Centro de Acopio, Parque Simón Bolívar, Parque Educativo. Historical only; do not infer live counts or coordinates:
   https://dssa.gov.co/asis/documentos2024/asis2024/ORIENTE/El%20Carmen%20de%20Viboral%202024.pdf
3. Municipal 2024 procurement referred specifically to **manual operation** by EDUR, indicating that original automation/app claims may not reflect subsequent operations:
   https://colombialicita.com/licitacion/250684372
4. EDUR contract `014-2026-SD`, published 2026-01-30, concerns preventive/corrective maintenance of public bikes:
   https://colombialicita.com/licitacion/293619379
5. Municipality's social page mirrored at FindGlocal dated **2026-02-16** announced ViboBici's return to service:
   https://www.findglocal.com/CO/Carmen-de-Viboral/1588636578081476/Alcald%C3%ADa-de-El-Carmen-de-Viboral
   This is evidence of a relaunch announcement, **not** real-time service health.
6. AppStorio catalogs an iOS app `Vibobici`, app ID **1640508514**, publisher **GRUPO INVERSIONES DE COLOMBIA ZOMAC S.A.S.**, version shown **2.9**:
   https://vibobici.appstor.io/
   Store discovery/third-party listing does **not** prove the app is currently used by the municipality, that its backend is accessible, or that the listing version is current.

## Technical investigation begun

- Confirmed an app listing and the official public relaunch announcement; no verified anonymous GBFS or station-status JSON was located in public web-indexed searches as of review.
- Apple App Store URL candidate from published app ID: https://apps.apple.com/co/app/vibobici/id1640508514 ; tool retrieval failed, so its actual availability and recent updates **remain unverified**.
- Before APK/IPA analysis, establish whether current checkouts are manual or digitally managed. An iOS store listing alone is not an authorization to reverse engineer private rider information.

## Next actionable checks

1. Verify actual service delivery in late 2026, current stations and hours, and whether EDUR still handles rentals manually.
2. Check if a **public** operator station map exists with read-only anonymous bike counts, GPS coordinates and update timestamps.
3. If public feeds do not exist, request an anonymized station-status export or published GBFS feed from EDUR/municipality.
4. Preserve historical station names separately; do not publish historic inventory as live bikes.
5. Only implement a PyBikes adapter after a verified lawful source is identified.

**Decision:** High-priority source research; **no production scraper** and no changes to `ENABLED_NETWORKS`.
