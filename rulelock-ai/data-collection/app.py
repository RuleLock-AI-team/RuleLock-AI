import os

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from config import CAKELY_ORIGINS, PORT
from catalog import DEFAULT_PRODUCTS
from db import get_products
from routes.events import bp as events_bp

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app, origins=CAKELY_ORIGINS)
app.register_blueprint(events_bp)


@app.get("/health")
def health():
    return jsonify(status="ok"), 200


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/browse")
def browse():
    products = get_products()
    return jsonify(products or DEFAULT_PRODUCTS)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=os.environ.get("FLASK_DEBUG", "0") == "1",
    )
