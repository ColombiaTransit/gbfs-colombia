#!/usr/bin/env python3
"""Inspect only public BiciRio frontend JavaScript for bicycleState mapping.

No authenticated calls, scripts executed or vehicle/user records collected.
Print limited sanitized snippets of publicly served code, never bike IDs.
"""
import os
import re

from tools.research_bicirio import get

PUBLIC_BUNDLES = (
    "https://bicirio.somosmovilidad.gov.co/main-YSAWJGXJ.js",
    "https://bicirio.somosmovilidad.gov.co/chunk-LJOODKNY.js",
)
LOOK_FOR = re.compile(
    r"bicycleState|bikeState|BICYCLE_STATE|estadoBicicleta|bicycle_state|"
    r"disponible|noDisponible|enMantenimiento|enPrestamo",
    re.IGNORECASE,
)

def scrub(text):
    text = re.sub(r"https?://[^\s'\"]{20,}", "[absolute-url]", text)
    text = re.sub(r"[A-Za-z0-9_-]{48,}", "[redacted-long-string]", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:380]

def main():
    assert os.environ.get("BICIRIO_PUBLIC_RESEARCH_TLS_FALLBACK") == "1"
    print("Inspect public static JS only; never publish credentials or bicycle identifiers.")
    for url in PUBLIC_BUNDLES:
        print("BUNDLE", url)
        try:
            status, final, ctype, body = get(url)
            if status != 200 or "javascript" not in ctype.lower():
                print("  unexpected response", status, ctype[:80])
                continue
            hits = list(LOOK_FOR.finditer(body))
            print("  code_size", len(body), "status_reference_count", len(hits))
            for index, found in enumerate(hits[:18], start=1):
                print("  PUBLIC_JS_CONTEXT", index, scrub(body[max(0, found.start()-150):found.end()+200]))
        except Exception as exc:
            print("  ERROR", type(exc).__name__, str(exc)[:120])

if __name__ == "__main__":
    main()
