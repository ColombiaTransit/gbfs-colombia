"""Optional EnCicla Azure relay while preserving upstream PyBikes station parsing.

Enabled only when ENCICLA_PROXY_URL and ENCICLA_FUNCTION_KEY are both set.
No retry, cache, or fallback to the blocked direct upstream endpoint.
"""
import json
import os
from urllib.parse import urlsplit

import requests
from pybikes.encicla import Encicla, FEED_URL

MAX_BYTES = 1024 * 1024
DEFAULT_PROXY_HOST = "func-encicla-probe.azurewebsites.net"


def proxy_settings():
    url = os.environ.get("ENCICLA_PROXY_URL", "").strip()
    key = os.environ.get("ENCICLA_FUNCTION_KEY", "").strip()
    if not url and not key:
        return None
    if not url or not key:
        raise ValueError("EnCicla proxy requires both ENCICLA_PROXY_URL and ENCICLA_FUNCTION_KEY")
    parts = urlsplit(url)
    # Host can be customized for a renamed Azure Function App, but not redirected
    # to arbitrary third-party hosts. Never send the Function Key over HTTP.
    if (parts.scheme != "https" or not parts.hostname
            or not parts.hostname.endswith(".azurewebsites.net")
            or parts.username is not None or parts.password is not None
            or parts.port not in (None, 443)
            or parts.path != "/api/encicla-data"
            or parts.query or parts.fragment):
        raise ValueError("ENCICLA_PROXY_URL must be HTTPS Azure Functions /api/encicla-data")
    return url, key


class EnCiclaProxyScraper:
    """Minimal PyBikesScraper-compatible request interface for upstream Encicla."""

    def __init__(self, url, key):
        self.url = url
        self.key = key

    def request(self, url, **kwargs):
        if url != FEED_URL:
            raise ValueError("Only the official EnCicla feed may be relayed")
        with requests.Session() as session:
            # Ignore HTTP_PROXY/HTTPS_PROXY configured for other services.
            session.trust_env = False
            with session.get(
                self.url,
                headers={
                    "x-functions-key": self.key,
                    "Accept": "application/json",
                    "User-Agent": "ColombiaTransit-GBFS/1.0",
                },
                timeout=15,
                allow_redirects=False,
                stream=True,
            ) as response:
                if response.status_code != 200:
                    # Do not include headers, URL, or key in an exception.
                    raise RuntimeError("EnCicla Azure proxy HTTP " + str(response.status_code))
                if "json" not in response.headers.get("Content-Type", "").lower():
                    raise ValueError("EnCicla Azure proxy returned non-JSON response")
                if int(response.headers.get("Content-Length") or "0") > MAX_BYTES:
                    raise ValueError("EnCicla Azure proxy response too large")
                chunks = []
                length = 0
                for chunk in response.iter_content(chunk_size=16384):
                    length += len(chunk)
                    if length > MAX_BYTES:
                        raise ValueError("EnCicla Azure proxy response too large")
                    chunks.append(chunk)
        raw = b"".join(chunks)
        try:
            data = json.loads(raw)
        except (ValueError, UnicodeDecodeError):
            raise ValueError("EnCicla Azure proxy returned invalid JSON") from None
        if not isinstance(data, list):
            raise ValueError("EnCicla Azure proxy expected station array")
        return raw.decode("utf-8")


class EnciclaProxy(Encicla):
    """Keep the upstream Encicla class and metadata; replace only its transport."""

    def update(self, scraper=None):
        settings = proxy_settings()
        if settings is None:
            return super().update(scraper=scraper)
        return super().update(scraper=EnCiclaProxyScraper(*settings))
