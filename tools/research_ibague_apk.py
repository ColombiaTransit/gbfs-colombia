#!/usr/bin/env python3
"""Reproducible, read-only source inspection for the Rueda por Ibagué APK.

Works only with a public APK distribution page or a separately provided
APK file. Does not execute the app, sign in, request private endpoints,
make API calls to the app backend or read user data.
"""
from __future__ import annotations
import argparse
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
from zipfile import ZipFile, BadZipFile

PACKAGE = "com.ruedaxibaguex"
SOURCE = "https://rueda-por-ibague.uptodown.com/android/descargar"
OLD_SHA = "291e3e82032c4f0a759b7fc3ce67f7499ae3de1191fa117da9eda6b7fb3711cc"
ALLOWED_DOWNLOAD_HOSTS = {
    "dw.uptodown.com", "dw.uptodown.net", "cdn.uptodown.com",
    "rueda-por-ibague.uptodown.com", "dw.uptodown.net",
    "stc.utdstc.com", "dw.uptodown.com", "cdn.utdstc.com",
}
MAX_PAGE = 1_000_000
MAX_APK = 90_000_000
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ColombiaTransit research)",
           "Accept": "text/html,application/vnd.android.package-archive,*/*"}
OUTPUT = Path("ibague-apk-analysis.json")

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("a", "button", "form", "script"):
            self.links.append((tag, a))

def safe_url(raw):
    p = urlparse(raw)
    if p.scheme not in {"http", "https"} or not p.hostname:
        return ""
    # Do not include tokenized path/query in public logs.
    return p.scheme + "://" + p.hostname

def get_html():
    with urlopen(Request(SOURCE, headers=HEADERS), timeout=25) as r:
        body = r.read(MAX_PAGE + 1)
        if len(body) > MAX_PAGE:
            raise ValueError("HTML exceeds size limit")
        return body.decode("utf-8", "replace")

def candidates_from_html(html):
    parser = LinkParser()
    parser.feed(html)
    candidates = set()
    diagnostics = []
    for tag, attrs in parser.links:
        s = " ".join(map(str, attrs.values())).lower()
        if any(word in s for word in ("download", "apk", "file", "mirror", "dw.")):
            safe_attrs = {k: str(v)[:95] for k,v in attrs.items()
                          if k in {"id", "class", "rel", "type", "name", "method",
                                   "data-id", "data-version", "data-file-id",
                                   "data-type"}}
            diagnostics.append({"tag": tag, "attrs": safe_attrs})
        for key, val in attrs.items():
            if not isinstance(val, str):
                continue
            if key.lower() in ("href","action","data-url","data-href",
                               "data-download-url","data-link","data-download"):
                url = urljoin(SOURCE, val.replace("&amp;", "&"))
                if urlparse(url).hostname in ALLOWED_DOWNLOAD_HOSTS and (
                    "download" in url.lower() or "dwn" in url.lower()
                    or url.endswith((".apk", ".xapk"))
                ):
                    candidates.add(url)
    for raw in re.findall(r"https?:(?:\\?/){2}[^\\s\"'<>]{8,400}", html):
        url = raw.replace("\\/", "/").replace("&amp;", "&").rstrip("),;")
        if urlparse(url).hostname in ALLOWED_DOWNLOAD_HOSTS and (
            "/dwn/" in url or url.endswith((".apk",".xapk"))
        ):
            candidates.add(url)
    return sorted(candidates), diagnostics[:20]

def download_candidate(url, dest):
    host = urlparse(url).hostname
    if host not in ALLOWED_DOWNLOAD_HOSTS:
        raise ValueError("Blocked untrusted download host")
    req = Request(url, headers=HEADERS)
    with urlopen(req, timeout=50) as resp:
        final_host = urlparse(resp.url).hostname
        # Binary CDNs may redirect to another Uptodown-owned domain.
        if final_host not in ALLOWED_DOWNLOAD_HOSTS and not (
            final_host and (final_host.endswith(".uptodown.net") or
                            final_host.endswith(".uptodown.com") or
                            final_host.endswith(".utdstc.com"))):
            raise ValueError("Redirect to unknown download domain")
        ctype = resp.headers.get("Content-Type","")
        prefix = resp.read(4)
        if prefix != b"PK\x03\x04":
            raise ValueError("Not a ZIP/APK (content type " + ctype[:50] + ")")
        size = 4
        h = hashlib.sha256(prefix)
        with dest.open("wb") as out:
            out.write(prefix)
            while True:
                chunk = resp.read(1024*1024)
                if not chunk:
                    break
                size += len(chunk)
                if size > MAX_APK:
                    raise ValueError("APK exceeds size limit")
                out.write(chunk); h.update(chunk)
    return {"sha256":h.hexdigest(), "bytes":size,
            "source_host":host, "final_host":final_host}

def inspect(apk, acquisition):
    result={"package_expected": PACKAGE, "source": SOURCE,
            "expected_old_version_sha256": OLD_SHA,
            "acquisition": acquisition, "status":"analysis_complete",
            "urls":[],"interesting_paths":[],
            "files":[],"notes":[]}
    if acquisition["sha256"] != OLD_SHA:
        result["notes"].append("SHA256 differs from historical Uptodown 1.0.9; validate package and version before trusting findings")
    else:
        result["notes"].append("Matches known Uptodown 1.0.9 SHA256 (22 July 2025), NOT the current 2026 Play Store version")
    paths=set()
    urls=set()
    with ZipFile(apk) as z:
        names=z.namelist()
        dex=[n for n in names if re.fullmatch(r"classes(\d*)\.dex",n)]
        result["files"]=[{"name":n,"size":z.getinfo(n).file_size} for n in dex]
        for name in dex:
            data=z.read(name)
            if len(data)>65_000_000:
                raise ValueError("DEX exceeds scan limit")
            for raw in re.findall(rb"https?://[a-zA-Z0-9.-]+(?::[0-9]+)?(?:/[-a-zA-Z0-9_./{}%?&=+]{0,250})?",data):
                s=raw.decode("ascii","ignore")
                if any(k in s.lower() for k in (
                    "ibague", "infibague", "bicic", "station","estaci",
                    "/api/", "/v1", "/v2", "/get", "/public", "rueda"
                )):
                    # Strict removal of any query string or embedded secrets
                    p=urlparse(s)
                    path=p.path[:140]
                    if not re.search(r"(token|secret|pass|auth|key)",path,re.I):
                        urls.add(p.scheme+"://"+p.netloc+path)
            for raw in re.findall(rb"/(?:api|v1|v2|estacion|station|bicicleta|bicycles|bikes|vehiculo|vehicle)[a-zA-Z0-9/_{}.-]{1,120}",data,re.I):
                s=raw.decode("ascii","ignore")
                if not re.search(r"(token|secret|password|user|email|auth|login)",s,re.I):
                    paths.add(s)
    result["urls"]=sorted(urls)[:70]
    result["interesting_paths"]=sorted(paths)[:100]
    if not result["urls"] and not result["interesting_paths"]:
        result["notes"].append("Static DEX strings yielded no suitable public availability API; JADX/string-resource review may be required")
    return result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--apk", help="Optional already downloaded APK path")
    args=parser.parse_args()
    report={"status":"started","package_expected":PACKAGE,
            "source":SOURCE,"play_store_release":"2026-07-31",
            "mirror_version":"1.0.9 (2025-07-22)",
            "notes":["Research only; never scrape authenticated user APIs"]}
    apk=Path(args.apk) if args.apk else Path("/tmp/rueda-por-ibague.apk")
    if args.apk and apk.exists():
        report=inspect(apk,{"sha256":hashlib.sha256(apk.read_bytes()).hexdigest(),
                            "bytes":apk.stat().st_size, "source_host":"user_supplied"})
    else:
        try:
            html=get_html()
            candidates, diagnostics=candidates_from_html(html)
            report["page_bytes"]=len(html)
            report["candidate_download_hosts"]=sorted({urlparse(x).hostname for x in candidates})
            report["candidate_count"]=len(candidates)
            report["html_download_element_signals"]=diagnostics
            print("Uptodown HTML bytes:",len(html))
            print("Download candidates:",len(candidates),"hosts:",report["candidate_download_hosts"])
            print("Download-related HTML signals:",json.dumps(diagnostics,ensure_ascii=False)[:4000])
            attempts=[]
            for url in candidates[:6]:
                try:
                    acquisition=download_candidate(url,apk)
                    report=inspect(apk,acquisition)
                    break
                except Exception as exc:
                    attempts.append({"host":urlparse(url).hostname, "error_type":type(exc).__name__,
                                     "error":str(exc)[:100]})
            else:
                report["status"]="apk_not_acquired"
                report["download_attempts"]=attempts
                report["notes"].append("No independently verified APK acquired; never claim analysis of latest Play Store APK")
        except Exception as exc:
            report["status"]="page_error"
            report["error_type"]=type(exc).__name__
            report["error"]=str(exc)[:180]
    OUTPUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print("RESULT:",report["status"])
    print("Candidate URLs:",json.dumps(report.get("urls",[]),ensure_ascii=False))
    print("Candidate paths:",json.dumps(report.get("interesting_paths",[]),ensure_ascii=False))
    print("Artifact:",OUTPUT)
    # A missing public APK is an investigative outcome, not a CI code failure.
    return 0

if __name__=="__main__":
    raise SystemExit(main())
