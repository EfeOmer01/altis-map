import urllib.request
import json

base = "http://localhost:3000"

endpoints = [
    "/api/buildings",
    "/api/island_buildings",
    "/api/cities",
    "/api/markers",
    "/api/roads",
    "/иконки/atm.png",
    "/иконки/loc_Fountain.png",
    "/иконки/amazing_marker_DP.png",
    "/"
]

for ep in endpoints:
    url = base + urllib.parse.quote(ep)
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            data = resp.read()
            print(f"[OK] {ep} -> status {resp.status}, size {len(data)} bytes")
    except Exception as e:
        print(f"[FAIL] {ep} -> {e}")
