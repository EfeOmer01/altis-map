import json

with open(r'C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\дороги.json', 'r', encoding='utf-8') as f:
    roads = json.load(f)

print(f"Total road segments: {len(roads)}")
from collections import Counter
print("Types:", Counter(r['type'] for r in roads))

# Check total points
total_pts = sum(len(r['pts']) for r in roads)
print(f"Total road vertices: {total_pts}")

# Check geographic coverage
all_x = [pt[0] for r in roads for pt in r['pts']]
all_y = [pt[1] for r in roads for pt in r['pts']]
print(f"Roads X range: {min(all_x):.1f} to {max(all_x):.1f}")
print(f"Roads Y range: {min(all_y):.1f} to {max(all_y):.1f}")
