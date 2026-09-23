
# **JA4 Firewall Lab — README**

## **Overview**
This project implements a full **JA4 TLS fingerprinting firewall** in front of a Traefik reverse‑proxy and a backend web service.  
It passively inspects TLS ClientHello packets, computes JA4/JA4C fingerprints, enforces a blocklist, and forwards allowed TLS traffic without terminating it.

The architecture:

```
Browser → TLS-Sniffer → JA4-Firewall → Traefik → Backend
```

This design mirrors real enterprise passive TLS inspection systems (FoxIO JA4, Cloudflare JA3/JA4, Zeek, Suricata).

---

## **Components**

### **1. TLS-Sniffer (Port 443)**
- Accepts incoming TLS connections.
- Peeks at the ClientHello using `MSG_PEEK`.
- Forwards raw TLS to the JA4-firewall.
- Does **not** decrypt or modify TLS.

### **2. JA4-Firewall (Port 443 → Traefik)**
- Computes JA4 fingerprints from ClientHello.
- Extracts **JA4C** (stable TLS stack identity).
- Enforces a blocklist.
- Forwards allowed TLS to Traefik unchanged.
- Blocks disallowed fingerprints by closing the connection.

### **3. Traefik Reverse Proxy**
- Terminates TLS.
- Routes HTTP traffic to backend services.
- Uses a trusted certificate signed by a local CA.

### **4. Backend (Nginx)**
- Serves a simple HTML page.
- Demonstrates successful routing through the JA4 firewall.

---

## **JA4 Fingerprinting**
A JA4 fingerprint has the format:

```
JA4_JA4C_JA4S
```

Example:

```
t13d201261_2b729b4bf6f3_36bf25f296df
```

- **JA4** → varies per connection  
- **JA4C** → stable browser identity (used for blocking)  
- **JA4S** → session-specific  

Browsers open multiple parallel TLS connections, so JA4 changes constantly.  
JA4C remains stable and is the correct value to block.

---

## **Blocklist**
The JA4-firewall reads a comma‑separated list of JA4C fingerprints from the environment:

```yaml
environment:
  - BLOCKLIST=2b729b4bf6f3,8daaf6152771
```

To block a fingerprint:

1. Look at the JA4-firewall logs:
   ```
   [JA4] Browser Fingerprint: t13d201261_2b729b4bf6f3_36bf25f296df
   ```
2. Extract the **JA4C**:
   ```
   2b729b4bf6f3
   ```
3. Add it to `BLOCKLIST`.

The firewall will immediately block all TLS connections from that TLS stack.

---

## **Trusted Certificates**
TODO!!!!

---

## **Running the Lab**

### **Start the environment**
```
docker compose up -d
```

### **Access the backend**
Visit:

```
https://secure.local
```

You should see:

```
Backend Works!
Traefik Routing Works
```

### **View JA4 fingerprints**
Check JA4-firewall logs:

```
docker logs -f ja4-firewall
```

You will see multiple fingerprints — this is normal for modern browsers.

---

## **Project Goals**
This lab demonstrates:

- Passive TLS fingerprinting (JA4)
- TLS forwarding without termination
- JA4C-based firewall enforcement
- Reverse-proxy routing with Traefik
- Trusted internal certificates
- Docker networking and service isolation

It is a realistic foundation for:

- Bot detection  
- Malware TLS fingerprinting  
- TLS stack classification  
- Zero-trust network filtering  
- Enterprise TLS inspection  

---

## **Notes**
- JA4_B is the correct fingerprint to block.  
- JA4 varies per connection and should not be used for blocking.  
- TLS is never decrypted by the firewall; only Traefik terminates TLS.  
- Multiple fingerprints per page load are normal.

---
