import os
from flask import Flask, jsonify

def create_app():
    app = Flask(__name__)

    @app.route("/health", methods=["GET"])
    def health():
        status = os.getenv("APP_STATUS", "OK")
        if status != "OK":
            return jsonify({
                "status": "unhealthy",
                "reason": f"Invalid or faulty service state: {status}"
            }), 503
        return jsonify({"status": "healthy"}), 200

    @app.route("/version", methods=["GET"])
    def version():
        app_version = os.getenv("APP_VERSION", "1.0.0").strip()
        if not app_version or not app_version[0].isdigit() or "." not in app_version:
            return jsonify({
                "error": "Invalid APP_VERSION configuration"
            }), 500
        return jsonify({"version": app_version}), 200

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("APP_PORT", "5000"))
    app.run(host="0.0.0.0", port=port)