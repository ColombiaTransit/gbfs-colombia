"""Authenticated EnCicla connectivity probe and uncached JSON relay."""
import json
import logging
import azure.functions as func
from probe import run_probe
from proxy import UpstreamError, fetch_encicla_json

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.route(route="encicla-probe", methods=["GET"])
def encicla_probe(req: func.HttpRequest) -> func.HttpResponse:
    try:
        result = run_probe()
        logging.info("EnCicla Azure probe successful=%s", result["success"])
        return func.HttpResponse(
            json.dumps(result, ensure_ascii=False),
            status_code=200,
            mimetype="application/json",
            headers={"Cache-Control": "no-store"},
        )
    except Exception:
        logging.exception("EnCicla Azure probe failed unexpectedly")
        return func.HttpResponse(
            '{"error":"internal_probe_error"}',
            status_code=500,
            mimetype="application/json",
        )


@app.route(route="encicla-data", methods=["GET"], auth_level=func.AuthLevel.FUNCTION)
def encicla_data(req: func.HttpRequest) -> func.HttpResponse:
    """Return exact upstream JSON bytes; authentication is enforced by Functions host."""
    try:
        payload = fetch_encicla_json()
        return func.HttpResponse(
            body=payload,
            status_code=200,
            mimetype="application/json",
            headers={"Cache-Control": "no-store, max-age=0"},
        )
    except UpstreamError as exc:
        logging.warning("EnCicla relay upstream failure: %s", exc.code)
        return func.HttpResponse(
            json.dumps({"error": exc.code}),
            status_code=exc.status,
            mimetype="application/json",
            headers={"Cache-Control": "no-store"},
        )
    except Exception:
        logging.exception("EnCicla relay unexpected failure")
        return func.HttpResponse(
            '{"error":"internal_proxy_error"}',
            status_code=500,
            mimetype="application/json",
            headers={"Cache-Control": "no-store"},
        )
