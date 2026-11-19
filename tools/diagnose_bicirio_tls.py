#!/usr/bin/env python3
"""Diagnose certificate-chain presentation on the PUBLIC BiciRio HTTPS host.

Read-only TLS handshakes and HEAD; no login, no API contents, no credentials,
no insecure fallback. Findings are diagnostic and not used for GBFS feeds.
"""
import os
import re
import socket
import ssl
import subprocess

HOST = "bicirio.somosmovilidad.gov.co"

def check_python():
    context = ssl.create_default_context()
    print("PYTHON_OPENSSL", ssl.OPENSSL_VERSION, flush=True)
    print("PYTHON_CA_CERTS", context.cert_store_stats(), flush=True)
    try:
        with socket.create_connection((HOST, 443), timeout=12) as conn:
            with context.wrap_socket(conn, server_hostname=HOST) as tls:
                cert = tls.getpeercert()
                print("PYTHON_TLS_VERIFY", "PASS", tls.version(), flush=True)
                print("PYTHON_CERT_SUBJECT", cert.get("subject"), flush=True)
                print("PYTHON_CERT_ISSUER", cert.get("issuer"), flush=True)
    except ssl.SSLCertVerificationError as exc:
        print("PYTHON_TLS_VERIFY", "FAIL", "verify_code=", exc.verify_code,
              "reason=", exc.verify_message, flush=True)
    except OSError as exc:
        print("PYTHON_TLS_CONNECT", "ERROR", type(exc).__name__, str(exc)[:180], flush=True)

def check_openssl():
    cmd = ["openssl", "s_client", "-connect", HOST + ":443", "-servername", HOST,
           "-showcerts", "-verify", "5", "-verify_return_error"]
    try:
        result = subprocess.run(cmd, input="", capture_output=True,
                                text=True, timeout=22, check=False)
    except Exception as exc:
        print("OPENSSL_ERROR", type(exc).__name__, str(exc)[:150], flush=True)
        return
    combined = result.stdout + "\n" + result.stderr
    count = len(re.findall(r"-----BEGIN CERTIFICATE-----", combined))
    print("OPENSSL_EXIT_CODE", result.returncode)
    print("OPENSSL_PRESENTED_CERTIFICATES", count)
    for line in combined.splitlines():
        line = line.strip()
        if (line.startswith(("depth=", "verify error:", "Verification error:",
                             "Verify return code:", "subject=", "issuer=", "notBefore=",
                             "notAfter=", "Certificate chain")) or
            re.match(r"^\d+\s+s:", line) or
            re.match(r"^i:", line)):
            print("OPENSSL_CHAIN_DETAIL", line[:250])

def check_curl():
    result = subprocess.run(["curl", "--head", "--silent", "--show-error",
                             "--max-time", "12",
                             "https://" + HOST + "/"],
                            capture_output=True, text=True, check=False, timeout=17)
    print("CURL_EXIT_CODE", result.returncode)
    # Do not expose arbitrary response cookies or headers.
    for line in result.stderr.splitlines():
        if any(t in line.lower() for t in ("certificate", "ssl", "issuer", "curl:")):
            print("CURL_TLS_DETAIL", line[:200])

if __name__ == "__main__":
    print("RUNNER_IMAGE", os.environ.get("ImageOS"), os.environ.get("ImageVersion"))
    check_python()
    check_openssl()
    check_curl()
