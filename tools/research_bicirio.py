#!/usr/bin/env python3
"""Inspect only public BiciRio pages and same-origin JavaScript references.

No account requests, form submissions, credentials, authenticated endpoints,
private APIs, arbitrary API brute-force, or per-user data are accessed.
"""
from html.parser import HTMLParser
import json
import re
import os
import ssl
import socket
import urllib.error
import urllib.parse
import urllib.request

SITES = [
    "https://somosmovilidad.gov.co/sistema-de-bicicletas-bicirio/",
    "https://bicirio.somosmovilidad.gov.co/",
    "https://bicirio.somosmovilidad.gov.co/login",
    "https://bicirio.somosmovilidad.gov.co/register",
    "https://bicirio.somosmovilidad.gov.co/stations",
    # Explicit public routes present in the official frontend's no-auth list:
    "https://bicirio.somosmovilidad.gov.co/free_access/stations/get_all",
    "https://bicirio.somosmovilidad.gov.co/free_access/bicycles/get_all_by_station",
    "https://somosmovilidad.gov.co/somos-mapa/leaflet-routing-machine-3.2.12/examples/index.html",
]
DOMAINS = {"somosmovilidad.gov.co", "bicirio.somosmovilidad.gov.co"}
HEADERS = {
    "User-Agent": "ColombiaTransit-GBFS-Research/1.0 (public-asset-discovery)",
    "Accept": "text/html,application/javascript,text/javascript,*/*",
}
MAX_BYTES = 1_800_000
MAX_ASSETS_PER_HOST = 10
MAX_TOTAL_ASSETS = 16
ROUTE_PATTERN = re.compile(
    r"""(?:"|')((?:/api/|/api|/stations?|/estaciones|/bicicletas|/disponibilidad)
        [A-Za-z0-9_./-]{0,100})(?:"|')""", re.X | re.I
)
URL_PATTERN = re.compile(r"""https?:(?:\\?/){2}[A-Za-z0-9._:/?&=%-]{5,180}""")
KEYWORDS = ("bicirio", "station", "estacion", "bicicletas", "disponib",
            "puntoslibres", "capacidad", "api", "mapa", "leaflet")


class PublicAssets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.assets = []
        self.iframes = []
        self.title = ""
        self._title = False

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "script" and d.get("src"):
            self.assets.append(d["src"])
        if tag == "iframe" and d.get("src"):
            self.iframes.append(d["src"])
        if tag == "title":
            self._title = True

    def handle_data(self, data):
        if self._title:
            self.title += data

    def handle_endtag(self, tag):
        if tag == "title":
            self._title = False


def display_safe(url):
    parts = urllib.parse.urlsplit(url.replace("\\/", "/"))
    if parts.hostname not in DOMAINS:
        return ""
    # Purposely discard query strings, fragments and userinfo.
    return f"{parts.scheme}://{parts.hostname}{parts.path[:160]}"


def get(url):
    if urllib.parse.urlsplit(url).hostname not in DOMAINS:
        raise ValueError("Only explicitly approved official public origins")
    request = urllib.request.Request(url, headers=HEADERS)
    try:
        response = urllib.request.urlopen(request, timeout=12)
    except urllib.error.URLError as exc:
        # Public GET-only research workaround for the operator's broken
        # certificate chain. Never use this for real requests, user input,
        # authentication, production scrapers, or GBFS distribution.
        host = urllib.parse.urlsplit(url).hostname
        allow_research = os.getenv("BICIRIO_PUBLIC_RESEARCH_TLS_FALLBACK") == "1"
        if not (allow_research and host == "bicirio.somosmovilidad.gov.co"
                and "CERTIFICATE_VERIFY_FAILED" in str(exc)):
            raise
        print("  WARNING: cert verification failed; isolated PUBLIC-ASSET"
              " research fallback only; response content is UNTRUSTED")
        context = ssl._create_unverified_context()
        response = urllib.request.urlopen(request, timeout=12, context=context)
    with response:
        data = response.read(MAX_BYTES+1)
        if len(data) > MAX_BYTES:
            raise ValueError("public asset size limit exceeded")
        return response.status, response.url, response.headers.get("Content-Type", ""), data.decode("utf-8", errors="replace")


def summarize(url, content):
    counts = {word: len(re.findall(re.escape(word), content, re.I))
              for word in KEYWORDS if re.search(re.escape(word), content, re.I)}
    print("  relevant terms", counts)
    candidates = sorted(set(
        safe for match in URL_PATTERN.finditer(content)
        if (safe := display_safe(match.group())) and
        any(term in safe.lower() for term in ("bicirio", "api", "mapa", "estacion"))
    ))
    print("  official URL references", candidates[:20])
    paths = sorted(set(ROUTE_PATTERN.findall(content)))
    print("  literal API/station path candidates", paths[:40])
    if url.endswith(".js") and "bicirio.somosmovilidad.gov.co" in url:
        hosts = set()
        for match in URL_PATTERN.finditer(content):
            parsed = urllib.parse.urlsplit(match.group().replace("\\/", "/"))
            if parsed.scheme in ("http", "https") and parsed.hostname:
                hosts.add(parsed.hostname)
        print("  JS referenced hosts (not requested)", sorted(hosts)[:40])
        for term in ("/stations", "API_URL", "apiUrl", "baseUrl", "baseURL",
                     "api/", "http://", "https://", "estaciones", "bicicletas"):
            hints = []
            for found in list(re.finditer(re.escape(term), content, re.I))[:4]:
                nearby = content[max(0, found.start()-90):found.end()+105]
                # Strictly remove long possible API keys and all URI query data.
                nearby = re.sub(r"[A-Za-z0-9_-]{30,}", "[redacted]", nearby)
                nearby = re.sub(r"https?://[^\\s'\";]+", "[absolute URL]", nearby)
                nearby = re.sub(r"\\s+", " ", nearby)
                hints.append(nearby[:180])
            if hints:
                print("  JS code context", term, hints)


def main():
    seen_assets = set()
    per_host = {}
    print("BiciRio public HTML and static-JS inspection; no auth, no user data.")
    for url in SITES:
        try:
            code, actual, ctype, body = get(url)
            print("PAGE", display_safe(url), "status", code,
                  "bytes", len(body), "type", ctype, "final", display_safe(actual))
            if "json" in ctype.lower():
                try:
                    result = json.loads(body)
                    if isinstance(result, dict):
                        print("  JSON top-level keys", sorted(result.keys())[:35])
                        for key, val in list(result.items())[:10]:
                            if isinstance(val, list):
                                print("  JSON list", key, "length", len(val),
                                      "first record keys", sorted(val[0].keys())[:30]
                                      if val and isinstance(val[0], dict) else [])
                    elif isinstance(result, list):
                        print("  JSON array length", len(result),
                              "first record keys", sorted(result[0].keys())[:30]
                              if result and isinstance(result[0], dict) else [])
                    else:
                        print("  JSON value type", type(result).__name__)
                except ValueError:
                    print("  JSON decode failed")
            if "html" in ctype.lower() or "<html" in body[:2000].lower():
                h = PublicAssets()
                h.feed(body)
                print("  title", repr(h.title[:110]))
                print("  linked iframes", [display_safe(urllib.parse.urljoin(actual, v))
                                           for v in h.iframes][:10])
                for v in h.assets:
                    src = urllib.parse.urljoin(actual, v)
                    host = urllib.parse.urlsplit(src).hostname
                    path = urllib.parse.urlsplit(src).path.lower()
                    if host in DOMAINS and path.endswith(".js"):
                        if per_host.get(host, 0) < MAX_ASSETS_PER_HOST:
                            seen_assets.add(src)
                            per_host[host] = per_host.get(host, 0) + 1
                print("  discovered JS", len(h.assets))
                print("  JS references", [display_safe(urllib.parse.urljoin(actual, v))
                                          for v in h.assets if display_safe(
                                          urllib.parse.urljoin(actual, v))][:25])
            summarize(url, body)
        except urllib.error.HTTPError as exc:
            print("PAGE", display_safe(url), "HTTP", exc.code)
        except (OSError, socket.timeout, urllib.error.URLError, ValueError) as exc:
            print("PAGE", display_safe(url), "ERROR", type(exc).__name__, str(exc)[:110])

    for asset in sorted(seen_assets)[:MAX_TOTAL_ASSETS]:
        try:
            code, final, ctype, body = get(asset)
            print("SCRIPT", display_safe(asset), "status", code,
                  "bytes", len(body), "type", ctype)
            summarize(asset, body)
        except urllib.error.HTTPError as exc:
            print("SCRIPT", display_safe(asset), "HTTP", exc.code)
        except (OSError, socket.timeout, urllib.error.URLError, ValueError) as exc:
            print("SCRIPT", display_safe(asset), "ERROR",
                  type(exc).__name__, str(exc)[:110])


if __name__ == "__main__":
    main()
