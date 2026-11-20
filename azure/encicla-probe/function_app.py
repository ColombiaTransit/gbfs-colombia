"""Authenticated HTTP-only diagnostic endpoint. No scheduled polling."""
import json
import logging
import azure.functions as func
from probe import run_probe

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
