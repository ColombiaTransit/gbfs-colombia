import json
import tempfile
import unittest
from pathlib import Path

from colombia_gbfs.registry import activate, enabled_networks, load_registry

REPO_REGISTRY = Path(__file__).resolve().parents[1] / "config" / "scrapers.json"


def plugin_entry(**overrides):
    entry = {
        "tag": "test-bikes",
        "module": "example_adapter",
        "class": "ExampleAdapter",
        "meta": {
            "name": "Test bikes", "city": "Test city", "country": "CO",
            "latitude": 4.0, "longitude": -74.0, "company": ["Test operator"],
        },
    }
    entry.update(overrides)
    return entry


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self.addCleanup(self._dir.cleanup)

    def registry(self, entries):
        """Write a throwaway registry so tests never depend on config/."""
        path = Path(self._dir.name) / "registry.json"
        path.write_text(json.dumps(entries), encoding="utf-8")
        return path

    def test_default_networks(self):
        self.assertEqual(enabled_networks("encicla,tembici-bogota"),
                         ["encicla", "tembici-bogota"])

    def test_reject_duplicate_networks(self):
        with self.assertRaises(ValueError):
            enabled_networks("encicla,encicla")

    def test_upstream_networks_are_colombian(self):
        records = activate(["encicla", "tembici-bogota"], self.registry([]))
        self.assertEqual({instance["tag"] for _, _, instance in records},
                         {"encicla", "tembici-bogota"})
        from pybikes import get
        self.assertEqual(get("encicla").tag, "encicla")
        self.assertEqual(get("tembici-bogota").tag, "tembici-bogota")

    def test_plugin_registration(self):
        records = activate(["test-bikes"], self.registry([plugin_entry()]))
        self.assertEqual(records[0][0], "colombia_example_adapter")
        from pybikes import get
        network = get("test-bikes")
        self.assertEqual(network.tag, "test-bikes")
        self.assertEqual(network.meta["company"], ["Test operator"])

    def test_plugin_requires_company_list(self):
        for company in (None, "Operator", [1]):
            entry = plugin_entry()
            if company is None:
                del entry["meta"]["company"]
            else:
                entry["meta"]["company"] = company
            with self.subTest(company=company), \
                    self.assertRaisesRegex(ValueError, "meta.company"):
                load_registry(self.registry([entry]))

    def test_plugin_requires_colombia(self):
        entry = plugin_entry()
        entry["meta"]["country"] = "ES"
        with self.assertRaisesRegex(ValueError, "country=CO"):
            load_registry(self.registry([entry]))

    def test_reject_custom_tag_colliding_with_upstream(self):
        with self.assertRaisesRegex(ValueError, "collide.*encicla"):
            activate(["test-bikes"], self.registry([plugin_entry(tag="encicla")]))

    def test_reject_non_colombia_network(self):
        with self.assertRaisesRegex(ValueError, "non-Colombian"):
            activate(["bicing"], self.registry([]))

    def test_reject_unknown_network(self):
        with self.assertRaisesRegex(ValueError, "Unknown Colombian network"):
            activate(["not-configured"], self.registry([]))

    def test_repository_registry_is_valid(self):
        # Whatever is committed in config/scrapers.json must load and must
        # activate cleanly alongside the default upstream networks.
        entries = load_registry(REPO_REGISTRY)
        tags = ["encicla", "tembici-bogota"] + [entry["tag"] for entry in entries]
        activate(tags, REPO_REGISTRY)


if __name__ == "__main__":
    unittest.main()
