import json
with open(r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\города.json", "r", encoding="utf-8") as f:
    cities = json.load(f)
for c in cities:
    for target in [(18888, 16639), (9287, 15857), (17000, 12670), (20900, 16800), (25600, 21300), (4000, 13600)]:
        dist = ((c['x']-target[0])**2 + (c['y']-target[1])**2)**0.5
        if dist < 2000:
            print(f"{c['name']} ({c['type']}) is {dist:.0f}m from {target}")
