import subprocess
import shlex
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

ALLOWED_COMMANDS = {"install", "uninstall", "list", "search", "upgrade"}


def run_winget(args: list[str]) -> dict:
    try:
        result = subprocess.run(
            ["winget"] + args,
            capture_output=True,
            text=True,
            timeout=60,
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except FileNotFoundError:
        return {"error": "winget is not available on this system", "returncode": -1}
    except subprocess.TimeoutExpired:
        return {"error": "Command timed out", "returncode": -1}


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/packages")
def list_packages():
    result = run_winget(["list"])
    return jsonify(result)


@app.get("/api/search")
def search_packages():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
    result = run_winget(["search", query])
    return jsonify(result)


@app.post("/api/install")
def install_package():
    data = request.get_json(silent=True) or {}
    package_id = (data.get("id") or "").strip()
    if not package_id:
        return jsonify({"error": "Package 'id' is required"}), 400
    result = run_winget(["install", "--id", package_id, "--silent", "--accept-package-agreements", "--accept-source-agreements"])
    return jsonify(result)


@app.post("/api/uninstall")
def uninstall_package():
    data = request.get_json(silent=True) or {}
    package_id = (data.get("id") or "").strip()
    if not package_id:
        return jsonify({"error": "Package 'id' is required"}), 400
    result = run_winget(["uninstall", "--id", package_id, "--silent"])
    return jsonify(result)


@app.post("/api/upgrade")
def upgrade_package():
    data = request.get_json(silent=True) or {}
    package_id = (data.get("id") or "").strip()
    args = ["upgrade", "--silent", "--accept-package-agreements", "--accept-source-agreements"]
    if package_id:
        args += ["--id", package_id]
    else:
        args.append("--all")
    result = run_winget(args)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
