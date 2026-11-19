import test from "node:test";
import assert from "node:assert/strict";
import worker from "../src/index.mjs";

const SOURCE = "https://webapp.metropol.gov.co/wsencicla/api/Disponibilidad/GetDisponibilidadMapas";
const TOKEN = "unit-test-secret-token-long-enough-1234567890";
const ENV = { PROXY_TOKEN: TOKEN };
const base = "https://test.example.workers.dev";
const makeReq = (path, token = TOKEN) => new Request(base + path, {
  headers: { Authorization: "Bearer " + token },
});
const makeJson = (data, status = 200) => new Response(JSON.stringify(data), {
  status, headers: { "Content-Type": "application/json" },
});
async function mock(responses, callback) {
  const previousFetch = globalThis.fetch;
  const previousCaches = globalThis.caches;
  const calls = [];
  globalThis.fetch = async (url, options) => {
    calls.push({ url: String(url), options });
    if (!responses[String(url)]) throw Error("Unexpected request " + url);
    if (responses[String(url)] instanceof Error) throw responses[String(url)];
    return responses[String(url)].clone();
  };
  delete globalThis.caches;
  try {
    await callback(calls);
  } finally {
    globalThis.fetch = previousFetch;
    if (previousCaches === undefined) delete globalThis.caches;
    else globalThis.caches = previousCaches;
  }
}

test("health reports token configuration without requiring login", async () => {
  assert.equal((await worker.fetch(makeReq("/health"), ENV, {})).status, 200);
  assert.equal((await worker.fetch(makeReq("/health"), {}, {})).status, 503);
});

test("protected routes reject missing/incorrect token without upstream calls", async () => {
  await mock({}, async (calls) => {
    for (const path of ["/diagnose", "/availability"]) {
      assert.equal((await worker.fetch(makeReq(path, "invalid"), ENV, {})).status, 401);
      assert.equal((await worker.fetch(new Request(base + path), ENV, {})).status, 401);
    }
    assert.equal(calls.length, 0);
  });
});

test("rejects non-GET, arbitrary paths and URL parameters", async () => {
  await mock({}, async (calls) => {
    assert.equal((await worker.fetch(new Request(base + "/availability", { method: "POST" }), ENV, {})).status, 405);
    assert.equal((await worker.fetch(makeReq("/availability?url=https://evil.test"), ENV, {})).status, 400);
    assert.equal((await worker.fetch(makeReq("/api/proxy"), ENV, {})).status, 404);
    assert.equal(calls.length, 0);
  });
});

test("returns verified public station array and never forwards Authorization", async () => {
  const stations = [{ id: "1", name: "Example station", bikes: 5 }];
  await mock({ [SOURCE]: makeJson(stations) }, async (calls) => {
    const response = await worker.fetch(makeReq("/availability"), ENV, {});
    assert.equal(response.status, 200);
    assert.deepEqual(await response.json(), stations);
    assert.equal(response.headers.get("X-Proxy-Cache"), "MISS");
    assert.equal(calls.length, 1);
    assert.equal(calls[0].url, SOURCE);
    assert.equal(calls[0].options.redirect, "manual");
    assert.equal(calls[0].options.headers.Authorization, undefined);
  });
});

test("an empty valid source array is not treated as an error", async () => {
  await mock({ [SOURCE]: makeJson([]) }, async () => {
    const response = await worker.fetch(makeReq("/availability"), ENV, {});
    assert.equal(response.status, 200);
    assert.deepEqual(await response.json(), []);
  });
});

test("upstream HTTP 403 is an explicit source error, not a fake zero", async () => {
  await mock({ [SOURCE]: new Response("geo block", { status: 403, headers: { "Content-Type": "text/html" } }) }, async () => {
    const response = await worker.fetch(makeReq("/availability"), ENV, {});
    assert.equal(response.status, 502);
    const data = await response.json();
    assert.equal(data.upstream_http_status, 403);
  });
});

test("HTTP 200 with an HTML challenge is rejected", async () => {
  await mock({ [SOURCE]: new Response("<html>blocked</html>", { status: 200 }) }, async () => {
    const response = await worker.fetch(makeReq("/availability"), ENV, {});
    assert.equal(response.status, 502);
    assert.equal((await response.json()).reason, "invalid_json");
  });
});

test("a redirect or non-array JSON never becomes station availability", async () => {
  await mock({ [SOURCE]: new Response(null, { status: 302, headers: { Location: "https://evil.test" } }) }, async (calls) => {
    const response = await worker.fetch(makeReq("/availability"), ENV, {});
    assert.equal(response.status, 502);
    assert.equal(calls.length, 1);
  });
  await mock({ [SOURCE]: makeJson({ unexpected: "shape" }) }, async () => {
    assert.equal((await worker.fetch(makeReq("/availability"), ENV, {})).status, 502);
  });
});

test("diagnosis reports count and egress estimate, not individual stations", async () => {
  await mock({
    [SOURCE]: makeJson([{ name: "Station A" }, { name: "Station B" }]),
    "https://api.ipify.org?format=json": makeJson({ ip: "203.0.113.6" }),
    "https://api.country.is/203.0.113.6": makeJson({ country: "CO", ip: "203.0.113.6" }),
  }, async (calls) => {
    const request = makeReq("/diagnose");
    Object.defineProperty(request, "cf", { value: { colo: "AMS" } });
    const response = await worker.fetch(request, ENV, {});
    const diagnosis = await response.json();
    assert.equal(response.status, 200);
    assert.equal(diagnosis.upstream.station_records, 2);
    assert.equal(diagnosis.egress_estimate.country, "CO");
    assert.equal(diagnosis.worker_edge_colo, "AMS");
    assert.equal(diagnosis.upstream_accessible, true);
    assert.equal(JSON.stringify(diagnosis).includes("Station A"), false);
    assert.equal(calls.length, 3);
  });
});

test("cache hit avoids repeating source calls", async () => {
  let entry;
  await mock({ [SOURCE]: makeJson([{ id: "1" }]) }, async (calls) => {
    globalThis.caches = {
      default: {
        async match() { return entry?.clone() || null; },
        async put(_key, value) { entry = value.clone(); },
      },
    };
    const tasks = [];
    const context = { waitUntil(task) { tasks.push(task); } };
    const first = await worker.fetch(makeReq("/availability"), ENV, context);
    assert.equal(first.headers.get("X-Proxy-Cache"), "MISS");
    await Promise.all(tasks);
    const second = await worker.fetch(makeReq("/availability"), ENV, context);
    assert.equal(second.headers.get("X-Proxy-Cache"), "HIT");
    assert.equal(calls.length, 1);
  });
});
