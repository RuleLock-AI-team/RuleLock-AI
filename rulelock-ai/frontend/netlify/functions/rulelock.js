const DATA_COLLECTION_URL = process.env.RULELOCK_API_URL || "https://rulelock-data-collection.onrender.com";
const RULELOCK_API_TOKEN = process.env.RULELOCK_API_TOKEN || "";

exports.handler = async (event) => {
  const requestedPath = event.queryStringParameters?.path || "/health";
  const path = requestedPath.startsWith("/") ? requestedPath : `/${requestedPath}`;
  const allowedPaths = [
    "/dashboard/summary",
    "/audit-log",
    "/review-order",
    "/settings/rulelock",
    "/browse",
    "/cart",
    "/apply-coupon",
    "/checkout",
  ];

  if (!allowedPaths.some((allowed) => path === allowed || path.startsWith(`${allowed}?`))) {
    return response(404, { error: "proxy route not found" });
  }
  if (!RULELOCK_API_TOKEN) {
    return response(503, { error: "RULELOCK_API_TOKEN is not configured in Netlify" });
  }

  try {
    const upstream = await fetch(`${DATA_COLLECTION_URL}${path}`, {
      method: event.httpMethod,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${RULELOCK_API_TOKEN}`,
      },
      body: ["GET", "HEAD"].includes(event.httpMethod) ? undefined : event.body,
    });
    const text = await upstream.text();
    return {
      statusCode: upstream.status,
      headers: { "Content-Type": upstream.headers.get("content-type") || "application/json" },
      body: text,
    };
  } catch (error) {
    return response(502, { error: `RuleLock upstream unavailable: ${error.message}` });
  }
};

function response(statusCode, body) {
  return { statusCode, headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) };
}
