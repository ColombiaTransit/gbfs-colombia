"""EnCicla-only Azure relay transport tests; never make live HTTP requests."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from colombia_gbfs.scrapers.encicla_proxy import (
    EnCiclaProxyScraper, EnciclaProxy, proxy_settings,
)
from colombia_gbfs.registry import activate
from pybikes.encicla import FEED_URL

URL = "https://func-encicla-probe.azurewebsites.net/api/encicla-data"
KEY = "not-a-real-function-key"


class FakeResponse:
    status_code = 200
    url = URL
    headers = {"Content-Type": "application/json"}
    def __init__(self, payload):
        self.payload = payload
    def __enter__(self):
        return self
    def __exit__(self, *_):
        return False
    def iter_content(self, chunk_size):
        for p in range(0, len(self.payload), chunk_size):
            yield self.payload[p:p + chunk_size]


class TestEnCiclaProxy(unittest.TestCase):
    def settings(self):
        return patch.dict(os.environ, {
            "ENCICLA_PROXY_URL": URL,
            "ENCICLA_FUNCTION_KEY": KEY,
        })

    def test_disabled_by_default(self):
        with patch.dict(os.environ, {"ENCICLA_PROXY_URL": "", "ENCICLA_FUNCTION_KEY": ""}):
            self.assertIsNone(proxy_settings())

    def test_incomplete_config_fails_closed(self):
        with patch.dict(os.environ, {"ENCICLA_PROXY_URL": URL, "ENCICLA_FUNCTION_KEY": ""}):
            with self.assertRaises(ValueError):
                proxy_settings()

    def test_rejects_non_azure_or_insecure_endpoint(self):
        for url in ("http://func-encicla-probe.azurewebsites.net/api/encicla-data",
                    "https://example.com/api/encicla-data",
                    URL + "?code=secret",
                    "https://func-encicla-probe.azurewebsites.net/api/other"):
            with self.subTest(url=url), patch.dict(os.environ, {
                "ENCICLA_PROXY_URL": url, "ENCICLA_FUNCTION_KEY": KEY
            }):
                with self.assertRaises(ValueError):
                    proxy_settings()

    def test_preserves_original_station_data(self):
        record = {
            "cdo": "0", "name": "Estacion prueba", "lon": -75.57,
            "lat": 6.25, "bikes": 3, "capacity": 10,
            "id": 123, "address": "Calle 1", "description": "Prueba",
            "closed": "0",
        }
        with self.settings(), patch("requests.Session.get", return_value=FakeResponse(
            json.dumps([record]).encode("utf-8")
        )) as get:
            station_system = EnciclaProxy("encicla", {"country": "CO"})
            station_system.update()
        self.assertEqual(len(station_system.stations), 1)
        station = station_system.stations[0]
        self.assertEqual(station.name, "Estacion prueba")
        self.assertEqual(station.bikes, 3)
        self.assertEqual(station.free, 7)
        self.assertEqual(station.extra["uid"], 123)
        self.assertEqual(get.call_args.args, (URL,))
        self.assertEqual(get.call_args.kwargs["headers"]["x-functions-key"], KEY)
        self.assertFalse(get.call_args.kwargs["allow_redirects"])

    def test_failed_upstream_preserves_previous_snapshot(self):
        with self.settings(), patch("requests.Session.get", return_value=FakeResponse(b'<html>blocked</html>')):
            station_system = EnciclaProxy("encicla", {"country": "CO"})
            station_system.stations = ["existing"]
            with self.assertRaises(ValueError):
                station_system.update()
        self.assertEqual(station_system.stations, ["existing"])

    def test_rejects_unexpected_target(self):
        with self.assertRaises(ValueError):
            EnCiclaProxyScraper(URL, KEY).request("https://unrelated.example/api")

    def test_registry_switch_isolated_to_encicla(self):
        with tempfile.TemporaryDirectory() as directory:
            registry_path = Path(directory) / "scrapers.json"
            registry_path.write_text("[]", encoding="utf-8")
            with self.settings():
                records = activate(["encicla", "tembici-bogota"], registry_path)
                selected = {record["tag"]: (module, cls)
                            for module, cls, record in records}
                self.assertEqual(selected["encicla"],
                                 ("colombia_encicla_proxy", "EnciclaProxy"))
                self.assertNotEqual(selected["tembici-bogota"][0],
                                    "colombia_encicla_proxy")


if __name__ == "__main__":
    unittest.main()
