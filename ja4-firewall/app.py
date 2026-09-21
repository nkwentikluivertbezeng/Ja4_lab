# from flask import Flask, request, jsonify
# from python.ja4 import ja4_fingerprint


# app = Flask(__name__)

# @app.route("/fingerprint", methods=["POST"])
# def fingerprint():
#     clienthello = request.json.get("clienthello")

#     # Compute JA4 fingerprint using FoxIO code
#     ja4c = ja4_fingerprint(clienthello)

#     return jsonify({"ja4c": ja4c})

# app.run(host="0.0.0.0", port=5001)


import os
import requests
import socket
import threading
import binascii
from flask import Flask, request, Response
from python.ja4 import ja4_fingerprint
import socket
import ssl
app = Flask(__name__)

TRAefik_URL = os.getenv("TRAEFIK_URL", "http://reverse-proxy:80")
BLOCKLIST = os.getenv("BLOCKLIST", "").split(",")

def forward_tls(client_conn):
    import socket
    import selectors

    sel = selectors.DefaultSelector()

    upstream = socket.create_connection(("reverse-proxy", 443))
    upstream.setblocking(False)
    client_conn.setblocking(False)

    sel.register(client_conn, selectors.EVENT_READ, data=upstream)
    sel.register(upstream, selectors.EVENT_READ, data=client_conn)

    while True:
        events = sel.select(timeout=1)
        if not events:
            continue

        for key, _ in events:
            src = key.fileobj
            dst = key.data

            try:
                data = src.recv(4096)
                if not data:
                    sel.unregister(src)
                    sel.unregister(dst)
                    src.close()
                    dst.close()
                    return
                dst.sendall(data)
            except Exception:
                sel.unregister(src)
                sel.unregister(dst)
                src.close()
                dst.close()
                return



def tls_listener():
    sock = socket.socket()
    sock.bind(("0.0.0.0", 443))
    sock.listen(5)
    print("[JA4] TLS listener active on port 443")

    while True:
        conn, addr = sock.accept()
        print(f"[JA4] TLS connection from {addr}")

        clienthello_raw = conn.recv(4096, socket.MSG_PEEK)
        print("[JA4] Raw ClientHello bytes:", clienthello_raw[:64])

        clienthello_hex = binascii.hexlify(clienthello_raw).decode("ascii")
        print("[JA4] ClientHello HEX:", clienthello_hex[:128])

        fp = ja4_fingerprint(clienthello_hex)
        print("[JA4] Browser Fingerprint:", fp)

        forward_tls(conn)


# Start TLS listener in background
threading.Thread(target=tls_listener, daemon=True).start()


def sniff_tls_clienthello():
    sock = socket.socket()
    sock.bind(("0.0.0.0", 443))
    sock.listen(5)

    while True:
        conn, addr = sock.accept()

        # Peek at ClientHello without consuming it
        clienthello_raw = conn.recv(4096, socket.MSG_PEEK)

        # Convert raw bytes → hex string
        clienthello_hex = binascii.hexlify(clienthello_raw).decode("ascii")

        # Compute JA4 fingerprint
        fp = ja4_fingerprint(clienthello_hex)
        print("[JA4] Browser Fingerprint:", fp)

        # Forward raw TLS to Traefik
        forward_tls(conn)



def forward_to_traefik(req):
    # Print incoming Host header
    print(f"[JA4] Incoming Host header: {req.headers.get('Host')}")

    safe_headers = {}

    for k, v in req.headers.items():
        kl = k.lower()

        # DO NOT remove Host header when forwarding to Traefik
        if kl in ["connection", "accept-encoding", "content-length"]:
            continue

        safe_headers[k] = v

    # Print forwarded Host header
    print(f"[JA4] Forwarding Host header: {safe_headers.get('Host')}")

    resp = requests.request(
        method=req.method,
        url=TRAefik_URL,
        headers=safe_headers,
        data=req.get_data(),
        allow_redirects=False,
    )

    return Response(resp.content, status=resp.status_code, headers=dict(resp.headers))



@app.route("/", methods=["GET", "POST"])
def firewall():
    clienthello_hex = request.headers.get("X-ClientHello")

    if not clienthello_hex:
        print("[JA4] No ClientHello provided — allowing request")
        return forward_to_traefik(request)

    fp = ja4_fingerprint(clienthello_hex)
    print("this is the fingerprint")
    print(f"[JA4] this is the Fingerprint: {fp}")

    if fp in BLOCKLIST:
        print(f"[JA4] BLOCKED: {fp}")
        return Response("Blocked by JA4 firewall", status=403)

    return forward_to_traefik(request)
@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    print("hello world")
    return firewall()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
