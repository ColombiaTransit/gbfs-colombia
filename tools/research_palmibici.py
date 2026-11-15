#!/usr/bin/env python3
"""Public-asset-only discovery for PalmiBici PWA.

This script downloads only HTML and same-origin static JS from the officially
linked PWA. It never attempts authentication, user registration, user API calls,
private Firestore paths or requests to newly discovered hosts.

Output includes only metadata and scrubbed endpoint candidates, not JS contents.
"""
import html.parser
import re
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://palmibici-pwa.web.app/"
HEADERS = {"User-Agent": "ColombiaTransit-GBFS-research/1.0 (+https://github.com/ColombiaTransit/gbfs-colombia)"}
PAGES = ("", "register", "information")
MAX_BYTES = 5_000_000
MAX_JS = 12
URL_RE = re.compile(r"https?:(?:\\?/){2}[A-Za-z0-9_.:/?&=%\-]+")
ROUTE_RE = re.compile(r"/(?:api|v1|v2|v3|stations?|bicicletas?|bikes?|disponibilidad|availability|estaciones)[A-Za-z0-9_/?\-]{0,140}", re.I)
KEYWORDS = ("station", "estacion", "bicicl", "disponib", "availability", "bikes", "firebase", "firestore", "graphql", "axios", "baseurl")


class HTMLAssets(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = set()
        self.links = set()
        self.title = False
        self.title_text = ""

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script" and attrs.get("src"):
            self.scripts.add(attrs["src"])
        if tag == "link" and attrs.get("href"):
            self.links.add(attrs["href"])
        if tag == "title":
            self.title = True

    def handle_data(self, data):
        if self.title:
            self.title_text += data

    def handle_endtag(self, tag):
        if tag == "title":
            self.title = False


def fetch(url):
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=18) as response:
        size = 0
        chunks = []
        while size < MAX_BYTES:
            piece = response.read(min(131072, MAX_BYTES-size))
            if not piece:
                break
            size += len(piece)
            chunks.append(piece)
        return response.status, response.url, b"".join(chunks).decode("utf-8", "replace")


def scrub(url):
    """Never report query credentials or fragments."""
    url = url.replace("\\/", "/")
    p = urllib.parse.urlsplit(url)
    if not p.scheme or not p.netloc:
        return ""
    # Exclude any user-info, queries and fragments.
    return p.scheme + "://" + (p.hostname or "") + (p.path[:180] or "/")


def main():
    scripts = set()
    print("Palmibici public PWA static-asset discovery; no authentication.")
    for page in PAGES:
        url = urllib.parse.urljoin(BASE, page)
        try:
            status, resolved, content = fetch(url)
            parser = HTMLAssets()
            parser.feed(content)
            print("PAGE", page or "/", "status", status,
                  "bytes", len(content), "title", repr(parser.title_text[:100]))
            for script in sorted(parser.scripts):
                target = urllib.parse.urljoin(BASE, script)
                if urllib.parse.urlsplit(target).hostname == "palmibici-pwa.web.app":
                    scripts.add(target)
            print("  scripts", len(parser.scripts), "same-origin", len(scripts))
            print("  links", len(parser.links))
        except (TimeoutError, OSError, urllib.error.URLError) as exc:
            print("PAGE", page or "/", "ERROR", type(exc).__name__, str(exc)[:150])

    print("SAME-ORIGIN SCRIPTS (maximum %d)" % MAX_JS)
    for url in sorted(scripts)[:MAX_JS]:
        try:
            status, resolved, body = fetch(url)
            print("SCRIPT", scrub(url), "status", status, "bytes", len(body))
            print("  keyword_counts", {word: len(re.findall(re.escape(word), body, re.I))
                                      for word in KEYWORDS if re.search(re.escape(word), body, re.I)})
            found_urls = {scrub(match.group()) for match in URL_RE.finditer(body)}
            # limit output to likely data-service URLs; skip common third-party docs.
            matches = sorted(x for x in found_urls if x and any(
                word in x.lower() for word in ("api", "firebase", "firestore", "palmibici", "station",
                                               "bici", "imscorp", "ims.com", "graphql")))
            print("  public URL references:", *matches[:60], sep="\n    ")
            routes = sorted(set(ROUTE_RE.findall(body)))
            print("  route candidate strings:", *routes[:60], sep="\n    ")
            # Inspect only short string literals (paths and labels) associated
            # with API and station terminology; no user data or auth calls.
            interesting = ("estacion", "station", "bicicl", "disponib",
                           "api", "baseurl", "endpoint", "palmibici")
            tokens = set()
            for m in re.finditer(r"""(["'])([^"'\\\n]{1,150})\1""", body):
                candidate = m.group(2)
                low = candidate.lower()
                if any(word in low for word in interesting):
                    if any(secret in low for secret in
                           ("password", "token=", "secret", "bearer", "authorization")):
                        continue
                    if "?" in candidate:
                        candidate = candidate.split("?", 1)[0]
                    if len(candidate) <= 125 and all(ord(ch) >= 32 for ch in candidate):
                        tokens.add(candidate)
            print("  matching static string literals:", *sorted(tokens)[:90],
                  sep="\n    ")
        except (TimeoutError, OSError, urllib.error.URLError) as exc:
            print("SCRIPT", scrub(url), "ERROR", type(exc).__name__, str(exc)[:150])


if __name__ == "__main__":
    main()
