import json

with open(r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\дома_острова.json", "r", encoding="utf-8") as f:
    bldgs = json.load(f)

# Find bldgs around Rodopoli [18700..19000, 16500..16800]
rodo = [b for b in bldgs if 18500 <= b['x'] <= 19200 and 16500 <= b['y'] <= 16800]
print(f"Found {len(rodo)} bldgs in Rodopoli area")
for b in sorted(rodo, key=lambda x: x['x']):
    print(f"x={b['x']:.1f}, y={b['y']:.1f}, w={b['w']}, l={b['l']}, yaw={b.get('yaw', 0):.1f}")
