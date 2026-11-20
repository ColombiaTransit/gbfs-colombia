#!/usr/bin/env python3
"""Compare direct and Tor access to the public EnCicla availability endpoint.

Only sends one request per route; does not write API response bodies to artifacts.
"""
import argparse
import datetime as dt
import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import requests

TOR_PROXY = "socks5h://127.0.0.1:9050"
TOR_PROXIES = {"http": TOR_PROXY, "https": TOR_PROXY}


def session(tor=False):
    s = requests.Session()
    s.trust_env = False
    s.headers.update({"User-Agent": "Mozilla/5.0 (compatible; ColombiaTransit-EnCicla-Diagnostic/1.0)", "Accept": "application/json, text/plain, */*"})
    if tor:
        s.proxies.update(TOR_PROXIES)
    return s


def request_summary(s, url, timeout):
    start = time.monotonic()
    try:
        response = s.get(url, timeout=timeout, allow_redirects=False)
        result = {
            "http_status": response.status_code,
            "content_type": response.headers.get("Content-Type", ""),
            "elapsed_ms": round((time.monotonic() - start) * 1000),
            "bytes_received": len(response.content),
            "final_host": urlparse(response.url).hostname,
            "redirect_host": urlparse(response.headers.get("Location", "")).hostname,
        }
        try:
            obj = response.json()
            result["valid_json"] = True
            result["json_type"] = type(obj).__name__
            if isinstance(obj, list):
                result["records"] = len(obj)
            elif isinstance(obj, dict):
                result["top_level_keys"] = sorted(str(k) for k in obj.keys())[:25]
                # Recognize common EnCicla response wrappers without asserting success.
                for key in ("data", "Data", "result", "Result", "stations", "Estaciones"):
                    if isinstance(obj.get(key), list):
                        result["records"] = len(obj[key])
                        break
        except ValueError:
            result["valid_json"] = False
        result["data_received"] = bool(response.ok and result.get("valid_json") and (result.get("records", 0) > 0 or result.get("json_type") == "dict"))
        return result
    except requests.RequestException as exc:
        return {"error_type": type(exc).__name__, "elapsed_ms": round((time.monotonic() - start) * 1000)}


def exit_info(s, timeout):
    try:
        r = s.get("https://ipwho.is/", timeout=timeout)
        r.raise_for_status()
        body = r.json()
        if not body.get("success", False):
            return {"error": "geoip_lookup_failed"}
        return {"ip": body.get("ip"), "country_code": body.get("country_code"), "country": body.get("country")}
    except (requests.RequestException, ValueError):
        return {"error": "geoip_unavailable"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=os.getenv("ENCICLA_PROBE_URL", ""))
    parser.add_argument("--output", default="artifacts/encicla-tor-probe.json")
    parser.add_argument("--timeout", type=int, default=25)
    args = parser.parse_args()
    parsed = urlparse(args.url)
    if parsed.scheme != "https" or parsed.hostname != "webapp.metropol.gov.co":
        parser.error("ENCICLA_PROBE_URL must be an HTTPS URL on webapp.metropol.gov.co (full GetDisponibilidadMapas URL)")
    report = {"checked_at": dt.datetime.now(dt.timezone.utc).isoformat(), "endpoint_host": parsed.hostname, "endpoint_path": parsed.path, "tests": {}}
    for label, use_tor in [("direct", False), ("tor", True)]:
        s = session(use_tor)
        report["tests"][label] = {"exit": exit_info(s, args.timeout), "upstream": request_summary(s, args.url, args.timeout)}
        s.close()
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    direct = report["tests"]["direct"]["upstream"]
    tor = report["tests"]["tor"]["upstream"]
    if tor.get("data_received"):
        print("RESULT: TOR_RETURNED_JSON; inspect records and shape.")
    elif direct.get("data_received"):
        print("RESULT: DIRECT_RETURNED_JSON; Tor did not improve access.")
    else:
        print("RESULT: NO_CONFIRMED_DATA; check status, GeoIP and connection errors.")
    return 0  # diagnostics are never a build failure due to upstream availability


if __name__ == "__main__":
    sys.exit(main())
