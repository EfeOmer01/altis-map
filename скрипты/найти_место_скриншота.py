import json

with open(r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\дома_острова.json", "r", encoding="utf-8") as f:
    bldgs = json.load(f)

# Find clusters where several buildings are clustered near each other along an E-W line
# Let's search for buildings with specific sizes or density
print(f"Total bldgs: {len(bldgs)}")

# Also let's check `данные/дороги.json` near highway segments (type 1)
with open(r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\дороги.json", "r", encoding="utf-8") as f:
    roads = json.load(f)

print(f"Total roads: {len(roads)}")
hw_roads = [r for r in roads if r.get('type') == 1]
print(f"Highway roads (type 1): {len(hw_roads)}")

# Check where the highway is nearly horizontal
for idx, r in enumerate(hw_roads):
    pts = r['pts']
    for p in pts:
        # Check if there are buildings within 50m of p
        near_b = [b for b in bldgs if abs(b['x'] - p[0]) < 60 and abs(b['y'] - p[1]) < 60]
        if len(near_b) >= 8:
            print(f"Highway road idx {idx} at pt {p} has {len(near_b)} nearby buildings!")
            # print coords of these buildings
            # break or show top 5
