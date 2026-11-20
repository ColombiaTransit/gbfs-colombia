import unittest
from unittest.mock import patch
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import probe


class Response:
    status = 200
    headers = {"Content-Type": "application/json"}
    def __init__(self, content):
        self.content = content
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def read(self, n):
        return self.content[:n]


class TestProbe(unittest.TestCase):
    def test_en_cicla_records(self):
        with patch.object(probe.urllib.request, "urlopen", return_value=Response(b'[{"id":1},{"id":2}]')):
            value = probe.get_json(probe.ENCICLA_URL)
        self.assertEqual(value["http_status"], 200)
        self.assertEqual(value["records"], 2)
        self.assertTrue(value["valid_json"])

    def test_invalid_json_is_not_success(self):
        with patch.object(probe.urllib.request, "urlopen", return_value=Response(b'<html>blocked</html>')):
            value = probe.get_json(probe.ENCICLA_URL)
        self.assertFalse(value["valid_json"])

    def test_too_large(self):
        with patch.object(probe.urllib.request, "urlopen", return_value=Response(b'X' * (probe.MAX_BYTES + 1))):
            value = probe.get_json(probe.ENCICLA_URL)
        self.assertEqual(value["error_type"], "ResponseTooLarge")


if __name__ == "__main__":
    unittest.main()
