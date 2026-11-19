#!/usr/bin/env python3
"""Research-only test of BiciRio's missing TLS intermediate without disabling TLS.

Pass a locally acquired GoDaddy PEM intermediate obtained over verified HTTPS.
No private API calls, credentials or personal/vehicle data are collected.
"""
import argparse
import hashlib
import json
import ssl
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

HOST = "bicirio.somosmovilidad.gov.co"
STATIONS_URL = f"https://{HOST}/api/v1/free_access/stations/get_all"
OFFICIAL_INTERMEDIATE = "https://certs.godaddy.com/repository/gdig2.crt.pem"
GO_DADDY_G2_SHA256 = "973a41276ffd01e027a2aad49e34c37846d3e976ff6a620b6712e33832041aa6"
MAX_BODY = 100_000


def validate_intermediate(contents):
    """Verify the *DER certificate fingerprint* against the official CA index."""
    if contents.count("-----BEGIN CERTIFICATE-----") != 1:
        raise ValueError("Expected exactly one GoDaddy intermediate PEM")
    der = ssl.PEM_cert_to_DER_cert(contents)
    digest = hashlib.sha256(der).hexdigest()
    if digest != GO_DADDY_G2_SHA256:
        raise ValueError("Intermediate fingerprint mismatch; refusing untrusted CA")
    return digest


def describe_error(exc):
    if isinstance(exc, ssl.SSLCertVerificationError):
        return {"error": "SSLCertVerificationError",
                "verify_code": exc.verify_code,
                "reason": exc.verify_message}
    return {"error": type(exc).__name__, "reason": str(exc)[:130]}


def python_check(context):
    req = Request(STATIONS_URL, headers={
        "Accept": "application/json", "User-Agent": "ColombiaTransit-GBFS-Research/1.0"
    })
    try:
        with urlopen(req, context=context, timeout=18) as response:
            if response.geturl() != STATIONS_URL:
                raise ValueError("Unexpected redirect")
            if "json" not in response.headers.get("content-type", "").lower():
                raise ValueError("Expected JSON response")
            data = response.read(MAX_BODY + 1)
            if len(data) > MAX_BODY:
                raise ValueError("Too large")
            items = json.loads(data)
            if not isinstance(items, list):
                raise ValueError("Expected station array")
            return {"verified": True, "http_status": response.status,
                    "station_count": len(items)}
    except Exception as exc:
        return {"verified": False, **describe_error(exc)}


def requests_check(pem):
    """Requests is used by PyBikes; create a per-request CA bundle."""
    import certifi
    import requests
    with tempfile.TemporaryDirectory(prefix="bicirio-tls-") as tmp:
        combined = Path(tmp) / "roots-plus-intermediate.pem"
        combined.write_bytes(
            Path(certifi.where()).read_bytes().rstrip() + b"\n" +
            pem.encode("ascii").strip() + b"\n"
        )
        try:
            response = requests.get(
                STATIONS_URL, verify=str(combined), timeout=18,
                headers={"Accept": "application/json",
                         "User-Agent": "ColombiaTransit-GBFS-Research/1.0"},
                allow_redirects=False
            )
            if response.status_code != 200:
                return {"verified": True, "http_status": response.status_code}
            if "json" not in response.headers.get("Content-Type", "").lower():
                return {"verified": True, "error": "unexpected_content_type"}
            data = response.json()
            return {"verified": True, "http_status": response.status_code,
                    "station_count": len(data) if isinstance(data, list) else None}
        except requests.exceptions.SSLError as exc:
            return {"verified": False, "error": "SSLError", "detail": str(exc)[:170]}
        except requests.exceptions.RequestException as exc:
            return {"verified": False, "error": type(exc).__name__, "detail": str(exc)[:170]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--intermediate", required=True)
    args = parser.parse_args()
    pem = Path(args.intermediate).read_text(encoding="ascii")
    print("OFFICIAL_INTERMEDIATE_URL", OFFICIAL_INTERMEDIATE)
    print("INTERMEDIATE_SHA256_DER", validate_intermediate(pem))
    print("PYTHON_DEFAULT", json.dumps(python_check(ssl.create_default_context())))
    augmented = ssl.create_default_context()
    augmented.load_verify_locations(cadata=pem)
    python_result = python_check(augmented)
    print("PYTHON_WITH_GODADDY_INTERMEDIATE", json.dumps(python_result))
    requests_result = requests_check(pem)
    print("REQUESTS_WITH_GODADDY_INTERMEDIATE", json.dumps(requests_result))
    # Both clients must verify HTTPS and receive valid JSON from the official host.
    if not python_result.get("verified") or not requests_result.get("verified"):
        raise SystemExit(1)
    if python_result.get("http_status") != 200 or requests_result.get("http_status") != 200:
        raise SystemExit(2)
    if not isinstance(python_result.get("station_count"), int) or not isinstance(requests_result.get("station_count"), int):
        raise SystemExit(3)


if __name__ == "__main__":
    main()
