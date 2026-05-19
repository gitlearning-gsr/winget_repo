import json
import os
from flask import Flask, jsonify, request

app = Flask(__name__)

BROCHURES_FILE = os.path.join(os.path.dirname(__file__), "brochures.json")

with open(BROCHURES_FILE) as f:
    BROCHURES = json.load(f)


def _matches(brochure: dict, query: str, filters: dict) -> bool:
    for key, value in filters.items():
        if brochure.get(key, "").lower() != value.lower():
            return False
    if query:
        searchable = " ".join(str(v) for v in brochure.values()).lower()
        if query.lower() not in searchable:
            return False
    return True


@app.route("/brochures", methods=["GET"])
def list_brochures():
    """Return all available car brochures, with optional filtering."""
    query = request.args.get("q", "").strip()
    filters = {}
    for field in ("make", "model", "fuel_type", "body_style"):
        value = request.args.get(field, "").strip()
        if value:
            filters[field] = value

    results = [b for b in BROCHURES if _matches(b, query, filters)]
    return jsonify({"count": len(results), "results": results})


@app.route("/brochures/<int:brochure_id>", methods=["GET"])
def get_brochure(brochure_id: int):
    """Return a single brochure by its ID."""
    for brochure in BROCHURES:
        if brochure["id"] == brochure_id:
            return jsonify(brochure)
    return jsonify({"error": "Brochure not found"}), 404


@app.route("/brochures/search", methods=["GET"])
def search_brochures():
    """Full-text search across all brochure fields."""
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "Missing query parameter 'q'"}), 400

    results = [b for b in BROCHURES if query.lower() in " ".join(str(v) for v in b.values()).lower()]
    return jsonify({"query": query, "count": len(results), "results": results})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
