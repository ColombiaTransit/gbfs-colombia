#!/usr/bin/env python3
"""Inspect public Flotu HTML and same-origin static JS without authentication.

Read-only public file retrieval; no account, reservation, private API,
fleet endpoint probing, keys or rider data are collected.
"""
from html.parser import HTMLParser
import re
import urllib.error
import urllib.parse
import urllib.request

PAGES = (
    "https://flotu.com/",
    "https://flotu.com/alquiler-vehiculos",
)
HOSTS = {"flotu.com", "www.flotu.com"}
HEADERS = {"User-Agent": "ColombiaTransit-GBFS-Research/1.0",
           "Accept": "text/html,application/javascript,*/*"}
MAX_DOWNLOAD = 3_000_000
MAX_ASSETS = 9
WORDS = ("station", "estacion", "vehicle", "vehiculo", "bicicl",
         "disponib", "availability", "scooter", "api", "mapa", "flotu", "graphql")
URL_PATTERN = re.compile(r"https?:(?:\\?/){2}[A-Za-z0-9_.:/?=&%-]+", re.I)
PATH_PATTERN = re.compile(r"""["'](\/(?:api|v[123]|stations?|vehicles?|bicicletas|availability|flotas)[\/a-zA-Z0-9_-]{0,130})["']""",re.I)

class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.assets = set()
        self.title = ""
        self.in_title = False
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "script" and d.get("src"):
            self.assets.add(d["src"])
        if tag == "link" and d.get("rel") in ("modulepreload", "preload") and d.get("href"):
            self.assets.add(d["href"])
        if tag == "title":
            self.in_title = True
    def handle_data(self, data):
        if self.in_title:
            self.title += data
    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

def clean(url):
    p = urllib.parse.urlsplit(url.replace("\\/", "/"))
    if p.scheme not in ("http","https") or not p.hostname:
        return ""
    return f"{p.scheme}://{p.hostname}{p.path[:120]}"

def load(url):
    hostname = urllib.parse.urlsplit(url).hostname
    if hostname not in HOSTS:
        raise ValueError("Only official public web-origin assets are allowed")
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=18) as resp:
        data = resp.read(MAX_DOWNLOAD + 1)
        if len(data) > MAX_DOWNLOAD:
            raise ValueError("static file over size limit")
        return resp.status, resp.url, resp.headers.get("Content-Type",""), data.decode("utf-8","replace")

def analyze(url, body):
    counts = {word: len(re.findall(re.escape(word),body,re.I))
              for word in WORDS if re.search(re.escape(word),body,re.I)}
    print("  keywords:", counts)
    endpoints = sorted(set(PATH_PATTERN.findall(body)))
    print("  static path references:", endpoints[:40])
    hosts = set()
    service_paths = set()
    for m in URL_PATTERN.finditer(body):
        p = urllib.parse.urlsplit(m.group().replace("\\/","/"))
        if p.scheme in ("http","https") and p.hostname:
            hosts.add(p.hostname)
            if any(w in p.path.lower() for w in
                   ("api","station","estacion","vehicle","bicicl","availability")):
                service_paths.add(clean(m.group()))
    print("  outbound hosts referenced (not requested):",sorted(hosts)[:45])
    print("  service-like references (queries removed):",sorted(service_paths)[:30])

def main():
    assets=set()
    print("Flotu public frontend asset research: no login, no vehicle-data calls")
    for url in PAGES:
        try:
            code, final, ctype, body = load(url)
            print("PAGE",clean(url),"HTTP",code,"bytes",len(body),"type",ctype)
            parsed = Parser()
            parsed.feed(body)
            print("  page title",repr(parsed.title[:100]))
            for raw in parsed.assets:
                target = urllib.parse.urljoin(final,raw)
                parsed_url = urllib.parse.urlsplit(target)
                if parsed_url.hostname in HOSTS and parsed_url.path.endswith((".js",".mjs")):
                    assets.add(target)
            print("  same-origin JS candidates",len(assets))
            analyze(url,body)
        except (OSError,urllib.error.URLError,ValueError) as exc:
            print("PAGE",clean(url),"ERROR",type(exc).__name__,str(exc)[:130])
    for url in sorted(assets)[:MAX_ASSETS]:
        try:
            code, _, ctype, body = load(url)
            print("SCRIPT",clean(url),"HTTP",code,"bytes",len(body),"type",ctype)
            analyze(url,body)
        except (OSError,urllib.error.URLError,ValueError) as exc:
            print("SCRIPT",clean(url),"ERROR",type(exc).__name__,str(exc)[:130])

if __name__ == "__main__":
    main()
