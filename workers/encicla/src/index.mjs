/**
 * EnCicla / Medellín: Cloudflare Workers Free diagnostic and narrow proxy.
 * License: AGPL-3.0-or-later.
 * Diagnostic only until the public source and reuse permission are verified.
 * No general-purpose URL proxy and no incoming client credentials forwarded.
 */
const SOURCE = "https://webapp.metropol.gov.co/wsencicla/api/Disponibilidad/GetDisponibilidadMapas";
const IP_SERVICE = "https://api.ipify.org?format=json";
const GEO_SERVICE = "https://api.country.is/";
const TTL = 30;
const MAX_BODY = 1_000_000;

function json(data, status = 200, extraHeaders = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
      "X-Content-Type-Options": "nosniff",
      ...extraHeaders,
    },
  });
}

function configured(env) {
  return typeof env?.PROXY_TOKEN === "string" && env.PROXY_TOKEN.length >= 32;
}

function equalToken(expected, supplied) {
  if (typeof supplied !== "string" || supplied.length > 1024) return false;
  let diff = expected.length ^ supplied.length;
  for (let i = 0, end = Math.max(expected.length, supplied.length); i < end; i++) {
    diff |= (expected.charCodeAt(i) || 0) ^ (supplied.charCodeAt(i) || 0);
  }
  return diff === 0;
}

async function limitedJson(response, maximum = MAX_BODY) {
  const headerLength = response.headers.get("content-length");
  if (headerLength && Number(headerLength) > maximum) throw Error("response_too_large");
  if (!response.body) throw Error("missing_response_body");
  const reader = response.body.getReader();
  let total = 0;
  const chunks = [];
  try {
    for (;;) {
      const part = await reader.read();
      if (part.done) break;
      total += part.value.byteLength;
      if (total > maximum) throw Error("response_too_large");
      chunks.push(part.value);
    }
  } finally {
    await reader.cancel().catch(() => {});
  }
  const bytes = new Uint8Array(total);
  let position = 0;
  for (const chunk of chunks) {
    bytes.set(chunk, position);
    position += chunk.byteLength;
  }
  try {
    return JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(bytes));
  } catch {
    throw Error("invalid_json");
  }
}

function remoteFetch(url, timeout = 10000) {
  return fetch(url, {
    method: "GET",
    redirect: "manual",
    headers: {
      Accept: "application/json",
      "User-Agent": "ColombiaTransit-GBFS-Research/1.0",
    },
    signal: AbortSignal.timeout(timeout),
  });
}

async function sourceRequest() {
  let response;
  try {
    response = await remoteFetch(SOURCE);
  } catch (error) {
    return { ok: false, error: "network_error", detail: error?.name === "TimeoutError" ? "timeout" : "connection_failed" };
  }
  const status = response.status;
  const contentType = (response.headers.get("content-type") || "").slice(0, 100);
  if (status !== 200) {
    response.body?.cancel().catch(() => {});
    return { ok: false, error: "non_200", status, contentType };
  }
  try {
    const data = await limitedJson(response);
    if (!Array.isArray(data)) return { ok: false, error: "unexpected_json_shape", status, contentType };
    return { ok: true, status, contentType, count: data.length, data };
  } catch (error) {
    return { ok: false, error: error?.message || "invalid_response", status, contentType };
  }
}

function safeIp(value) {
  return typeof value === "string" && value.length > 2 && value.length < 50 &&
    /^[0-9a-fA-F:.]+$/.test(value) && value.includes(".") !== value.includes(":");
}

async function egressEstimate() {
  try {
    const ipResponse = await remoteFetch(IP_SERVICE, 7000);
    if (!ipResponse.ok) return { status: "ip_lookup_http_error", http_status: ipResponse.status };
    const ipData = await limitedJson(ipResponse, 4096);
    if (!safeIp(ipData?.ip)) return { status: "invalid_ip_result" };
    const ip = ipData.ip;
    const geoResponse = await remoteFetch(GEO_SERVICE + encodeURIComponent(ip), 7000);
    if (!geoResponse.ok) return { status: "geo_lookup_http_error", ip, http_status: geoResponse.status };
    const geo = await limitedJson(geoResponse, 4096);
    return {
      status: "ok",
      ip,
      country: typeof geo?.country === "string" ? geo.country : null,
      note: "Third-party GeoIP estimate. EnCicla can see/classify a different egress IP.",
    };
  } catch {
    return { status: "lookup_unavailable" };
  }
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (request.method !== "GET") return json({ error: "method_not_allowed" }, 405, { Allow: "GET" });
    if (url.search || url.hash) return json({ error: "query_not_allowed" }, 400);
    if (url.pathname === "/health") {
      return json({ service: "encicla-worker-test", status: configured(env) ? "ready" : "not_configured" },
        configured(env) ? 200 : 503);
    }
    if (url.pathname !== "/diagnose" && url.pathname !== "/availability") return json({ error: "not_found" }, 404);
    if (!configured(env)) return json({ error: "token_not_configured" }, 503);
    const header = request.headers.get("authorization") || "";
    if (!equalToken(env.PROXY_TOKEN, header.startsWith("Bearer ") ? header.slice(7) : "")) {
      return json({ error: "unauthorized" }, 401, { "WWW-Authenticate": "Bearer" });
    }

    if (url.pathname === "/diagnose") {
      const upstream = await sourceRequest();
      const egress = await egressEstimate();
      return json({
        checked_at: new Date().toISOString(),
        worker_edge_colo: request.cf?.colo || null,
        worker_edge_note: "Worker execution location, NOT egress country",
        upstream: {
          reachable: upstream.ok,
          http_status: upstream.status ?? null,
          content_type: upstream.contentType ?? null,
          station_records: upstream.ok ? upstream.count : null,
          error: upstream.error ?? null,
          detail: upstream.detail ?? null,
        },
        egress_estimate: egress,
        upstream_accessible: upstream.ok,
      });
    }

    const cache = globalThis.caches?.default;
    const key = new Request(new URL("/availability", request.url), { method: "GET" });
    if (cache) {
      const found = await cache.match(key);
      if (found) {
        const headers = new Headers(found.headers);
        headers.set("X-Proxy-Cache", "HIT");
        return new Response(found.body, { status: 200, headers });
      }
    }
    const upstream = await sourceRequest();
    if (!upstream.ok) {
      return json({ error: "source_unavailable", upstream_http_status: upstream.status ?? null, reason: upstream.error }, 502);
    }
    const response = json(upstream.data, 200, {
      "Cache-Control": "public, max-age=" + TTL + ", s-maxage=" + TTL,
      "X-Proxy-Cache": "MISS",
    });
    if (cache && ctx?.waitUntil) ctx.waitUntil(cache.put(key, response.clone()).catch(() => {}));
    return response;
  },
};
