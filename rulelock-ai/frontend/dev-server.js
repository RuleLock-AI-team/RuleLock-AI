// Local dev server: serves the static frontend AND runs the same Netlify
// function used in production, so /.netlify/functions/rulelock works on localhost
// without needing the Netlify CLI installed.
const http = require("http");
const fs = require("fs");
const path = require("path");
const { handler } = require("./netlify/functions/rulelock.js");

const PORT = process.env.PORT || 8080;
const ROOT = __dirname;

const MIME = {
  ".html": "text/html",
  ".js": "application/javascript",
  ".css": "text/css",
  ".json": "application/json",
  ".ico": "image/x-icon",
};

function serveStatic(req, res) {
  const urlPath = req.url.split("?")[0];
  const filePath = path.join(ROOT, urlPath === "/" ? "index.html" : urlPath);
  if (!filePath.startsWith(ROOT)) {
    res.writeHead(403);
    res.end("Forbidden");
    return;
  }
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404);
      res.end("Not found");
      return;
    }
    res.writeHead(200, { "Content-Type": MIME[path.extname(filePath)] || "application/octet-stream" });
    res.end(data);
  });
}

async function readBody(req) {
  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  return chunks.length ? Buffer.concat(chunks).toString("utf8") : undefined;
}

const server = http.createServer(async (req, res) => {
  if (req.url.startsWith("/.netlify/functions/rulelock")) {
    const [, query = ""] = req.url.split("?");
    const event = {
      httpMethod: req.method,
      queryStringParameters: Object.fromEntries(new URLSearchParams(query)),
      body: await readBody(req),
      headers: req.headers,
    };
    try {
      const result = await handler(event);
      res.writeHead(result.statusCode, result.headers || {});
      res.end(result.body);
    } catch (error) {
      res.writeHead(500, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ error: error.message }));
    }
    return;
  }
  serveStatic(req, res);
});

server.listen(PORT, () => {
  console.log(`RuleLock frontend running at http://localhost:${PORT}`);
  console.log(`Proxying to ${process.env.RULELOCK_API_URL || "https://rulelock-data-collection.onrender.com"}`);
  if (!process.env.RULELOCK_API_TOKEN) {
    console.log("Warning: RULELOCK_API_TOKEN is not set — protected endpoints (dashboard, audit log) will return 503.");
    console.log('Set it first: $env:RULELOCK_API_TOKEN = "<token configured on the Render service>"');
  }
});
