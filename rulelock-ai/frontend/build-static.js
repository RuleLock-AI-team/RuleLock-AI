const fs = require("fs");
const path = require("path");

const root = __dirname;
const output = path.resolve(root, "public");
if (path.dirname(output) !== path.resolve(root)) throw new Error("Static build output escaped frontend directory");
const assets = ["index.html", "app.js", "styles.css", "charuka.html", "mishen.html", "nihara.html", "sadini.html"];

fs.rmSync(output, { recursive: true, force: true });
fs.mkdirSync(output, { recursive: true });
for (const asset of assets) fs.copyFileSync(path.join(root, asset), path.join(output, asset));
