import json
import tempfile
import unittest
from pathlib import Path

from colombia_gbfs.registry import activate, enabled_networks, load_registry


class RegistryTests(unittest.TestCase):
    def test_default_networks(self):
        self.assertEqual(enabled_networks("encicla,tembici-bogota"),
                         ["encicla", "tembici-bogota"])

    def test_reject_duplicate_networks(self):
        with self.assertRaises(ValueError):
            enabled_networks("encicla,encicla")

    def test_upstream_networks_are_colombian(self):
        records = activate(["encicla", "tembici-bogota"],
                           "/app/config/scrapers.json")
        self.assertEqual({instance["tag"] for _, _, instance in records},
                         {"encicla", "tembici-bogota"})
        from pybikes import get
        self.assertEqual(get("encicla").tag, "encicla")
        self.assertEqual(get("tembici-bogota").tag, "tembici-bogota")

    def test_plugin_registration(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "registry.json"
            path.write_text(json.dumps([{
                "tag": "test-bikes",
                "module": "example_adapter",
                "class": "ExampleAdapter",
                "meta": {
                    "name": "Test bikes", "city": "Test city",
                    "country": "CO", "latitude": 4.0, "longitude": -74.0
                }
            }]), encoding="utf-8")
            records = activate(["test-bikes"], path)
            self.assertEqual(records[0][0], "colombia_example_adapter")
            from pybikes import get
            self.assertEqual(get("test-bikes").tag, "test-bikes")

    def test_reject_non_colombia_network(self):
        with self.assertRaisesRegex(ValueError, "non-Colombian"):
            activate(["bicing"], "/app/config/scrapers.json")

    def test_reject_unknown_network(self):
        with self.assertRaisesRegex(ValueError, "Unknown Colombian network"):
            activate(["not-configured"], "/app/config/scrapers.json")

    def test_registry_is_empty_initially(self):
        self.assertEqual(load_registry("/app/config/scrapers.json"), [])


if __name__ == "__main__":
    unittest.main()
