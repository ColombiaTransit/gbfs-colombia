# EnCicla — Cloudflare Workers Free test

**Status:** prepared and tested offline; **not deployed to Cloudflare**; no production GBFS changes.

This is a read-only, authenticated diagnostic + narrow proxy. It targets only the public endpoint referenced by pinned `pybikes/encicla.py` at revision `b8681d2344d2ccc61d7b99b089a8cdba167a169e`:

`https://webapp.metropol.gov.co/wsencicla/api/Disponibilidad/GetDisponibilidadMapas`

## API

| Route | Auth | Purpose |
| --- | --- | --- |
| `GET /health` | None | Check whether the required secret is configured |
| `GET /diagnose` | Bearer token | Measure EnCicla HTTP status, validated JSON array record count, approximate egress IP and GeoIP country |
| `GET /availability` | Bearer token | Proxy the fixed public source, checking for valid JSON array; 30-second per-edge cache of successful response |

All other paths and query strings are rejected. No arbitrary URL parameters, incoming cookies, credentials or Authorization headers are relayed to the source; no redirects are followed. An upstream 403 or HTML challenge produces a source error, not fabricated zero availability. Max response size is 1 MB.

The Worker requires a secret `PROXY_TOKEN` with at least 32 characters. **Never** put the token in a URL, repository, screenshot, issue, chat or public logs. Only the public `/health` path is unauthenticated.

## Beginner setup: Cloudflare dashboard

1. Create a **free** Cloudflare account at https://dash.cloudflare.com/.
2. Go to **Workers & Pages** > **Create application**. Choose a basic/Hello World Worker starter (dashboard terminology may vary). Use name **`colombiatransit-encicla-test`** and deploy it. Note the assigned `*.workers.dev` URL.
3. Open that Worker, choose **Edit code**, and replace the starter with the complete contents of [`src/index.mjs`](src/index.mjs), copying via GitHub's **Raw** view. **Deploy**.
4. Open **Settings > Variables and Secrets > Add**, choose **Secret**, enter name **`PROXY_TOKEN`** and a securely generated random value of at least 32 characters, then **Deploy**.
5. Open `https://YOUR-WORKER.workers.dev/health` in the browser. Expect `{"service":"encicla-worker-test","status":"ready"}` and HTTP 200. A 503/`not_configured` means the secret is not set properly.
6. Run the diagnosis using PowerShell (below). Replace the URL and enter your secret when prompted. Do not send your token to anybody.

PowerShell:

~~~powershell
$base = 'https://colombiatransit-encicla-test.YOUR-SUBDOMAIN.workers.dev'
$secret = Read-Host 'PROXY_TOKEN' -AsSecureString
$plain = [System.Net.NetworkCredential]::new('', $secret).Password
Invoke-RestMethod -Uri "$base/diagnose" -Headers @{ Authorization = "Bearer $plain" } | ConvertTo-Json -Depth 6
Remove-Variable plain, secret
~~~

The `/availability` route uses the same token, but only test it after confirming that the public source is accessible and that data reuse is allowed. Do not connect it to production yet.

## Alternative: deploy from a terminal with Wrangler

~~~sh
cd workers/encicla
npx wrangler login
npx wrangler deploy
npx wrangler secret put PROXY_TOKEN
~~~

Wrangler prompts for the secret rather than placing it in the repo. The default config uses **Workers Free** and does not force a placement region.

## Interpreting the diagnostic

- `upstream.reachable=true`, HTTP 200 and a station count: the Worker received a valid station JSON array on this attempt. The count is *not* proof that all stations or bikes are actually available.
- HTTP **403**: the Worker was blocked or rejected by the source, but the reason may be GeoIP, bot protection or other policy.
- HTTP 200 with `invalid_json`: often an HTML challenge/portal instead of the JSON feed.
- `network_error`: timeout, DNS/TLS or connectivity failure; cannot be classified as GeoIP.
- `egress_estimate`: based on requests from the Worker to ipify and country.is. This is a **third-party approximation** and does not guarantee that EnCicla sees the same source IP or country.
- `worker_edge_colo`: Cloudflare location handling the Worker; **not** confirmation of the exit IP/country.

Cloudflare **Smart Placement** is optional: Worker > **Settings > General > Placement > Smart**. It is available on Free, but does not guarantee a Colombian IP. Compare results before and after changing it. Do not assume a Colombian edge location means a Colombian IP.

## Verification and limitations

Run offline tests with `node --test workers/encicla/test/index.test.mjs` from the repository root. The GitHub Actions workflow `.github/workflows/test-encicla-worker.yml` checks the Worker without contacting Cloudflare, EnCicla, or third-party IP services.

Cloudflare Workers Free currently includes 100,000 incoming requests/day, 10 ms CPU time/request, and 50 external subrequests/request. This diagnostic uses at most 3 remote subrequests and the availability route normally 1 (0 on a cache hit). Network wait does not count as CPU time. The cache is per Cloudflare data centre.

**Production:** No deployment, adaptation of the PyBikes scraper, or activation of a new GBFS feed occurs automatically. First verify consistent source responses, the validity of the actual data, usage terms/licensing, and whether a worker token can be safely passed to the Python publisher.

## Official references

- https://developers.cloudflare.com/workers/get-started/dashboard/
- https://developers.cloudflare.com/workers/configuration/secrets/
- https://developers.cloudflare.com/workers/configuration/placement/
- https://developers.cloudflare.com/workers/platform/limits/
- https://developers.cloudflare.com/workers/runtime-apis/cache/
- https://www.ipify.org/
- https://country.is/
