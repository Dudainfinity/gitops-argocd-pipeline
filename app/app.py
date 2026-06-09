import os
import socket

from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify(
        {
            "message": "Deploy via GitOps com ArgoCD!",
            "pod": socket.gethostname(),
            "version": os.environ.get("APP_VERSION", "1.0"),
        }
    )


@app.route("/healthz")
def health():
    return "ok", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
