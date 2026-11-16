import json

with open(r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\дороги.json", "r", encoding="utf-8") as f:
    roads = json.load(f)

for idx, r in enumerate(roads):
    pts = r['pts']
    # Check if road passes near 19000, 16600
    near = [p for p in pts if 18700 <= p[0] <= 19300 and 16500 <= p[1] <= 16800]
    if len(near) >= 2:
        print(f"Road #{idx}: type={r.get('type')}, pts_count={len(pts)}")
        print(f"  first: {pts[0]}, last: {pts[-1]}")
        print(f"  sample: {near[:4]}")
