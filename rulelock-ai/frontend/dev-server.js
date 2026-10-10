// Local development server for the static frontend.
const http = require("http");
const fs = require("fs");
const path = require("path");

const PORT = process.env.PORT || 8080;
const ROOT = __dirname;
const STATIC_ASSETS = new Set([
  "index.html", "app.js", "styles.css", "charuka.html", "mishen.html", "nihara.html", "sadini.html",
]);

const MIME = {
  ".html": "text/html",
  ".js": "application/javascript",
  ".css": "text/css",
  ".json": "application/json",
  ".ico": "image/x-icon",
};

function serveStatic(req, res) {
  const urlPath = req.url.split("?")[0];
  const relativePath = urlPath === "/" ? "index.html" : urlPath.replace(/^\//, "");
  if (!STATIC_ASSETS.has(relativePath)) {
    res.writeHead(404);
    res.end("Not found");
    return;
  }
  const filePath = path.join(ROOT, relativePath);
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

const server = http.createServer((req, res) => {
  serveStatic(req, res);
});

server.listen(PORT, () => {
  console.log(`RuleLock frontend running at http://localhost:${PORT}`);
  console.log(`Proxying to ${process.env.RULELOCK_API_URL || "https://rulelock-data-collection.onrender.com"}`);
  if (!process.env.RULELOCK_API_TOKEN) {
    console.log("Warning: dashboard proxy is unavailable until its backend token and dashboard login settings are configured.");
  }
});
