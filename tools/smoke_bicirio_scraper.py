#!/usr/bin/env python3
"""Run a single BiciRio live-read dry run within the built GBFS container.

No publication, no auth, no bike identifiers or serials in output.
"""
import json
from collections import Counter

from colombia_gbfs.registry import activate
from colombia_gbfs.scrapers.bicirio import OFFICIAL_MAP_COORDINATES

# Exact stations previously lost because the API reused the same coordinates.
MAP_RECOVERED_STATIONS = {
    "21": "el faro",
    "24": "porvenir 50",
    "31": "la cuarta",
}


def main():
    activate(allowed=["bicirio-rionegro"])
    from pybikes import get

    system = get("bicirio-rionegro")
    system.update()
    stations = system.stations
    if not stations:
        raise RuntimeError("No safely geolocated BiciRio stations")

    unique_ids = {s.get_hash() for s in stations}
    if len(unique_ids) != len(stations):
        raise RuntimeError("BiciRio stable station IDs collided")
    if any(s.bikes is None or s.bikes < 0 or s.free is not None for s in stations):
        raise RuntimeError("Invalid BiciRio bicycle count/dock inference")
    station_by_id = {str(s.extra["uid"]): s for s in stations}
    verified_map_recoveries = {}
    for station_id, map_name in MAP_RECOVERED_STATIONS.items():
        station = station_by_id.get(station_id)
        if station is None:
            raise RuntimeError("Official-map station missing from live BiciRio adapter: " + station_id)
        actual = (station.latitude, station.longitude)
        expected = OFFICIAL_MAP_COORDINATES[map_name]
        if actual != expected:
            raise RuntimeError("Official-map coordinates mismatch for BiciRio station " + station_id)
        verified_map_recoveries[station_id] = map_name
    if len(stations) < 16:
        raise RuntimeError("Expected all 16 currently identified public API stations")
    counts = Counter(str(s.extra["station_state"]) for s in stations)
    report = {
        "status": "scraper_dry_run_ok",
        "network": "bicirio-rionegro",
        "published": False,
        "station_records_emitted": len(stations),
        "recovered_official_map_stations": verified_map_recoveries,
        "unique_station_ids": len(unique_ids),
        "bike_objects_counted": sum(s.bikes for s in stations),
        "station_status_counts": dict(sorted(counts.items())),
        "reported_online_stations": sum(1 for s in stations if s.extra["online"]),
        "unknown_free_docks_kept_null": all(s.free is None for s in stations),
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
