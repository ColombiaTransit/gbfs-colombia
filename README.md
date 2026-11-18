# GBFS Colombia

Colombia-only GBFS 3.0 feeds built with [PyBikes](https://github.com/eskerda/pybikes),
[CityBikes Hyper](https://github.com/citybikes/hyper), and
[CityBikes GBFS API](https://github.com/citybikes/gbfs-api).

The project initially enables **EnCicla** (Medellín / Valle de Aburrá) and
**Tembici Bogotá**, with an extension mechanism for additional Colombian
scrapers. It does not scrape or publish networks outside Colombia.

## Architecture

One GHCR image, four Compose services:

- `publisher`: periodically loads only enabled networks via PyBikes/Hyper
  and publishes updates over ZeroMQ.
- `subscriber`: stores those updates in the persistent SQLite database.
- `api`: serves GBFS **3.0**; only enabled network IDs are exposed.
- `migrate`: a one-shot database initialization/migration job.

No container publishes TCP ports on the Docker host. The `publisher`,
`subscriber`, and `migrate` services communicate only on their Compose
backend network. The `api` joins the predictably named bridge network
`gbfs-colombia-shared`, where it is reachable as `http://gbfs-colombia:8000`.
The `publisher` can still reach the upstream providers over the internet.
Traefik and OpenTripPlanner (OTP) can join this shared network from their
own Compose projects without conflicting with host ports. The database
persists in the `gbfs-data` named Docker volume.

## Quick start

```sh
git clone https://github.com/ColombiaTransit/gbfs-colombia.git
cd gbfs-colombia
cp .env.example .env
# Edit .env: set GBFS_CONTACT_EMAIL to a monitored address.
docker compose pull
docker compose up -d
docker compose ps
```

Once live provider updates have arrived, **from a container on the shared
Docker network** use:

- `http://gbfs-colombia:8000/3/manifest.json`
- `http://gbfs-colombia:8000/3/encicla/gbfs.json`
- `http://gbfs-colombia:8000/3/tembici-bogota/gbfs.json`
- `http://gbfs-colombia:8000/healthz` (API liveness only)

The host cannot access these URLs directly without joining the Docker
network or going through Traefik. To check liveness on the server:

```sh
docker compose exec -T api python -c 'import urllib.request; print(urllib.request.urlopen("http://127.0.0.1:8000/healthz").read().decode())'
```

### Traefik and OTP connectivity

This Compose stack automatically creates a shared bridge network named
`gbfs-colombia-shared`. In **each separate Traefik or OTP Compose project**
that must access the API, attach its service to that network, declaring:

```yaml
services:
  # Example: merge this into your existing Traefik or OTP service.
  otp:
    networks:
      - gbfs-shared

networks:
  gbfs-shared:
    external: true
    name: gbfs-colombia-shared
```

The example service name `otp` is illustrative; use your real service name.
The network must already exist, so start the GBFS stack first. To reuse a
name other than `gbfs-colombia-shared`, set `GBFS_SHARED_NETWORK` in
`.env`, and use the same name for the other Compose projects.

**Traefik routing is disabled by default** (`GBFS_TRAEFIK_ENABLED=false`).
Once Traefik has joined the shared network, set
`GBFS_TRAEFIK_HOST` to your public DNS hostname,
`GBFS_TRAEFIK_ENTRYPOINT` to its HTTPS entrypoint (default `websecure`),
and `GBFS_TRAEFIK_ENABLED=true`. Then run `docker compose up -d` to
apply the new labels. Traefik discovers port `8000` over the shared network,
not a host port. Ensure HTTPS and certificates are configured on Traefik.

OTP can fetch EnCicla and Tembici GBFS directly using the two URLs above.
The exact updater configuration depends on your OTP version.

**Data freshness is not guaranteed by the health endpoint.** Check
`last_updated`, provider availability, and logs before advertising feeds.
The initial GBFS outputs depend on the live upstream endpoints being reachable.
GBFS 3.0 requires a monitored `feed_contact_email` and
`opening_hours`. Until `GBFS_CONTACT_EMAIL` is provided,
`system_information.json` returns HTTP 503 instead of inventing a contact.
The initial `24/7 unknown` opening_hours expression explicitly indicates
unverified hours; replace it with verified OSM opening_hours values per
network using `GBFS_OPENING_HOURS_<TAG>` (tag upper-cased, `-` replaced
by `_`), e.g. `GBFS_OPENING_HOURS_ENCICLA` or
`GBFS_OPENING_HOURS_TEMBICI_BOGOTA`. The `api` and `publisher` services
read `.env` directly, so these work for any enabled network without
editing `compose.yaml`.
Changes to `.env` take effect after `docker compose up -d`.

For external clients, use Traefik with HTTPS; the Docker host does not
publish a GBFS API port. Generated feed URLs use the incoming request
host/scheme. Traefik forwards `Host` and `X-Forwarded-Proto` by default;
uvicorn only honours them from addresses listed in
`GBFS_FORWARDED_ALLOW_IPS` (default `*`, which is acceptable because the API
is reachable only over the shared Docker network). Narrow it to Traefik's
address or subnet if untrusted containers join that network.
For OTP, ensure it can resolve and reach the network alias and every URL
linked inside the GBFS discovery feed.

## Image and releases

The image is published to:

```text
ghcr.io/colombiatransit/gbfs-colombia:latest
```

The GitHub Actions workflow builds and tests the image on push and
publishes it to GHCR from `main` and `v*` tags. It first pushes an
immutable `sha-...` tag, runs a Compose smoke test against it, and only
then promotes it to `latest` or the version tag. Pin a version tag or digest for reproducible deployments.
If the package is not public initially, set its GHCR package visibility to
**Public** in the GitHub organization's package settings.

To deploy a pinned release, set `GBFS_IMAGE` in `.env`, then run:

```sh
docker compose pull
docker compose up -d
```

## Add your own Colombian scraper

1. Copy `colombia_gbfs/scrapers/example_adapter.py` into a new module
   such as `cali_bikes.py`.
2. Implement a subclass of `pybikes.base.BikeShareSystem`, with
   `update(self, scraper=None)`. Populate `self.stations` with
   `BikeShareStation` values, or `self.vehicles` where appropriate.
   Do not fabricate bike counts, coordinates or service status.
3. Register the adapter in `config/scrapers.json`:

```json
[
  {
    "tag": "cali-bikes",
    "module": "cali_bikes",
    "class": "CaliBikes",
    "meta": {
      "name": "Cali Bikes",
      "city": "Cali",
      "country": "CO",
      "latitude": 3.4516,
      "longitude": -76.5320,
      "company": ["Operator name"]
    }
  }
]
```

This JSON is an **example configuration**, not a claim that this bike
sharing system or provider exists. Never enable the example until you
have implemented and tested a real data source.

   `meta.company` is required and must be a list of operator names
   (use `[]` if unknown). The tag must not reuse an upstream PyBikes
   tag such as `encicla`; collisions are rejected at startup.
4. Add `cali-bikes` to `ENABLED_NETWORKS` in `.env`. Optionally set
   `GBFS_OPENING_HOURS_CALI_BIKES`. If the adapter sets `authed = True`,
   provide its key as `PYBIKES_COLOMBIA_CALI_BIKES` in `.env`.
5. Commit the changes so GitHub Actions builds a new image, then deploy
   that image and restart the stack. New Python modules are bundled into
   the image; editing a running container is not required.

The adapter registry is deliberately restricted to modules within
`colombia_gbfs.scrapers`. At startup the code verifies that the
network is registered, the adapter subclasses `BikeShareSystem`, and
its metadata declares `country: CO` and a `company` list. Unregistered or foreign network
tags fail fast rather than silently enabling global collectors.

## Operations

```sh
docker compose logs -f publisher subscriber api
docker compose restart publisher
docker compose ps
```

The default poll interval is 180 seconds. The minimum configured
interval is 30 seconds. Respect data-provider terms, rate limits and
personal-data requirements before adding new sources.

The upstream PyBikes, Hyper and GBFS API versions are pinned by Git
commit hash in `Dockerfile`. Upgrades should be deliberate, followed
by a new image build and schema/GBFS validation. CI runs adapter
registration and API tests inside the Docker build (the tests use their
own temporary registries, so adding scrapers to `config/scrapers.json`
does not break them, but the committed registry must stay valid); it does not check the
availability of the live Colombian endpoints.

GBFS output is generated at runtime and **is not a GitHub Release artifact**.

## Licenses and attribution

This repository uses **AGPL-3.0-or-later**. The embedded upstream components
are licensed under AGPLv3 and retain their original copyrights. See
`LICENSE` and the upstream repositories above.

The Colombian transport operators remain the operators of their systems;
ColombiaTransit publishes the normalized feeds. Each feed retains
the upstream provider's operator metadata when it is supplied. This
project is not affiliated with CityBikes, EnCicla or Tembici.
