from flask import Flask, request, jsonify
import os

app = Flask(__name__)

BLOCKLIST = os.getenv("BLOCKLIST", "").split(",")

@app.route("/check", methods=["POST"])
def check():
    ja4c = request.json.get("ja4c")
    if ja4c in BLOCKLIST:
        return jsonify({"decision": "block"})
    return jsonify({"decision": "allow"})

app.run(host="0.0.0.0", port=5002)
