"""BiciRio Rionegro: public, read-only bicycle station availability.

The official public Angular map uses len(bicycles) per station. This adapter
reproduces that count, *without* collecting or exposing bike identifiers.

Source currently omits an intermediate TLS certificate. HTTPS remains fully
verified using a host-specific CA bundle prepared at image build time with
a pinned official GoDaddy intermediate. Never use verify=False.

This plugin is registered but NOT enabled by default. Source data has known
coordinate issues and an incomplete official/public station roster.
"""
import hashlib
import json
import logging
import os
import re
import unicodedata
from urllib.parse import urlsplit

import requests
from pybikes.base import BikeShareStation, BikeShareSystem

LOG = logging.getLogger(__name__)
HOST = "bicirio.somosmovilidad.gov.co"
ORIGIN = "https://" + HOST
STATIONS_URL = ORIGIN + "/api/v1/free_access/stations/get_all"
BICYCLES_URL_PREFIX = ORIGIN + "/api/v1/free_access/bicycles/get_all_by_station/"
CA_BUNDLE = "/opt/venv/bicirio-godaddy-ca.pem"
MAX_STATIONS = 40
MAX_BICYCLES = 250
MAX_BYTES = 256_000
BOUNDS = {"south": 5.9, "north": 6.4, "west": -75.7, "east": -75.1}
# Public map markers published by the operator on its BiciRio system page:
# https://somosmovilidad.gov.co/somos-mapa/leaflet-routing-machine-3.2.12/examples/index.js
# Source: official Leaflet L.marker([latitude, longitude]) values, reviewed
# 2026-11-19. These are station coordinates, NOT real-time API availability.
# The public BiciRio API incorrectly duplicates multiple coordinates, so this
# operator-provided independent map has priority for known station names.
OFFICIAL_MAP_COORDINATES = {
    "el faro": (6.1412796, -75.3770481),
    "la cuarta": (6.150792, -75.392205),
    "los edificios": (6.149323, -75.385319),
    "san antonio": (6.130296, -75.3804),
    "plaza de la libertad": (6.153696, -75.373764),
    "san francisco": (6.154190, -75.372542),
    "san nicolas": (6.146392, -75.379080),
    "palos verdes": (6.126285, -75.383984),
    "cuatro esquinas": (6.153292, -75.362879),
    "el porvenir": (6.146621, -75.386334),
    "unidad deportiva": (6.146114, -75.374173),
    "santa ana": (6.15135, -75.36912),
    "el hospital": (6.158937, -75.370605),
    "porvenir 50": (6.1476775, -75.3893921),
    "barro blanco": (6.153107, -75.408059),
    "villa camila": (6.148877, -75.357714),
    "quebrada arriba": (6.157583, -75.375444),
    "zona franca": (6.157769, -75.412286),
}
# Documented spelling differences between operator map and current API.
MAP_NAME_ALIASES = {
    "edificios": "los edificios",
    "hospital": "el hospital",
}
UNUSABLE_NAMES = {"virtual", "bodega", "centro de operaciones"}


def _inside(lat, lon):
    return (type(lat) in (int, float) and type(lon) in (int, float)
            and BOUNDS["south"] <= lat <= BOUNDS["north"]
            and BOUNDS["west"] <= lon <= BOUNDS["east"])


def corrected_coordinates(record):
    """Validate each record, fixing reversed lat/lon only when unambiguous."""
    a = record.get("latitude")
    b = record.get("longitude")
    if _inside(a, b):
        return float(a), float(b)
    if _inside(b, a):
        return float(b), float(a)
    return None


def _normalized_name(name):
    if not isinstance(name, str):
        return ""
    ascii_name = "".join(
        ch for ch in unicodedata.normalize("NFKD", name.casefold())
        if not unicodedata.combining(ch)
    )
    return " ".join(re.sub(r"[^a-z0-9]+", " ", ascii_name).split())


def station_coordinates(record):
    """Prioritize the operator's independent public map; use valid API data only as fallback."""
    key = _normalized_name(record.get("name"))
    canonical = MAP_NAME_ALIASES.get(key, key)
    known = OFFICIAL_MAP_COORDINATES.get(canonical)
    if known is not None:
        if not _inside(*known):
            raise ValueError("Invalid coordinates in official BiciRio map reference")
        return known
    # A previously unseen station is not on the snapshot of the official
    # map; use the source if its coordinates are valid, without guessing.
    return corrected_coordinates(record)


def _public_id(value):
    if isinstance(value, bool) or not re.fullmatch(r"[1-9][0-9]{0,8}", str(value)):
        raise ValueError("Invalid BiciRio station ID")
    return str(value)


def _text(value, limit=120):
    return value.strip()[:limit] if isinstance(value, str) else ""


class BiciRioStation(BikeShareStation):
    """Station IDs must not collide when the source reuses coordinates."""

    def get_hash(self):
        uid = _public_id(self.extra["uid"])
        return hashlib.md5(("bicirio:station:" + uid).encode("ascii")).hexdigest()


class BiciRio(BikeShareSystem):
    """PyBikes-compatible provider; opted in with bicirio-rionegro tag."""

    sync = True
    meta = {
        "system": "BiciRio",
        "company": ["SOMOS Movilidad Rionegro S.A.S."],
    }

    @staticmethod
    def _json(session, url):
        """Restrict requests to the two known anonymous GET API paths."""
        if url != STATIONS_URL and not (
            url.startswith(BICYCLES_URL_PREFIX)
            and re.fullmatch(r"[1-9][0-9]{0,8}", url[len(BICYCLES_URL_PREFIX):])
        ):
            raise ValueError("Unexpected BiciRio URL")
        if urlsplit(url).hostname != HOST:
            raise ValueError("BiciRio host mismatch")

        bundle = os.environ.get("BICIRIO_CA_BUNDLE", CA_BUNDLE)
        if not os.path.isfile(bundle):
            raise RuntimeError("BiciRio TLS CA bundle missing; rebuild Docker image")
        with session.get(
            url, timeout=15, verify=bundle, allow_redirects=False,
            headers={
                "Accept": "application/json",
                "User-Agent": "ColombiaTransit-GBFS/1.0 (public-station-data)",
            }, stream=True,
        ) as response:
            if response.status_code != 200:
                raise requests.HTTPError(
                    "BiciRio public API HTTP " + str(response.status_code),
                    response=response,
                )
            if response.url != url:
                raise ValueError("Unexpected redirect or changed response URL")
            if "json" not in response.headers.get("Content-Type", "").lower():
                raise ValueError("BiciRio API did not return JSON")
            if int(response.headers.get("Content-Length") or "0") > MAX_BYTES:
                raise ValueError("BiciRio JSON exceeds response size limit")
            chunks = []
            length = 0
            for chunk in response.iter_content(chunk_size=16384):
                length += len(chunk)
                if length > MAX_BYTES:
                    raise ValueError("BiciRio JSON exceeds response size limit")
                chunks.append(chunk)
        records = json.loads(b"".join(chunks))
        if not isinstance(records, list):
            raise ValueError("BiciRio API expected a JSON array")
        return records

    @staticmethod
    def _eligible(records):
        """Filter internal stations and resolve positions from the official map first."""
        if len(records) > MAX_STATIONS:
            raise ValueError("Unexpectedly large BiciRio station roster")
        eligible = []
        seen_ids = set()
        seen_coordinates = set()
        for record in sorted(
            records,
            key=lambda r: int(r["id"]) if isinstance(r, dict)
            and str(r.get("id", "")).isdigit() else 9999999999,
        ):
            if not isinstance(record, dict):
                raise ValueError("BiciRio station entry must be an object")
            uid = _public_id(record.get("id"))
            if uid in seen_ids:
                raise ValueError("Duplicate BiciRio station ID")
            seen_ids.add(uid)
            name = _text(record.get("name"))
            if not name or _normalized_name(name) in UNUSABLE_NAMES:
                continue
            # TYPE_3 is used for the internal/virtual class in observed data.
            if record.get("stationType") == "TYPE_3":
                continue
            coords = station_coordinates(record)
            if coords is None:
                LOG.warning("Skip BiciRio station %s: invalid position", uid)
                continue
            key = tuple(round(p, 6) for p in coords)
            if key in seen_coordinates:
                LOG.warning("Skip BiciRio station %s: reused coordinates after map reconciliation", uid)
                continue
            seen_coordinates.add(key)
            eligible.append((record, coords))
        return eligible

    @staticmethod
    def _station(record, coords, bicycles):
        if len(bicycles) > MAX_BICYCLES:
            raise ValueError("Unexpectedly many bicycles at one station")
        if any(not isinstance(bike, dict) for bike in bicycles):
            raise ValueError("Unexpected bicycle item shape")
        # The official public map displays len(bicycles) without filtering
        # bicycleState. Fail closed on unfamiliar states; don't invent counts.
        states = {bike.get("bicycleState") for bike in bicycles}
        if any(not isinstance(state, str) or state != "Ready" for state in states):
            raise ValueError("Unverified BiciRio bicycleState; review before GBFS")
        state = _text(record.get("state"))
        online = state == "Open" and record.get("connectionState") is True
        station = BiciRioStation(
            name=_text(record.get("name")),
            latitude=coords[0],
            longitude=coords[1],
            bikes=len(bicycles),
            free=None,  # No supported dock capacity source: do not infer free docks.
            extra={
                "uid": _public_id(record.get("id")),
                "address": _text(record.get("address"), limit=200),
                "online": online,
                "station_state": state,
                "slots": None,
            },
        )
        return station

    def update(self, scraper=None):
        """Fetch a complete, self-consistent snapshot before publishing it.

        Hyper passes its general-purpose scraper, but it cannot safely set
        a BiciRio-only certificate bundle. Use an isolated requests.Session
        instead; do not mutate global CA or other networks' TLS settings.
        """
        with requests.Session() as session:
            source = self._json(session, STATIONS_URL)
            eligible = self._eligible(source)
            if not eligible:
                raise ValueError("No BiciRio public stations with reliable coordinates")
            new_stations = []
            for record, coords in eligible:
                uid = _public_id(record["id"])
                bicycles = self._json(session, BICYCLES_URL_PREFIX + uid)
                new_stations.append(self._station(record, coords, bicycles))
        # Publish atomically; any failed station request leaves prior snapshot alone.
        self.stations = new_stations
