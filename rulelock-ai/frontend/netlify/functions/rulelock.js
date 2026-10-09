const crypto = require("crypto");

const SESSION_COOKIE = "rulelock_dashboard_session";
const SESSION_TTL_SECONDS = 4 * 60 * 60;
const DATA_COLLECTION_URL = () => process.env.RULELOCK_API_URL || "https://rulelock-data-collection.onrender.com";

exports.handler = async (event) => {
  let target;
  try {
    target = new URL(event.queryStringParameters?.path || "/health", "https://rulelock.local");
  } catch {
    return response(400, { error: "invalid proxy path" });
  }
  const path = target.pathname;
  const method = String(event.httpMethod || "GET").toUpperCase();

  if (path === "/login" && method === "POST") return login(event);
  if (path === "/logout" && method === "POST") {
    return response(200, { authenticated: false }, { "Set-Cookie": clearCookie(event) });
  }

  const allowed = new Set(["/dashboard/summary", "/audit-log", "/pipeline/info", "/ready", "/review-order"]);
  const auditDetail = /^\/audit-log\/(?:\d+|[A-Za-z0-9_-]+)$/.test(path);
  if (!allowed.has(path) && !auditDetail) return response(404, { error: "proxy route not found" });
  if (!hasValidSession(event)) return response(401, { error: "dashboard login required" });

  const upstreamToken = process.env.RULELOCK_API_TOKEN || "";
  if (!upstreamToken) return response(503, { error: "dashboard proxy is not configured" });
  if (path === "/review-order" && method !== "POST") return response(405, { error: "method not allowed" });
  if (path !== "/review-order" && method !== "GET") return response(405, { error: "method not allowed" });

  let body;
  if (path === "/review-order") {
    try {
      body = JSON.parse(event.body || "{}");
    } catch {
      return response(400, { error: "invalid JSON body" });
    }
    if (!body || typeof body !== "object" || Array.isArray(body) || body.simulation !== true) {
      return response(400, { error: "dashboard reviews require simulation:true" });
    }
    // Never trust a caller-supplied value to control the upstream mode.
    body.simulation = true;
  }

  try {
    const upstream = await fetch(`${DATA_COLLECTION_URL()}${path}${target.search}`, {
      method,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${upstreamToken}`,
      },
      body: path === "/review-order" ? JSON.stringify(body) : undefined,
    });
    return {
      statusCode: upstream.status,
      headers: {
        "Content-Type": upstream.headers.get("content-type") || "application/json",
        "Cache-Control": "no-store",
      },
      body: await upstream.text(),
    };
  } catch {
    return response(502, { error: "RuleLock upstream unavailable" });
  }
};

function login(event) {
  const username = process.env.DASHBOARD_USER || "";
  const password = process.env.DASHBOARD_PASSWORD || "";
  const secret = process.env.DASHBOARD_SESSION_SECRET || "";
  if (!username || !password || !secret) {
    return response(503, { error: "dashboard login is not configured" });
  }
  let credentials;
  try {
    credentials = JSON.parse(event.body || "{}");
  } catch {
    return response(400, { error: "invalid JSON body" });
  }
  if (!safeEqual(credentials?.username, username) || !safeEqual(credentials?.password, password)) {
    return response(401, { error: "invalid username or password" });
  }

  const expiresAt = Math.floor(Date.now() / 1000) + SESSION_TTL_SECONDS;
  const payload = Buffer.from(JSON.stringify({ expiresAt })).toString("base64url");
  const signature = sign(payload, secret);
  const cookie = `${SESSION_COOKIE}=${payload}.${signature}; Path=/; Max-Age=${SESSION_TTL_SECONDS}; HttpOnly; SameSite=Strict${isHttps(event) ? "; Secure" : ""}`;
  return response(200, { authenticated: true }, { "Set-Cookie": cookie });
}

function hasValidSession(event) {
  const secret = process.env.DASHBOARD_SESSION_SECRET || "";
  if (!secret) return false;
  const header = event.headers?.cookie || event.headers?.Cookie || "";
  const cookie = header.split(";").map((part) => part.trim()).find((part) => part.startsWith(`${SESSION_COOKIE}=`));
  if (!cookie) return false;
  const token = cookie.slice(SESSION_COOKIE.length + 1);
  const separator = token.lastIndexOf(".");
  if (separator <= 0) return false;
  const payload = token.slice(0, separator);
  const suppliedSignature = token.slice(separator + 1);
  if (!safeEqual(suppliedSignature, sign(payload, secret))) return false;
  try {
    const claims = JSON.parse(Buffer.from(payload, "base64url").toString("utf8"));
    return Number.isInteger(claims.expiresAt) && claims.expiresAt > Math.floor(Date.now() / 1000);
  } catch {
    return false;
  }
}

function sign(payload, secret) {
  return crypto.createHmac("sha256", secret).update(payload).digest("base64url");
}

function safeEqual(left, right) {
  const leftHash = crypto.createHash("sha256").update(String(left ?? "")).digest();
  const rightHash = crypto.createHash("sha256").update(String(right ?? "")).digest();
  return crypto.timingSafeEqual(leftHash, rightHash);
}

function isHttps(event) {
  const forwarded = event.headers?.["x-forwarded-proto"] || event.headers?.["X-Forwarded-Proto"] || "";
  return forwarded.split(",")[0].trim().toLowerCase() === "https" || process.env.NETLIFY === "true";
}

function clearCookie(event) {
  return `${SESSION_COOKIE}=; Path=/; Max-Age=0; HttpOnly; SameSite=Strict${isHttps(event) ? "; Secure" : ""}`;
}

function response(statusCode, body, extraHeaders = {}) {
  return {
    statusCode,
    headers: { "Content-Type": "application/json", "Cache-Control": "no-store", ...extraHeaders },
    body: JSON.stringify(body),
  };
}
