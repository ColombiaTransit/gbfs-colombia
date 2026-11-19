"""Offline tests for BiciRio's public API adapter. No live API requests."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from colombia_gbfs.scrapers.bicirio import (
    BICYCLES_URL_PREFIX, STATIONS_URL, BiciRio, BiciRioStation,
    corrected_coordinates,
)
from colombia_gbfs.scrapers.bicirio import BOUNDS

META = {"name": "BiciRio", "city": "Rionegro", "country": "CO",
        "latitude": 6.152, "longitude": -75.374,
        "company": ["SOMOS Movilidad Rionegro S.A.S."]}


def station(id, name, latitude, longitude, state="Open",
            connected=True, station_type="TYPE_2", **extra):
    return {
        "id": id, "name": name, "latitude": latitude,
        "longitude": longitude, "state": state,
        "connectionState": connected, "stationType": station_type,
        "address": "Example address", **extra,
    }


class FakeResponse:
    def __init__(self, url, value, status=200, content_type="application/json"):
        self.status_code = status
        self.url = url
        self.headers = {"Content-Type": content_type}
        self.body = (value if isinstance(value, bytes)
                     else json.dumps(value).encode("utf-8"))

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def iter_content(self, chunk_size):
        yield self.body


class FakeSession:
    def __init__(self, fixtures, fail_path=None):
        self.fixtures = fixtures
        self.calls = []
        self.fail_path = fail_path

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if url == self.fail_path:
            raise ConnectionError("Simulated temporary API failure")
        if url not in self.fixtures:
            raise AssertionError(f"Unexpected URL: {url}")
        result = self.fixtures[url]
        if isinstance(result, FakeResponse):
            return result
        return FakeResponse(url, result)


class BiciRioTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.bundle = Path(self.tmp.name) / "public-ca.pem"
        self.bundle.write_text("test-only dummy CA", encoding="ascii")
        self.env_patch = patch.dict(os.environ, {"BICIRIO_CA_BUNDLE": str(self.bundle)})
        self.env_patch.start()
        self.addCleanup(self.env_patch.stop)
        self.roster = [
            station(21, "El Faro", 6.147648, -75.39029),
            station(22, "Villa Camila", -75.4012, 6.156),
            station(24, "Porvenir 50", -75.39029, 6.147648),
            station(36, "San Antonio", -75.3700, 6.1590, state="Closed"),
            station(37, "Palos Verdes", -75.3900, 6.1500, connected=False),
            station(38, "Bodega", -75.3800, 6.1550),
            station(40, "Virtual", 0, 0, station_type="TYPE_3"),
            station(41, "Invalid", 0, 0),
        ]
        self.fixtures = {STATIONS_URL: self.roster}
        self.fixtures.update({
            BICYCLES_URL_PREFIX + "21": [{"id": "private-id", "serial": "private-serial", "bicycleState": "Ready"}],
            BICYCLES_URL_PREFIX + "22": [{"bicycleState": "Ready"}, {"bicycleState": "Ready"}],
            BICYCLES_URL_PREFIX + "36": [],
            BICYCLES_URL_PREFIX + "37": [],
        })

    def fake_update(self, network, session):
        with patch("colombia_gbfs.scrapers.bicirio.requests.Session", return_value=session):
            network.update()

    def test_coordinate_correction_is_per_record(self):
        self.assertEqual(corrected_coordinates(self.roster[0]), (6.147648, -75.39029))
        self.assertEqual(corrected_coordinates(self.roster[1]), (6.156, -75.4012))
        self.assertIsNone(corrected_coordinates(self.roster[-1]))

    def test_complete_snapshot_and_availability_follow_official_website(self):
        network = BiciRio("bicirio-rionegro", META)
        client = FakeSession(self.fixtures)
        self.fake_update(network, client)
        self.assertEqual(len(network.stations), 4)
        by_id = {x.extra["uid"]: x for x in network.stations}
        self.assertEqual(set(by_id), {"21", "22", "36", "37"})
        self.assertEqual(by_id["21"].bikes, 1)
        self.assertEqual(by_id["22"].bikes, 2)
        self.assertIsNone(by_id["22"].free)
        self.assertEqual(by_id["22"].longitude, -75.4012)
        self.assertTrue(by_id["21"].extra["online"])
        self.assertFalse(by_id["36"].extra["online"])
        self.assertFalse(by_id["37"].extra["online"])
        self.assertEqual(len(client.calls), 5)
        for url, settings in client.calls:
            self.assertEqual(settings["verify"], str(self.bundle))
            self.assertFalse(settings["allow_redirects"])
            self.assertTrue(settings["stream"])
            self.assertNotIn("Authorization", settings["headers"])
            self.assertTrue(url.startswith("https://bicirio.somosmovilidad.gov.co/api/v1/free_access/"))
        self.assertNotIn("private-id", str([x.to_dict() for x in network.stations]))
        self.assertNotIn("private-serial", str([x.to_dict() for x in network.stations]))

    def test_stable_station_ids_do_not_depend_on_location(self):
        a = BiciRioStation(latitude=6.1, longitude=-75.2, extra={"uid": "21"})
        b = BiciRioStation(latitude=6.1, longitude=-75.2, extra={"uid": "22"})
        self.assertNotEqual(a.get_hash(), b.get_hash())
        self.assertEqual(a.get_hash(), BiciRioStation(extra={"uid": "21"}).get_hash())

    def test_rejects_unknown_state_and_does_not_publish_partial_snapshot(self):
        network = BiciRio("bicirio-rionegro", META)
        marker = object()
        network.stations = [marker]
        fixtures = dict(self.fixtures)
        fixtures[BICYCLES_URL_PREFIX + "22"] = [{"bicycleState": "Broken"}]
        with self.assertRaisesRegex(ValueError, "Unverified BiciRio bicycleState"):
            self.fake_update(network, FakeSession(fixtures))
        self.assertEqual(network.stations, [marker])

    def test_api_failure_keeps_previous_snapshot(self):
        network = BiciRio("bicirio-rionegro", META)
        old = network.stations
        with self.assertRaisesRegex(ConnectionError, "Simulated"):
            self.fake_update(network, FakeSession(self.fixtures, fail_path=BICYCLES_URL_PREFIX + "22"))
        self.assertIs(network.stations, old)

    def test_missing_bundle_fails_closed(self):
        os.environ["BICIRIO_CA_BUNDLE"] = "/not/a/real/path"
        network = BiciRio("bicirio-rionegro", META)
        with self.assertRaisesRegex(RuntimeError, "TLS CA bundle missing"):
            self.fake_update(network, FakeSession(self.fixtures))

    def test_rejects_html_and_http_errors(self):
        session = FakeSession({
            STATIONS_URL: FakeResponse(STATIONS_URL, b"<html>nope</html>", content_type="text/html")
        })
        with self.assertRaisesRegex(ValueError, "did not return JSON"):
            BiciRio._json(session, STATIONS_URL)
        session = FakeSession({
            STATIONS_URL: FakeResponse(STATIONS_URL, b'{"error":"no"}', status=403),
        })
        with self.assertRaisesRegex(Exception, "403"):
            BiciRio._json(session, STATIONS_URL)

    def test_rejects_arbitrary_paths_and_large_responses(self):
        client = FakeSession({})
        with self.assertRaisesRegex(ValueError, "Unexpected BiciRio URL"):
            BiciRio._json(client, "https://evil.test/")
        big = "[" + (" " * 260000) + "]"
        with self.assertRaisesRegex(ValueError, "response size limit"):
            BiciRio._json(FakeSession({STATIONS_URL: big.encode()}), STATIONS_URL)

    def test_duplicate_ids_and_oversized_roster_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate BiciRio station ID"):
            BiciRio._eligible([self.roster[0], self.roster[0]])
        with self.assertRaisesRegex(ValueError, "Unexpectedly large"):
            BiciRio._eligible([self.roster[0]] * 41)

    def test_unknown_state_is_not_renting(self):
        unusual = station(25, "Unknown", -75.35, 6.155, state="Mystery")
        obj = BiciRio._station(unusual, (6.155, -75.35), [])
        self.assertFalse(obj.extra["online"])
        self.assertEqual(obj.bikes, 0)

    def test_no_fabricated_free_docks(self):
        obj = BiciRio._station(self.roster[0], (6.147648, -75.39029),
                              [{"bicycleState": "Ready"}])
        self.assertIsNone(obj.free)
        self.assertIsNone(obj.extra["slots"])


if __name__ == "__main__":
    unittest.main()
