#!/usr/bin/env python3
"""One-time, read-only research of BiciRio's explicitly public APIs.

No authentication, raw bike identifiers or rider data are collected.
The operator's HTTPS certificate chain currently fails verification:
the TLS fallback below is ONLY for this limited public research,
never for production or requests containing credentials.
"""
import argparse
from datetime import datetime, timezone
import json
import re
import ssl
import sys
import time
from urllib import error, parse, request
from zoneinfo import ZoneInfo

HOST = "bicirio.somosmovilidad.gov.co"
BASE = "https://" + HOST + "/api/v1/free_access/"
STATIONS = BASE + "stations/get_all"
BIKES = BASE + "bicycles/get_all_by_station/"
USER_AGENT = "ColombiaTransit-GBFS-Research/1.0 (public-stations-only)"
MAX_RESPONSE_BYTES = 1_000_000
MAX_STATIONS = 12
BOUNDS = {"south": 5.9, "north": 6.4, "west": -75.7, "east": -75.1}


def in_rionegro(lat, lon):
    return (isinstance(lat, (float, int)) and not isinstance(lat, bool)
            and isinstance(lon, (float, int)) and not isinstance(lon, bool)
            and BOUNDS["south"] <= lat <= BOUNDS["north"]
            and BOUNDS["west"] <= lon <= BOUNDS["east"])


def coordinate_status(station):
    """Check lat/lon for each record; never swap fields unconditionally."""
    lat, lon = station.get("latitude"), station.get("longitude")
    if in_rionegro(lat, lon):
        return "correct"
    if in_rionegro(lon, lat):
        return "swapped"
    return "invalid_or_unknown"


def select_stations(stations):
    """Public, open, geolocated, non-depot stations with numeric IDs."""
    eligible = []
    for station in stations:
        if not isinstance(station, dict):
            continue
        uid = station.get("id")
        if isinstance(uid, bool) or not re.fullmatch(r"[0-9]+", str(uid)):
            continue
        if station.get("stationType") == "TYPE_3":
            continue
        if str(station.get("name", "")).strip().lower() in {"virtual", "bodega"}:
            continue
        if str(station.get("state", "")).strip().lower() != "open":
            continue
        if coordinate_status(station) == "invalid_or_unknown":
            continue
        eligible.append(station)
    return sorted(eligible, key=lambda record: int(record["id"]))[:MAX_STATIONS]


def as_records(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("data", "items", "results"):
            if isinstance(payload.get(key), list):
                return payload[key]
    raise ValueError("Response is not a station/bicycle list")


def public_request(url):
    allowed = (url == STATIONS or
               (url.startswith(BIKES) and
                bool(re.fullmatch(r"[0-9]+", url[len(BIKES):]))))
    if not allowed or parse.urlsplit(url).hostname != HOST:
        raise ValueError("Refusing non-public or unexpected API request")
    req = request.Request(url, headers={
        "Accept": "application/json", "User-Agent": USER_AGENT
    }, method="GET")
    try:
        response = request.urlopen(req, timeout=15)
        tls_verified = True
    except error.URLError as exc:
        if "CERTIFICATE_VERIFY_FAILED" not in str(exc):
            raise
        # Isolated exception for this non-authenticated public research.
        response = request.urlopen(
            req, timeout=15, context=ssl._create_unverified_context()
        )
        tls_verified = False
    with response:
        if parse.urlsplit(response.geturl()).hostname != HOST:
            raise ValueError("Unexpected redirect away from official BiciRio host")
        ctype = response.headers.get("Content-Type", "").lower()
        if "json" not in ctype:
            raise ValueError("Expected JSON, got " + ctype[:80])
        body = response.read(MAX_RESPONSE_BYTES + 1)
        if len(body) > MAX_RESPONSE_BYTES:
            raise ValueError("API response exceeds 1 MB")
    return json.loads(body), tls_verified


def run_check(fetch=public_request, pause=time.sleep):
    now = datetime.now(timezone.utc)
    report = {
        "project": "BiciRio",
        "purpose": "One-time workday public bicycle availability check",
        "timestamp_utc": now.isoformat(timespec="seconds"),
        "timestamp_colombia": now.astimezone(
            ZoneInfo("America/Bogota")).isoformat(timespec="seconds"),
        "station_source": STATIONS,
        "bike_source_pattern": BIKES + "{station_id}",
        "api_station_records": None,
        "coordinate_status_counts": {},
        "eligible_stations": None,
        "tested_stations": [],
        "stations_with_nonempty_bicycle_response": 0,
        "total_bicycle_records": 0,
        "tls_verified_for_all_requests": True,
        "result": "not_started",
        "notes": [
            "No login, private endpoint, rider data or per-bike values collected",
            "An empty bicycle list is not proof of zero rentable bicycles",
            "Bike record counts do not establish whether bicycles are rentable",
            "No GBFS scraper is enabled as a result of this check",
        ],
    }

    try:
        stations_payload, verified = fetch(STATIONS)
        report["tls_verified_for_all_requests"] &= verified
        stations = as_records(stations_payload)
        report["api_station_records"] = len(stations)
        for st in stations:
            if not isinstance(st, dict):
                continue
            flag = coordinate_status(st)
            report["coordinate_status_counts"][flag] = (
                report["coordinate_status_counts"].get(flag, 0) + 1
            )
        eligible = select_stations(stations)
        report["eligible_stations"] = len(eligible)
        if not eligible:
            report["result"] = "no_eligible_public_stations"
            return report
    except Exception as exc:
        report["result"] = "station_api_error"
        report["error_type"] = type(exc).__name__
        report["error"] = str(exc)[:200]
        return report

    for st in eligible:
        sid = str(st["id"])
        row = {
            "station_id": sid,
            "station_name": str(st.get("name", ""))[:100],
            "station_state": str(st.get("state", ""))[:40],
            "connection_state": st.get("connectionState"),
            "coordinate_status": coordinate_status(st),
            "bike_record_count": None,
            "bicycle_field_names": [],
        }
        try:
            payload, verified = fetch(BIKES + sid)
            report["tls_verified_for_all_requests"] &= verified
            bicycles = as_records(payload)
            row["bike_record_count"] = len(bicycles)
            if bicycles and isinstance(bicycles[0], dict):
                # Do not store personal, vehicle-level or device identifiers.
                row["bicycle_field_names"] = sorted(bicycles[0].keys())[:40]
            if bicycles:
                report["stations_with_nonempty_bicycle_response"] += 1
                report["total_bicycle_records"] += len(bicycles)
        except Exception as exc:
            row["error_type"] = type(exc).__name__
            row["error"] = str(exc)[:160]
        report["tested_stations"].append(row)
        pause(0.6)

    if report["stations_with_nonempty_bicycle_response"] > 0:
        report["result"] = "nonempty_bicycle_responses"
    elif all(row["bike_record_count"] is None
             for row in report["tested_stations"]):
        report["result"] = "bicycle_api_errors"
    else:
        report["result"] = "no_nonempty_bicycle_responses"
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="bicirio-weekday-report.json")
    args = parser.parse_args()
    report = run_check()
    with open(args.output, "w", encoding="utf-8") as output:
        json.dump(report, output, ensure_ascii=False, indent=2)
        output.write("\n")
    print("Result:", report["result"])
    print("Station records:", report["api_station_records"])
    print("Stations tested:", len(report["tested_stations"]))
    print("Nonempty bicycle responses:",
          report["stations_with_nonempty_bicycle_response"])
    print("Total bicycle records (not proven available):",
          report["total_bicycle_records"])
    print("TLS fully verified:", report["tls_verified_for_all_requests"])
    print("Saved report:", args.output)
    return 0 if report["result"] == "nonempty_bicycle_responses" else 1


if __name__ == "__main__":
    sys.exit(main())
