from flask import Flask, request, jsonify
from python.ja4 import ja4_fingerprint


app = Flask(__name__)

@app.route("/fingerprint", methods=["POST"])
def fingerprint():
    clienthello = request.json.get("clienthello")

    # Compute JA4 fingerprint using FoxIO code
    ja4c = ja4_fingerprint(clienthello)

    return jsonify({"ja4c": ja4c})

app.run(host="0.0.0.0", port=5001)
