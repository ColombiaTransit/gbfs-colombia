"""End-to-end checks of the GBFS 3.0 API against a seeded SQLite database."""
import asyncio
import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

_TMP = tempfile.TemporaryDirectory()
DB_PATH = str(Path(_TMP.name) / "citybikes.db")
# colombia_gbfs.api reads these at import time.
os.environ["DB_URI"] = DB_PATH
os.environ["ENABLED_NETWORKS"] = "encicla"

from citybikes.cmd.subscriber import Sqlitesubscriber  # noqa: E402
from citybikes.db import migrate  # noqa: E402

from colombia_gbfs.api import app, lifespan  # noqa: E402


def seed(tag, company):
    con = sqlite3.connect(DB_PATH)
    con.row_factory = lambda *a: dict(sqlite3.Row(*a))
    assert migrate(con)
    meta = {"name": tag, "city": "Medellín", "country": "CO",
            "latitude": 6.2443, "longitude": -75.5735, "company": company}
    station = {"id": f"{tag}-1", "name": "Estación", "latitude": 6.25,
               "longitude": -75.57, "bikes": 3, "free": 5,
               "timestamp": "2026-01-01T00:00:00Z", "extra": {"uid": "1"}}
    Sqlitesubscriber(con, "tcp://unused", "").handle_message(
        "network", json.dumps({"tag": tag, "meta": meta,
                               "stations": [station], "vehicles": []}))
    con.close()


async def get(path, headers=()):
    """Minimal ASGI GET, so the image needs no extra HTTP test client."""
    scope = {
        "type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1",
        "method": "GET", "scheme": "http", "path": path,
        "raw_path": path.encode(), "root_path": "", "query_string": b"",
        "headers": [(b"host", b"gbfs-colombia:8000"), *headers],
        "server": ("gbfs-colombia", 8000), "client": ("127.0.0.1", 1),
    }
    sent = []

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        sent.append(message)

    await app(scope, receive, send)
    status = next(m["status"] for m in sent if m["type"] == "http.response.start")
    body = b"".join(m.get("body", b"") for m in sent if m["type"] == "http.response.body")
    return status, body


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        seed("encicla", ["Sistema de Bicicletas Públicas del Valle de Aburrá"])
        seed("bicing", ["Not Colombian"])  # stored, but not enabled

    def request(self, path, env=None):
        async def run():
            async with lifespan(app):
                return await get(path)

        saved = {key: os.environ.get(key) for key in (env or {})}
        os.environ.update(env or {})
        try:
            return asyncio.run(run())
        finally:
            for key, value in saved.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    def test_system_information_is_gbfs3_compliant(self):
        status, body = self.request("/3/encicla/system_information.json",
                                    {"GBFS_CONTACT_EMAIL": "ops@example.org"})
        self.assertEqual(status, 200)
        data = json.loads(body)["data"]
        localized = {"name", "short_name", "operator", "attribution_organization_name"}
        for field in localized:
            with self.subTest(field=field):
                self.assertIsInstance(data[field], list)
                for item in data[field]:
                    self.assertEqual(set(item), {"language", "text"})
                    self.assertIn(item["language"], data["languages"])
        self.assertEqual(data["attribution_organization_name"][0]["text"], "ColombiaTransit")
        self.assertEqual(data["timezone"], "America/Bogota")
        self.assertEqual(data["feed_contact_email"], "ops@example.org")
        self.assertEqual(data["opening_hours"], "24/7 unknown")

    def test_per_network_opening_hours(self):
        status, body = self.request("/3/encicla/system_information.json",
                                    {"GBFS_CONTACT_EMAIL": "ops@example.org",
                                     "GBFS_OPENING_HOURS_ENCICLA": "Mo-Sa 05:30-22:00"})
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["data"]["opening_hours"], "Mo-Sa 05:30-22:00")

    def test_missing_contact_email_is_503(self):
        status, _ = self.request("/3/encicla/system_information.json",
                                 {"GBFS_CONTACT_EMAIL": ""})
        self.assertEqual(status, 503)

    def test_disabled_network_is_hidden(self):
        self.assertEqual(self.request("/3/bicing/gbfs.json")[0], 404)
        status, body = self.request("/3/manifest.json")
        self.assertEqual(status, 200)
        ids = [d["system_id"] for d in json.loads(body)["data"]["datasets"]]
        self.assertEqual(ids, ["encicla"])

    def test_station_status(self):
        status, body = self.request("/3/encicla/station_status.json")
        self.assertEqual(status, 200)
        stations = json.loads(body)["data"]["stations"]
        self.assertEqual(len(stations), 1)
        self.assertEqual(stations[0]["num_vehicles_available"], 3)


if __name__ == "__main__":
    unittest.main()
