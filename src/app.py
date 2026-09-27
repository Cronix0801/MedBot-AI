"""
MedBot Web Application Server
Serves single-page diagnostic dashboard, static assets, and REST API.
"""

import os
import sys
from pathlib import Path

# Ensure src directory is in sys.path
SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from predict import bp as predict_bp

app = Flask(
    __name__,
    static_folder=str(SRC_DIR / "static"),
    static_url_path=""
)
CORS(app)

# Register the prediction blueprint
app.register_blueprint(predict_bp)

@app.route("/", methods=["GET"])
def serve_ui():
    """Serve the single-page UI."""
    return send_from_directory(app.static_folder, "index.html")

@app.route("/health", methods=["GET"])
def health_check():
    """System status and health check."""
    return jsonify({
        "status": "healthy",
        "service": "MedBot AI Healthcare Assistant",
        "version": "2.0.0"
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"==================================================")
    print(f"  MedBot AI Diagnostic Server Running")
    print(f"  URL: http://127.0.0.1:{port}")
    print(f"==================================================")
    app.run(host="0.0.0.0", port=port, debug=True)