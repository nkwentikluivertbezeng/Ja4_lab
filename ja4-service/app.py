from flask import Flask, request, jsonify
import ja4  # your JA4 library

app = Flask(__name__)

@app.route("/fingerprint", methods=["POST"])
def fingerprint():
    clienthello = request.json.get("clienthello")
    ja4c = ja4.ja4c(clienthello)
    return jsonify({"ja4c": ja4c})

app.run(host="0.0.0.0", port=5001)
