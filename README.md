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

The Docker network does **not** publish ZeroMQ publicly. The GBFS API binds
to `127.0.0.1:8000` by default, ready for an HTTPS reverse proxy.
The database persists in the `gbfs-data` named Docker volume.

## Quick start

```sh
git clone https://github.com/ColombiaTransit/gbfs-colombia.git
cd gbfs-colombia
cp .env.example .env
docker compose pull
docker compose up -d
docker compose ps
```

Once live provider updates have arrived, use:

- `http://localhost:8000/3/manifest.json`
- `http://localhost:8000/3/encicla/gbfs.json`
- `http://localhost:8000/3/tembici-bogota/gbfs.json`
- `http://localhost:8000/healthz` (API liveness only)

**Data freshness is not guaranteed by the health endpoint.** Check
`last_updated`, provider availability, and logs before advertising feeds.
The initial GBFS outputs depend on the live upstream endpoints being reachable.
Changes to `.env` take effect after `docker compose up -d`.

To access the API from another host, set `GBFS_BIND_IP=0.0.0.0` and
place it behind an appropriate firewall or HTTPS reverse proxy.
Generated feed URLs use the incoming request host/scheme; configure your
reverse proxy to forward the correct Host and HTTPS headers.

## Image and releases

The image is published to:

```text
ghcr.io/colombiatransit/gbfs-colombia:latest
```

The GitHub Actions workflow builds and tests the image on push and
publishes it to GHCR from `main` and `v*` tags. It also publishes
`sha-...` tags. Pin a version tag or digest for reproducible deployments.
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
      "company": []
    }
  }
]
```

This JSON is an **example configuration**, not a claim that this bike
sharing system or provider exists. Never enable the example until you
have implemented and tested a real data source.

4. Add `cali-bikes` to `ENABLED_NETWORKS` in `.env`.
5. Commit the changes so GitHub Actions builds a new image, then deploy
   that image and restart the stack. New Python modules are bundled into
   the image; editing a running container is not required.

The adapter registry is deliberately restricted to modules within
`colombia_gbfs.scrapers`. At startup the code verifies that the
network is registered, the adapter subclasses `BikeShareSystem`, and
its metadata declares `country: CO`. Unregistered or foreign network
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
registration tests inside the Docker build; it does not check the
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
