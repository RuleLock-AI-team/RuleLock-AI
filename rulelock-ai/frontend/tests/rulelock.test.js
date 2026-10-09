const test = require("node:test");
const assert = require("node:assert/strict");
const crypto = require("node:crypto");
const { handler } = require("../netlify/functions/rulelock.js");
const originalFetch = global.fetch;

const requiredEnv = ["DASHBOARD_USER", "DASHBOARD_PASSWORD", "DASHBOARD_SESSION_SECRET", "RULELOCK_API_TOKEN", "RULELOCK_API_URL"];
let previousEnv;

test.beforeEach(() => {
  previousEnv = Object.fromEntries(requiredEnv.map((key) => [key, process.env[key]]));
  process.env.DASHBOARD_USER = "dashboard-user";
  process.env.DASHBOARD_PASSWORD = "dashboard-password";
  process.env.DASHBOARD_SESSION_SECRET = "test-session-secret";
  process.env.RULELOCK_API_TOKEN = "backend-token";
  process.env.RULELOCK_API_URL = "https://backend.example";
});

test.afterEach(() => {
  for (const [key, value] of Object.entries(previousEnv)) {
    if (value === undefined) delete process.env[key];
    else process.env[key] = value;
  }
  global.fetch = originalFetch;
});

async function login() {
  return handler({
    httpMethod: "POST",
    queryStringParameters: { path: "/login" },
    headers: { "x-forwarded-proto": "https" },
    body: JSON.stringify({ username: "dashboard-user", password: "dashboard-password" }),
  });
}

function cookieFrom(result) {
  return result.headers["Set-Cookie"].split(";")[0];
}

test("proxy requires a valid signed dashboard cookie", async () => {
  const denied = await handler({ httpMethod: "GET", queryStringParameters: { path: "/audit-log" }, headers: {} });
  assert.equal(denied.statusCode, 401);

  const session = await login();
  assert.equal(session.statusCode, 200);
  assert.match(session.headers["Set-Cookie"], /HttpOnly/);
  assert.match(session.headers["Set-Cookie"], /Secure/);
  assert.match(session.headers["Set-Cookie"], /Max-Age=14400/);
  global.fetch = async () => { throw new Error("offline"); };
  const allowed = await handler({ httpMethod: "GET", queryStringParameters: { path: "/audit-log" }, headers: { cookie: cookieFrom(session) } });
  assert.equal(allowed.statusCode, 502); // Auth passed; fetch is unavailable in this test.
});

test("login rejects invalid credentials and requires all auth configuration", async () => {
  const denied = await handler({
    httpMethod: "POST", queryStringParameters: { path: "/login" }, headers: {},
    body: JSON.stringify({ username: "wrong", password: "wrong" }),
  });
  assert.equal(denied.statusCode, 401);
  delete process.env.DASHBOARD_SESSION_SECRET;
  assert.equal((await login()).statusCode, 503);
});

test("settings proxy route is removed", async () => {
  const result = await handler({ httpMethod: "GET", queryStringParameters: { path: "/settings/rulelock" }, headers: {} });
  assert.equal(result.statusCode, 404);
});

test("review proxy accepts only simulation requests and forces the upstream flag", async () => {
  const session = await login();
  const cookie = cookieFrom(session);
  let upstreamBody;
  let upstreamAuthorization;
  global.fetch = async (_url, options) => {
    upstreamBody = JSON.parse(options.body);
    upstreamAuthorization = options.headers.Authorization;
    return { status: 200, headers: new Headers({ "content-type": "application/json" }), text: async () => "{}" };
  };

  const denied = await handler({
    httpMethod: "POST", queryStringParameters: { path: "/review-order" }, headers: { cookie },
    body: JSON.stringify({ order_id: 42 }),
  });
  assert.equal(denied.statusCode, 400);

  const allowed = await handler({
    httpMethod: "POST", queryStringParameters: { path: "/review-order" }, headers: { cookie },
    body: JSON.stringify({ order_id: 42, simulation: true }),
  });
  assert.equal(allowed.statusCode, 200);
  assert.equal(upstreamBody.simulation, true);
  assert.equal(upstreamAuthorization, "Bearer backend-token");
});

test("proxy permits authenticated audit detail lookups by canonical order reference", async () => {
  const session = await login();
  let upstreamUrl;
  global.fetch = async (url) => {
    upstreamUrl = String(url);
    return { status: 200, headers: new Headers({ "content-type": "application/json" }), text: async () => JSON.stringify({ order_reference: "CK-20261003123456" }) };
  };
  const result = await handler({
    httpMethod: "GET",
    queryStringParameters: { path: "/audit-log/CK-20261003123456" },
    headers: { cookie: cookieFrom(session) },
  });
  assert.equal(result.statusCode, 200);
  assert.match(upstreamUrl, /\/audit-log\/CK-20261003123456$/);
});

test("edited or expired cookies are rejected", async () => {
  const session = await login();
  const modified = cookieFrom(session).replace(/.$/, "x");
  const rejected = await handler({ httpMethod: "GET", queryStringParameters: { path: "/audit-log" }, headers: { cookie: modified } });
  assert.equal(rejected.statusCode, 401);

  const expiredPayload = Buffer.from(JSON.stringify({ expiresAt: Math.floor(Date.now() / 1000) - 1 })).toString("base64url");
  const signature = crypto.createHmac("sha256", "test-session-secret").update(expiredPayload).digest("base64url");
  const expiredCookie = `rulelock_dashboard_session=${expiredPayload}.${signature}`;
  const expired = await handler({ httpMethod: "GET", queryStringParameters: { path: "/audit-log" }, headers: { cookie: expiredCookie } });
  assert.equal(expired.statusCode, 401);
});
