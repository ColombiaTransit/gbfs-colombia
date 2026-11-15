"""GBFS 3.0 API with Colombian timezone, attribution and network isolation."""
import os
from contextlib import asynccontextmanager
from functools import wraps

from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.responses import PlainTextResponse
from starlette.routing import Mount, Route

from citybikes.db.asyncio import CBD, get_session, migrate
from citybikes.gbfs.versions.v3.api import Gbfs as UpstreamGbfs3
from colombia_gbfs.registry import enabled_networks

ALLOWED = set(enabled_networks())
DB_URI = os.getenv("DB_URI", "/data/citybikes.db")


class ColombiaGbfs3(UpstreamGbfs3):
    def route_decorator(self, handler):
        original = super().route_decorator(handler)

        @wraps(original)
        async def restricted(request):
            uid = request.path_params.get("uid")
            if uid and uid not in ALLOWED:
                raise HTTPException(status_code=404)
            return await original(request)

        return restricted

    async def system_information(self, request, db, uid):
        contact = os.getenv("GBFS_CONTACT_EMAIL", "").strip()
        if not contact or "@" not in contact:
            raise HTTPException(
                status_code=503,
                detail="Set GBFS_CONTACT_EMAIL to a monitored address before publishing GBFS",
            )
        info = await super().system_information(request, db, uid)
        hours_key = "GBFS_OPENING_HOURS_" + uid.upper().replace("-", "_")
        hours = (os.getenv(hours_key)
                 or os.getenv("GBFS_OPENING_HOURS")
                 or "24/7 unknown")
        # OSM opening_hours 'unknown' explicitly conveys that hours have
        # not yet been verified; it must not be mistaken for 24/7 service.
        # Do not claim ColombiaTransit operates the bicycles. The operator
        # field retains the original provider identity.
        return info.model_copy(update={
            "timezone": "America/Bogota",
            "opening_hours": hours,
            "feed_contact_email": contact,
            "attribution_organization_name": "ColombiaTransit",
            "attribution_url": "https://github.com/ColombiaTransit/gbfs-colombia",
        })

    async def manifest(self, request, db):
        manifest = await super().manifest(request, db)
        datasets = [d for d in manifest.datasets if d.system_id in ALLOWED]
        return manifest.model_copy(update={"datasets": datasets})


@asynccontextmanager
async def lifespan(app):
    async with get_session(DB_URI) as db:
        if not await migrate(db):
            raise RuntimeError("Could not migrate GBFS SQLite database")
        app.db = CBD(db)
        app.VERSIONS = [ColombiaGbfs3.GBFS.version]
        yield


app = Starlette(
    lifespan=lifespan,
    routes=[
        Mount("/3", routes=ColombiaGbfs3().routes),
        Route("/", lambda request: PlainTextResponse(
            "ColombiaTransit GBFS 3.0 | /3/manifest.json\n")),
        Route("/healthz", lambda request: PlainTextResponse("ok\n")),
    ],
)
