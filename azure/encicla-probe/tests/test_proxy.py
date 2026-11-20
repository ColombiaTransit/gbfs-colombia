"""Offline tests for the production relay; no Azure access or credentials."""
import json
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import proxy


class Response:
    status = 200

    def __init__(self, data):
        self.data = data

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, max_bytes):
        return self.data[:max_bytes]


class ProxyTest(unittest.TestCase):
    def test_preserves_original_json_exactly(self):
        raw = b' [ { "name": "Estacion", "bikes": 3 } ] \n'
        with patch.object(proxy.urllib.request, "urlopen", return_value=Response(raw)) as call:
            result = proxy.fetch_encicla_json()
        self.assertEqual(raw, result)
        self.assertEqual(call.call_args.kwargs["timeout"], 12)

    def test_allows_empty_list(self):
        with patch.object(proxy.urllib.request, "urlopen", return_value=Response(b"[]")):
            self.assertEqual(proxy.fetch_encicla_json(), b"[]")

    def test_rejects_html(self):
        with patch.object(proxy.urllib.request, "urlopen", return_value=Response(b"<html>403</html>")):
            with self.assertRaises(proxy.UpstreamError) as ctx:
                proxy.fetch_encicla_json()
        self.assertEqual(ctx.exception.status, 502)

    def test_rejects_non_list_json(self):
        with patch.object(proxy.urllib.request, "urlopen", return_value=Response(b'{"error":"x"}')):
            with self.assertRaises(proxy.UpstreamError) as ctx:
                proxy.fetch_encicla_json()
        self.assertEqual(ctx.exception.code, "upstream_unexpected_json_shape")

    def test_rejects_oversized_body(self):
        with patch.object(proxy.urllib.request, "urlopen", return_value=Response(b"[" + b" " * proxy.MAX_BYTES + b"]")):
            with self.assertRaises(proxy.UpstreamError) as ctx:
                proxy.fetch_encicla_json()
        self.assertEqual(ctx.exception.code, "upstream_response_too_large")

    def test_http_403_maps_to_502(self):
        exc = urllib.error.HTTPError(proxy.ENCICLA_URL, 403, "Forbidden", {}, None)
        with patch.object(proxy.urllib.request, "urlopen", side_effect=exc):
            with self.assertRaises(proxy.UpstreamError) as ctx:
                proxy.fetch_encicla_json()
        self.assertEqual(ctx.exception.status, 502)

    def test_timeout_maps_to_504(self):
        with patch.object(proxy.urllib.request, "urlopen", side_effect=TimeoutError()):
            with self.assertRaises(proxy.UpstreamError) as ctx:
                proxy.fetch_encicla_json()
        self.assertEqual(ctx.exception.status, 504)


if __name__ == "__main__":
    unittest.main()
