# GBFS Colombia

Colombia-only GBFS 3.0 feeds built with [PyBikes](https://github.com/eskerda/pybikes),
[CityBikes Hyper](https://github.com/citybikes/hyper), and
[CityBikes GBFS API](https://github.com/citybikes/gbfs-api).

The default configuration enables **EnCicla** (Medellín / Valle de Aburrá) and
**Tembici Bogotá**. **BiciRio Rionegro** is implemented and opt-in. An observed
publisher run on 2026-11-20 successfully emitted **138 EnCicla**, **238
Tembici**, and **16 BiciRio** stations with all three enabled (one snapshot,
not guaranteed permanent totals). BiciRio still has source-completeness and
redistribution/usage questions documented below. No non-Colombian networks
are exposed.

## Architecture

One GHCR image, four Compose services:

- `publisher`: periodically loads only enabled networks via PyBikes/Hyper
  and publishes updates over ZeroMQ.
- `subscriber`: stores those updates in the persistent SQLite database.
- `api`: serves GBFS **3.0**; only enabled network IDs are exposed.
- `migrate`: a one-shot database initialization/migration job.

No container publishes TCP ports on the Docker host. The `publisher`,
`subscriber`, and `migrate` services communicate only on their Compose
backend network. The `api` additionally joins the existing external
Docker network `traefik_default`, where it is reachable as
`http://gbfs-colombia:8000`. The `publisher` can still reach the upstream
providers over the internet. The database
persists in the `gbfs-data` named Docker volume.

## Quick start

```sh
git clone https://github.com/ColombiaTransit/gbfs-colombia.git
cd gbfs-colombia
cp .env.example .env
# Edit .env: set GBFS_CONTACT_EMAIL to a monitored address.
docker network inspect traefik_default >/dev/null  # must already exist
docker compose pull
docker compose up -d
docker compose ps
```

Once live provider updates have arrived, **from a container on the
`traefik_default` network** use:

- `http://gbfs-colombia:8000/3/manifest.json`
- `http://gbfs-colombia:8000/3/encicla/gbfs.json`
- `http://gbfs-colombia:8000/3/tembici-bogota/gbfs.json`
- `http://gbfs-colombia:8000/3/bicirio-rionegro/gbfs.json` (only when enabled)
- `http://gbfs-colombia:8000/healthz` (API liveness only)

The host cannot access these URLs directly. To check liveness on the server:

```sh
docker compose exec -T api python -c 'import urllib.request; print(urllib.request.urlopen("http://127.0.0.1:8000/healthz").read().decode())'
```

### Network

The `api` service joins the external network `traefik_default`, which
this stack neither creates nor removes; `docker compose up` fails if it
does not exist. Any container on that network (for example OTP) reaches
the API as `http://gbfs-colombia:8000`. To use a different existing
network, set `GBFS_SHARED_NETWORK` in `.env`.

No reverse-proxy routing is configured: the API is not exposed publicly.
Generated feed URLs use the host and scheme of the incoming request, so
OTP sees `http://gbfs-colombia:8000/...` URLs, which it can reach on the
same network. The exact OTP updater configuration depends on your OTP
version.

**Data freshness is not guaranteed by the health endpoint.** Check
`last_updated`, provider availability, and logs before advertising feeds.
The GBFS outputs depend on live provider updates. EnCicla can use a dedicated
Azure Function relay when configured; other networks fetch their sources directly.
GBFS 3.0 requires a monitored `feed_contact_email` and
`opening_hours`. Until `GBFS_CONTACT_EMAIL` is provided,
`system_information.json` returns HTTP 503 instead of inventing a contact.
The initial `24/7 unknown` opening_hours expression explicitly indicates
unverified hours; replace it with verified OSM opening_hours values per
network using `GBFS_OPENING_HOURS_<TAG>` (tag upper-cased, `-` replaced
by `_`), e.g. `GBFS_OPENING_HOURS_ENCICLA`,
`GBFS_OPENING_HOURS_TEMBICI_BOGOTA`, or
`GBFS_OPENING_HOURS_BICIRIO_RIONEGRO`.

For local Docker Compose, the optional `.env` file provides Compose
substitution and is also loaded by the publisher/API through `env_file`.
For **Portainer stacks**, values entered in the stack's **Environment
variables** interface are Compose substitutions, **not** automatically
injected into a container. The current `compose.yaml` explicitly passes
`ENABLED_NETWORKS`, `UPDATE_INTERVAL_SECONDS`,
`ENCICLA_PROXY_URL`, and `ENCICLA_FUNCTION_KEY` to the publisher,
plus the API's relevant settings. Recreate the affected containers
after changing their environment (Portainer **Update the stack** or
`docker compose up -d`). Do not paste secrets into screenshots or logs.

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

## BiciRio Rionegro (opt-in scraper)

The `bicirio-rionegro` plugin is implemented at
[`colombia_gbfs/scrapers/bicirio.py`](colombia_gbfs/scrapers/bicirio.py),
registered in `config/scrapers.json`, and covered by offline tests.
The corrected, **non-publishing** live run on 2026-11-19 succeeded:
**16** public API stations geolocated against the operator map,
**26** bicycle objects and **13** stations reporting online.
These are a single snapshot, not permanent network totals.

- Operator data: only the two known public, unauthenticated
  `/api/v1/free_access/{stations,bicycles}` GET endpoints.
- Bicycle count: the official web-map's `len(bicycle_list)` approach.
  The currently observed `bicycleState` is `Ready`; unknown future
  states cause a visible scraper error rather than silently counting
  potentially unavailable bikes.
- Station positions: all **18** coordinates from the operator's public
  Leaflet map are embedded as name-matched reference locations. This
  resolves the API's El Faro/Porvenir 50/La Cuarta duplication; the 16
  currently known public API station records all have unique positions.
  Unknown names use strictly validated source coordinates only; the
  internal/virtual API records remain excluded. Station identifiers are
  stable and independent of coordinates.
- Station operations: `state=Open` and `connectionState=true`
  indicate online for this initial implementation. No made-up
  dock capacities or bike identifiers are published. Failed upstream
  requests abort the snapshot instead of fabricating zero availability.
- TLS: BiciRio omits a GoDaddy G2 intermediate certificate. During
  Docker build, the intermediate is downloaded over verified HTTPS
  from GoDaddy, fingerprint-checked, and included in a **BiciRio-only
  Requests CA bundle**. Normal hostname and certificate verification
  remain enabled. The system-wide trust store is not modified.
- **Not enabled by default** (although tested running in the user's stack
  on 2026-11-20): the map lists 18 named locations but two
  of them (Quebrada Arriba and Zona Franca) are not in the current
  anonymous station API; no fake availability is published for those.
  Redistribution terms and service-status semantics should also be
  confirmed before publishing.

To opt in after reviewing the outstanding source/permission questions,
edit `.env`:

```dotenv
ENABLED_NETWORKS=encicla,tembici-bogota,bicirio-rionegro
GBFS_OPENING_HOURS_BICIRIO_RIONEGRO=Mo-Fr 06:00-18:00; Sa 06:00-16:00
```

The hours above are the operator's historically published weekday/
Saturday hours; **verify current hours before applying them**. After
a tested image has been published, run `docker compose pull` and
`docker compose up -d`. Inspect the publisher logs and the
`/3/bicirio-rionegro/station_status.json` response from a container
on the shared network, checking data freshness and station status.

CI tests: [image build workflow](.github/workflows/container.yml);
public-data dry-run: [BiciRio live smoke test](.github/workflows/bicirio-live-dry-run.yml)
(requires read access to GHCR and uses the validated `latest` image).
Research and acceptance criteria:
[`docs/research/bicirio-rionegro.md`](docs/research/bicirio-rionegro.md).

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

## EnCicla via Azure Function (opt-in)

The publisher host cannot reliably access the official EnCicla API directly.
The **production-tested** Azure Function (West US, Flex Consumption)
exposes the authenticated `/api/encicla-data` relay. The 2026-11-20
publisher log confirmed:

```text
[encicla] stations 138
[encicla] Publishing network:EnciclaProxy:encicla:update
```

The upstream API can return a slightly different number of *raw* records:
a direct Azure test returned 139 JSON records, while PyBikes filters
operation-centre entries before publishing stations.

The relay changes only EnCicla's HTTP transport. It retains the pinned
upstream PyBikes `Encicla` station parsing, identifiers and metadata and
the normal Hyper → subscriber → GBFS 3.0 pipeline. Tembici and BiciRio
do not use Azure. Each scheduled EnCicla update makes one request via
Azure; there is **no application cache, timer, or Tor/Cloudflare proxy**.

### Configuration: Docker Compose or Portainer

Use these private environment variables on the **publisher**:

```dotenv
ENABLED_NETWORKS=encicla,tembici-bogota
UPDATE_INTERVAL_SECONDS=180
ENCICLA_PROXY_URL=https://func-encicla-probe-c9d2cuavbab5fga8.westus-01.azurewebsites.net/api/encicla-data
ENCICLA_FUNCTION_KEY=<function-key-from-azure>
```

The URL above is the deployment hostname used for the successful live
test. Confirm the actual hostname in Azure Portal → Function App →
Functions → `encicla-data` → **Get function URL**. Supply the key via
the `x-functions-key` HTTP header, never as a URL parameter.

In **Portainer**, set these under the stack's **Environment variables** and
choose **Update the stack**. `compose.yaml` explicitly forwards the two
`ENCICLA_*` values to the publisher. For command-line Compose, place them
in the private `.env` instead and recreate the publisher.

Never store the key in GitHub or paste it into screenshots, public logs,
or issue comments. **If a Function Key has been exposed, rotate it in
Azure and update the stack environment.**

To enable BiciRio *as an explicit opt-in* as well:

```dotenv
ENABLED_NETWORKS=encicla,tembici-bogota,bicirio-rionegro
```

BiciRio has been observed to publish 16 stations successfully, but
review the source/permission caveats in its section before relying on
its feed.

### Verification and troubleshooting

After the image build and container smoke test pass:

```sh
docker compose pull
docker compose up -d
docker compose logs --tail=100 publisher subscriber
```

Verify the EnCicla environment *without printing the key*:

```sh
docker compose exec -T publisher python -c 'import os; print("Proxy URL:", os.getenv("ENCICLA_PROXY_URL")); print("Key set:", bool(os.getenv("ENCICLA_FUNCTION_KEY")))'
```

Verify that the custom scraper, not the direct upstream scraper, is
selected:

```sh
docker compose exec -T publisher python -c 'from colombia_gbfs.registry import activate; print([(m,c) for m,c,r in activate() if r["tag"]=="encicla"])'
```

Expected when configured:

```text
[('colombia_encicla_proxy', 'EnciclaProxy')]
```

The publisher should then log `Publishing network:EnciclaProxy:encicla:update`.
A `json.decoder.JSONDecodeError: Expecting value: line 1 column 1`
may indicate the original PyBikes transport is still selected and
receiving an HTML/blocked response. Confirm both variables reached
the container and that the new image is running.

For a bounded live relay check from the publisher container:

```sh
docker compose exec -T publisher python -c 'import os,requests; u=os.environ["ENCICLA_PROXY_URL"]; k=os.environ["ENCICLA_FUNCTION_KEY"]; r=requests.get(u,headers={"x-functions-key":k},timeout=15); r.raise_for_status(); v=r.json(); assert isinstance(v,list); print("EnCicla records:",len(v))'
```

Finally check the subscriber and `/3/encicla/station_status.json`
on the shared Docker network for recent timestamps. The API `/healthz`
route confirms only liveness, not source freshness.

On Azure HTTP errors, timeouts or invalid JSON, the EnCicla update fails
rather than publishing fabricated zero availability or falling back to
the blocked direct endpoint.

To disable the override, clear **both**
`ENCICLA_PROXY_URL` and `ENCICLA_FUNCTION_KEY` and recreate the publisher.
This restores direct upstream transport, which may still be blocked.
It does not affect Tembici or BiciRio.

Azure deployment: [EnCicla Function workflow](.github/workflows/encicla-azure-function.yml).
Docker image deployment: [Container workflow](.github/workflows/container.yml).
The former Tor and Cloudflare experimental probes and their workflows
were removed after the Azure solution was verified.

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
