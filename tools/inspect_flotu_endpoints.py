#!/usr/bin/env python3
"""Inventory endpoint-like strings in the exact public Flotu JavaScript bundles.

STATIC FILE ANALYSIS ONLY: no API requests, login, customer/vehicle queries,
credentials, or response data. Output only short, sanitized path literals,
never full arbitrary JS snippets, cookies, tokens, or configuration secrets.
"""
import collections
import json
import re
from urllib.parse import urlsplit

from tools.research_flotu import load

BUNDLES = {
    "marketing": "https://flotu.com/_components/v2/063be6fa5f4d16053ad380e52e6be66c9ee71bef.js",
    "admin": "https://app.flotu.com/main.605db60a5b2b7808.js",
}
MAX_SOURCE_BYTES = 3_000_000
MAX_LITERAL = 260
API_WORDS = re.compile(
    r"api|vehicle|vehic|bicicl|bicycle|bike|scooter|station|estacion|"
    r"booking|reserve|reservation|rental|rent|alquil|loan|trip|ride|"
    r"fleet|flota|customer|client|user|auth|login|session|catalog|"
    r"tariff|pricing|category|categor|location|zone|map|geo|city|"
    r"payment|register|checkin|checkout|device|lock|ride|operator",
    re.I,
)
METHOD_CALL = re.compile(r"\.\s*(get|post|put|patch|delete|request)\s*\(\s*$", re.I)
URL = re.compile(r"https?://[^\s\"'\x60<>]{1,200}", re.I)
PATH = re.compile(r"^/(?:[a-z0-9_{}$-]+)(?:[/?.][\w{}$./?=&-]*)?$", re.I)
ROUTE = re.compile(r"route[s]?|path\s*:|loadChildren|component", re.I)

def literals(source):
    """Minimal bounded JS string lexer; does not execute JS."""
    i, end = 0, len(source)
    while i < end:
        quote = source[i]
        if quote not in ("'", '"', "\x60"):
            i += 1
            continue
        start = i
        i += 1
        data = []
        while i < end:
            c = source[i]
            if c == "\\":
                if len(data) <= MAX_LITERAL:
                    data.append(source[i:i+2])
                i += 2
                continue
            if c == quote:
                break
            if len(data) <= MAX_LITERAL:
                data.append(c)
            i += 1
        if i < end:
            i += 1
        if len(data) <= MAX_LITERAL and i-start <= MAX_LITERAL+4:
            yield start, quote, "".join(data)

def safe_literal(value):
    value = value.replace("\\/", "/").strip()
    # Do not print query strings, credentials or tokens.
    if len(value) > 195 or any(c in value for c in ("\n","\r","@",";"," ","\\\\")):
        return None
    if value.startswith(("http://","https://")):
        p = urlsplit(value)
        if p.username or p.password or not p.hostname:
            return None
        if not API_WORDS.search(p.path) and p.hostname not in {"app.flotu.com", "api.flotu.com"}:
            return None
        if p.query or p.fragment:
            return None
        return f"{p.scheme}://{p.hostname}{p.path}"
    if value.startswith("/") and PATH.fullmatch(value):
        if API_WORDS.search(value):
            return value
    return None

def lookup_hint(source, start):
    pre = source[max(0,start-180):start]
    call = METHOD_CALL.search(pre)
    if call:
        return "http_method_candidate:" + call.group(1).upper()
    if re.search(r"\bpath\s*:\s*$", pre[-30:]):
        return "frontend_route_candidate"
    if re.search(r"\b(?:baseUrl|apiUrl|API_URI|_baseUrl)\s*[:=]\s*$", pre[-45:], re.I):
        return "api_base_assignment"
    if re.search(r"\b(?:loadComponent|loadChildren)\s*[:=]", pre[-100:], re.I):
        return "frontend_route_context"
    return "other_literal"

def main():
    for label, url in BUNDLES.items():
        status, actual, ctype, js = load(url)
        if status != 200 or urlsplit(actual).hostname != urlsplit(url).hostname:
            raise RuntimeError("Unexpected JS asset response")
        if len(js) > MAX_SOURCE_BYTES or "javascript" not in ctype.lower():
            raise RuntimeError("Unexpected JS content")
        hits = collections.defaultdict(set)
        total_literals = 0
        for pos, _, literal in literals(js):
            total_literals += 1
            safe = safe_literal(literal)
            if safe:
                hits[safe].add(lookup_hint(js, pos))
        print("BUNDLE", label, url)
        print("BYTES", len(js), "EXAMINED_JS_LITERALS", total_literals,
              "ENDPOINT_LIKE_UNIQUE", len(hits))
        for path, hints in sorted(hits.items()):
            print("REFERENCE", label, json.dumps({"literal": path,
                  "contexts": sorted(hints)}, ensure_ascii=False))
        # Detect dynamic service construction patterns without displaying JS:
        for pattern in (
            r"\.\s*(?:get|post|put|patch|delete)\s*\(\s*\x60/",
            r"\.\s*(?:get|post|put|patch|delete)\s*\(\s*[\"']/",
            r"\b(?:baseURL|baseUrl|API_URI|apiUrl)\b",
        ):
            print("PATTERN_COUNT", label, pattern,
                  len(re.findall(pattern, js, re.I)))

if __name__ == "__main__":
    main()
