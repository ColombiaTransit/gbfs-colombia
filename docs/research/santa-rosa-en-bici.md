# Santa Rosa en Bici — Santa Rosa de Cabal, Risaralda

**Reviewed:** 2026-11-20  
**Research status:** municipal system with 2026 operational contracts; distinguish **bike parking** from **bike lending**. No public bike availability API confirmed.  
**Provisional GBFS system ID:** `santa-rosa-en-bici` (research only, disabled)  
**Operator:** Municipio de Santa Rosa de Cabal.
**Country/time zone:** CO / America/Bogota.

## Evidence

- Historical municipal 2023 document register identifies a `Sistema de bicicletas públicas - Santa Rosa En Bici`:
  https://santarosadecabalrisaralda.micolombiadigital.gov.co/sites/santarosadecabalrisaralda/content/files/001085/54247_2023_registro_publicaciones_2023.pdf
- A 2026-09 procurement entry concerns staff operating **bike-parking modules** within `Santa Rosa en Bici`:
  https://colombialicita.com/licitacion/311031863
  Bike-parking module activity is not equivalent to a rentable bicycle count.
- Another September 2026 procurement concerns **coordination** of the public bicycle program:
  https://colombialicita.com/licitacion/311746849
- Contract **1141-2026**, signed 2026-10-09, concerns a **motocarro driver** for the public bicycle system, suggesting ongoing operational support but still not a live station inventory:
  https://www.buscadorsecop.com/detalle/CO1.PCCNTR.10046165
- A published copy of the municipal development plan describes historical software-supported operations and real-time operations-center data. This does **not** prove the data is published anonymously to the internet:
  https://es.scribd.com/document/928998591/Plan-de-Desarrollo-Santa-Rosa-d-Cabal-2024-2027

## Technical assessment

- A potential internal software backend merits verification. Vendor, domain, API route, and public access **not established**.
- No verified public GBFS/station availability endpoint; station counts, active docks and geographic coordinates should not be inferred from historic reports.
- Separate three services in all future source parsing: `bicycle_rental`, `bicycle_parking`, `fleet_rebalancing`.

## Next actions

1. Confirm whether `Santa Rosa en Bici` actively lends bicycles in 2026, not only provides parking.
2. Identify the actual software provider and any publicly displayed anonymous station map.
3. If no public station data, contact the municipal operator for a lawful anonymized read-only endpoint or official GBFS.
4. Avoid private user/registration records; publish only verified bike counts with timestamps.

**Decision:** Investigate, but **not eligible for a scraper yet**.
