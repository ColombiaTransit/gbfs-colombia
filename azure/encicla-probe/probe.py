"""Network-only EnCicla test. No GBFS publishing or response-data mirroring."""
import datetime
import json
import time
import urllib.error
import urllib.request

ENCICLA_URL = "https://webapp.metropol.gov.co/wsencicla/api/Disponibilidad/GetDisponibilidadMapas"
IP_URL = "https://api.ipify.org?format=json"
USER_AGENT = "ColombiaTransit-EnCicla-Azure-Connectivity-Probe/1.0"
MAX_BYTES = 1024 * 1024


def get_json(url, timeout=12):
    start = time.monotonic()
    request = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"}
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = response.status
            content_type = response.headers.get("Content-Type", "")
            payload = response.read(MAX_BYTES + 1)
    except urllib.error.HTTPError as error:
        status = error.code
        content_type = error.headers.get("Content-Type", "")
        payload = error.read(MAX_BYTES + 1)
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        return {
            "error_type": type(error).__name__,
            "elapsed_ms": round((time.monotonic() - start) * 1000),
        }

    result = {
        "http_status": status,
        "content_type": content_type,
        "elapsed_ms": round((time.monotonic() - start) * 1000),
        "bytes_received": len(payload),
    }
    if len(payload) > MAX_BYTES:
        result["error_type"] = "ResponseTooLarge"
        return result
    try:
        data = json.loads(payload)
        result["valid_json"] = True
        result["json_type"] = type(data).__name__
        if isinstance(data, list):
            result["records"] = len(data)
        elif isinstance(data, dict):
            result["top_level_keys"] = sorted(data.keys())[:15]
    except (ValueError, UnicodeDecodeError):
        result["valid_json"] = False
    return result


def run_probe():
    result = {
        "checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "target": "EnCicla GetDisponibilidadMapas",
        "azure_public_ip": None,
    }
    # IP check is supplementary; it must not prevent the EnCicla test.
    ip_result = get_json(IP_URL, timeout=4)
    if ip_result.get("http_status") == 200 and ip_result.get("valid_json"):
        # Separate public IP lookup avoids logging API response bodies.
        try:
            with urllib.request.urlopen(
                urllib.request.Request(IP_URL, headers={"User-Agent": USER_AGENT}),
                timeout=4,
            ) as response:
                value = json.load(response).get("ip")
                if isinstance(value, str):
                    result["azure_public_ip"] = value
        except (urllib.error.URLError, TimeoutError, OSError, ValueError):
            pass
    result["encicla"] = get_json(ENCICLA_URL, timeout=12)
    result["success"] = (
        result["encicla"].get("http_status") == 200
        and result["encicla"].get("valid_json") is True
        and result["encicla"].get("json_type") == "list"
        and result["encicla"].get("records", 0) > 0
    )
    return result
