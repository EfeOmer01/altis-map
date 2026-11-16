import json

with open(r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\дороги.json", "r", encoding="utf-8") as f:
    roads = json.load(f)

for idx, r in enumerate(roads):
    for pt in r['pts']:
        if 18950 <= pt[0] <= 19200 and 16550 <= pt[1] <= 16750:
            print(f"Road {idx} (type {r.get('type')}) near target: {r['pts']}")
            break
