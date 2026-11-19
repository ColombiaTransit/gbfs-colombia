#!/usr/bin/env python3
"""Flotu public-JS auth analysis and unauthenticated status-only probe.

Examines only a publicly served JS bundle. The network probe uses GET
with stream=True, redirects disabled, no credentials/cookies, and does
not read response bodies or retain any inventory/customer records.
"""
import json
import re
from urllib.parse import urlsplit

import requests

BUNDLE = "https://app.flotu.com/main.605db60a5b2b7808.js"
ORIGIN = "https://app.flotu.com"
PUBLIC_REFERENCES = (
    "/api/v1/vehicles",
    "/api/v1/vehicles/",
    "/api/v1/vehicles/categories",
    "/api/v1/vehicles/categories/",
)
TIMEOUT = (8, 12)
MAX_JS_BYTES = 2_000_000


def static_inspection(source):
    groups = {
        "vehicle_route": r"(?<![\w])/vehicles(?:/categories)?",
        "authorization_header": r"authorization|x-access-token|x-auth-token",
        "bearer_header": r"bearer",
        "auth_interceptor": r"interceptor|httpinterceptor|intercept\(",
        "request_guard": r"canActivate|authGuard|routeGuard",
        "login_or_refresh": r"/auth/(?:login|refresh|token/refresh)",
        "session_storage": r"localStorage|sessionStorage|Cookies?",
        "request_methods": r"\.(?:get|post|put|patch|delete)\(",
    }
    for label, expression in groups.items():
        hits = list(re.finditer(expression, source, re.IGNORECASE))
        print("JS_SIGNAL", label, len(hits))

    # Nearby code of relevant, *public* static routing references only.
    # Emit modest snippets, removing long values (e.g. tokens and keys).
    for needle in ("/vehicles", "/vehicles/categories", "Authorization", "Bearer",
                   "HttpInterceptor", "withInterceptors", "canActivate"):
        hits = list(re.finditer(re.escape(needle), source, re.IGNORECASE))
        print("JS_REFERENCE", needle, "hits", len(hits))
        for n, hit in enumerate(hits[:3], 1):
            before = source[max(0, hit.start()-210):hit.start()]
            after = source[hit.end():min(len(source), hit.end()+290)]
            context = before + "[" + needle + "]" + after
            context = re.sub(r"https?://[^\s,;}\)'\"\x60]{16,}", "[URL]", context)
            context = re.sub(r"[a-zA-Z0-9_=-]{45,}", "[REDACTED]", context)
            context = re.sub(r"\s+", " ", context)
            print("JS_CONTEXT", needle, n, context[:530])


def probe():
    # The /vehicles and /vehicles/categories paths occur in public JS.
    # This probe does NOT attempt authentication and is status-only.
    for path in PUBLIC_REFERENCES:
        url = ORIGIN + path
        with requests.Session() as session:
            session.trust_env = True
            session.headers.update({
                "User-Agent": "ColombiaTransit-GBFS-Research/1.0",
                "Accept": "application/json",
                "Cache-Control": "no-cache",
            })
            for method in ("HEAD", "GET"):
                try:
                    # GET is streaming; do not read body, even for HTTP 200.
                    with session.request(method, url, timeout=TIMEOUT, stream=True,
                                         allow_redirects=False) as response:
                        location = response.headers.get("Location", "")
                        p = urlsplit(location)
                        loc_type = ("none" if not location else
                                    "same_origin" if (not p.netloc or p.netloc == "app.flotu.com")
                                    else "other_origin")
                        print("PROBE", json.dumps({
                            "method": method, "path": path,
                            "http_status": response.status_code,
                            "content_type": response.headers.get("Content-Type", "").split(";")[0][:65],
                            "www_authenticate_present": "WWW-Authenticate" in response.headers,
                            "location_kind": loc_type,
                            "location_path": p.path[:100] if loc_type == "same_origin" else "",
                            "body_read": False,
                        }))
                        # 200,401,403,404 enough to classify; 405 HEAD method mismatch -> GET.
                        if method == "HEAD" and response.status_code not in (405, 501):
                            # Still check GET since many single-page applications
                            # route HEAD independently from GET.
                            pass
                except requests.RequestException as exc:
                    print("PROBE_ERROR", method, path, type(exc).__name__, str(exc)[:120])


def main():
    r = requests.get(BUNDLE, timeout=TIMEOUT, allow_redirects=False)
    r.raise_for_status()
    if r.url != BUNDLE:
        raise RuntimeError("Unexpected JS bundle redirect")
    if len(r.content) > MAX_JS_BYTES:
        raise RuntimeError("Unexpectedly large JS bundle")
    if "javascript" not in r.headers.get("Content-Type", "").lower():
        raise RuntimeError("Unexpected content type")
    source = r.content.decode("utf-8", "replace")
    print("PUBLIC_STATIC_JS", BUNDLE, "bytes", len(r.content))
    static_inspection(source)
    probe()


if __name__ == "__main__":
    main()
