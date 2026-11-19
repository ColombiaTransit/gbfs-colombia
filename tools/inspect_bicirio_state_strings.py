#!/usr/bin/env python3
"""Compare public BiciRio frontend code with public per-station bicycle API.

Extract bounded, redacted code neighborhoods only. No credentials, login,
authenticated endpoints or bicycle identifiers are read or persisted.
"""
import os
import re

from tools.research_bicirio import get

PUBLIC_BUNDLES = (
    "https://bicirio.somosmovilidad.gov.co/main-YSAWJGXJ.js",
    "https://bicirio.somosmovilidad.gov.co/chunk-LJOODKNY.js",
)

PATTERNS = {
    "bicycleState": r"bicycleState|bicycle_state|bikeState|estadoBicicleta",
    "ready_literal": r"(?<![A-Za-z])Ready(?![A-Za-z])",
    "station_bike_count": r"bikeCount|availableBikes|bicicletas disponibles",
    "bicycle_endpoint": r"get_all_by_station|free_access/bicycles",
    "station_endpoint": r"free_access/stations|get_all(?:\W|$)",
    "station_state": r"getStyleForState|connectionState|On_Maintenance",
}

def scrub(text):
    text = re.sub(r"https?://[^\s'\"]{20,}", "[absolute-url]", text)
    text = re.sub(r"[A-Za-z0-9_-]{40,}", "[redacted-long-string]", text)
    text = re.sub(r"[\w.+-]+@[\w.-]+", "[redacted-email]", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def main():
    assert os.environ.get("BICIRIO_PUBLIC_RESEARCH_TLS_FALLBACK") == "1"
    print("Public frontend comparison only; no private API, bike IDs or rider data.")
    for url in PUBLIC_BUNDLES:
        print("BUNDLE", url)
        try:
            status, _, ctype, body = get(url)
            if status != 200 or "javascript" not in ctype.lower():
                print("  unexpected response", status, ctype[:80])
                continue
            print("  JS_BYTES", len(body))
            for name, expression in PATTERNS.items():
                matches = list(re.finditer(expression, body, re.I))
                print("  MATCH_COUNT", name, len(matches))
                for index, match in enumerate(matches[:5], 1):
                    start = max(0, match.start() - 850)
                    end = min(len(body), match.end() + 850)
                    print("  CODE_NEIGHBORHOOD", name, index,
                          scrub(body[start:end])[:1650])
        except Exception as exc:
            print("  ERROR", type(exc).__name__, str(exc)[:120])

if __name__ == "__main__":
    main()
