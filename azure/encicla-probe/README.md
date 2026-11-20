# EnCicla Azure Functions connectivity probe

A minimal, **manual**, authenticated Azure Functions Python v2 HTTP endpoint to
test whether Azure Functions can read the same official EnCicla endpoint that
returned 139 records in GitHub Actions. This does **not** modify the running
Docker publisher, create a public data mirror, or schedule any polling.

## Deployment

1. In your own Azure subscription, create a **Linux Python 3.12 Azure Function App**
   on a suitable consumption-based plan (prefer Flex Consumption), using an
   appropriately sized instance and **always-ready instances = 0**. Confirm the
   region, storage, logging, and networking costs in Azure before creation.
   Azure resource creation is deliberately **not** performed by this repository.
2. In the Function App's **Deployment** settings, configure GitHub Actions for
   the repository `ColombiaTransit/gbfs-colombia` if possible. Azure can configure
   GitHub OIDC credentials automatically. If configuring manually, create a
   federated identity with rights to deploy to this Function App.
3. In repository secrets, set `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`,
   `AZURE_SUBSCRIPTION_ID`. In repository variables, set
   `ENCICLA_AZURE_FUNCTION_APP` to the actual Function App name.
   Do not commit Azure credentials or Function keys.
4. Run [EnCicla Azure Function test and deploy](../../.github/workflows/encicla-azure-function.yml)
   with `deploy=false` to run **offline unit tests only**. Then run with
   `deploy=true` when the Azure resources and OIDC authorization are ready.
5. In Azure Portal, open the Function App → Functions → `encicla-probe`
   → **Get function URL**. Invoke the function with its key (never share the key
   in public logs). Example:

   `curl -sS -H "x-functions-key: <FUNCTION_KEY>" "https://<APP_NAME>.azurewebsites.net/api/encicla-probe"`

The response contains only the public outbound IP (if obtainable), HTTP status,
elapsed time, content type, byte count, JSON validity, and record count.
No station details or API response body are returned. A 200 response from the
Function means the diagnostics executed; check **`success`** to determine
whether EnCicla returned usable station data.

### Costs and security

No automated polling is configured. An HTTP Function with `FUNCTION` auth
requires a function key; avoid using an anonymous endpoint. Consumption plans
can have ancillary storage/logging/egress costs, and Azure Functions **does not
necessarily use the same outbound IP pool as GitHub Actions runners**.

After testing, disable or delete the Azure resources if they are not required.
This probe does not change PyBikes, GBFS publishing, or any production route.
