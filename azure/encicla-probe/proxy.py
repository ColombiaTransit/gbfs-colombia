"""One-request-in, one-request-out EnCicla relay with no cache or persistence."""
import json
import urllib.error
import urllib.request

from probe import ENCICLA_URL, MAX_BYTES, USER_AGENT


class UpstreamError(Exception):
    def __init__(self, status, code):
        super().__init__(code)
        self.status = status
        self.code = code


def fetch_encicla_json(timeout=12):
    """Return original upstream JSON bytes; reject errors and malformed responses."""
    request = urllib.request.Request(
        ENCICLA_URL,
        headers={"Accept": "application/json", "User-Agent": USER_AGENT},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if response.status != 200:
                raise UpstreamError(502, "upstream_non_200")
            payload = response.read(MAX_BYTES + 1)
    except urllib.error.HTTPError:
        raise UpstreamError(502, "upstream_http_error") from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise UpstreamError(504, "upstream_unreachable") from None

    if len(payload) > MAX_BYTES:
        raise UpstreamError(502, "upstream_response_too_large")
    try:
        records = json.loads(payload)
    except (ValueError, UnicodeDecodeError):
        raise UpstreamError(502, "upstream_invalid_json") from None
    if not isinstance(records, list):
        raise UpstreamError(502, "upstream_unexpected_json_shape")
    # An empty list is legitimate and must not be replaced with stale data.
    return payload
