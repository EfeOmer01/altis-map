import re
from collections import Counter

with open(r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\uploaded_mission.cpp", "r", encoding="latin1") as f:
    text = f.read()

types = []
for m in re.finditer(r'dataType="Object";.*?type="([^"]+)";', text, re.DOTALL):
    types.append(m.group(1))

print(f"Всего объектов в загруженной миссии: {len(types)}")
cnt = Counter(types)
print("Топ-30 типов объектов:")
for t, c in cnt.most_common(30):
    print(f"  {t}: {c}")

# Ищем постройки: house, shed, hangar, factory, barracks, shop, warehouse, office, cargo, bunker, pier, building
building_keywords = ["house", "shed", "hangar", "factory", "barracks", "shop", "warehouse", "office", "cargo", "bunker", "pier", "building", "supermarket", "garage", "station", "depot", "terminal", "checkpoint", "tower"]
buildings = [t for t in types if any(kw in t.lower() for kw in building_keywords)]
print(f"Всего построек в миссии: {len(buildings)}")
