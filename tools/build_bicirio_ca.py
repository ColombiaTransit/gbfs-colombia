#!/usr/bin/env python3
"""Create a BiciRio-only Requests CA bundle without disabling TLS verification.

During the Docker image build, download GoDaddy G2 intermediate from GoDaddy's
official HTTPS repository, verify its SHA256 DER fingerprint, and append it
to certifi's root CA bundle. No changes to system-wide CA trust.
"""
import hashlib
import ssl
from pathlib import Path
from urllib.request import Request, urlopen

import certifi

INTERMEDIATE_URL = "https://certs.godaddy.com/repository/gdig2.crt.pem"
SHA256_DER = "973a41276ffd01e027a2aad49e34c37846d3e976ff6a620b6712e33832041aa6"
BUNDLE_PATH = Path("/opt/venv/bicirio-godaddy-ca.pem")
MAX_PEM_BYTES = 16000


def validated_intermediate(pem):
    if not isinstance(pem, bytes) or len(pem) > MAX_PEM_BYTES:
        raise ValueError("GoDaddy PEM file missing or too large")
    text = pem.decode("ascii")
    if text.count("-----BEGIN CERTIFICATE-----") != 1 or text.count("-----END CERTIFICATE-----") != 1:
        raise ValueError("Expected a single official GoDaddy intermediate")
    digest = hashlib.sha256(ssl.PEM_cert_to_DER_cert(text)).hexdigest()
    if digest != SHA256_DER:
        raise ValueError("Refusing GoDaddy CA certificate with unexpected fingerprint")
    return text.strip().encode("ascii")


def build_bundle(output=BUNDLE_PATH, fetch=None):
    if fetch is None:
        def fetch():
            req = Request(INTERMEDIATE_URL, headers={"User-Agent": "ColombiaTransit-GBFS-Build/1.0"})
            with urlopen(req, timeout=20) as response:  # HTTPS verification ON
                return response.read(MAX_PEM_BYTES + 1)

    intermediate = validated_intermediate(fetch())
    ca_roots = Path(certifi.where()).read_bytes()
    output = Path(output)
    output.write_bytes(ca_roots.rstrip() + b"\n" + intermediate + b"\n")
    return output


if __name__ == "__main__":
    print("Validated, host-specific GoDaddy intermediate bundle:", build_bundle())
