import re
import json
import math

mission_path = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\uploaded_mission.cpp"
with open(mission_path, "r", encoding="latin1") as f:
    text = f.read()

# Ключевые слова для зданий/построек
BUILDING_KW = [
    "house", "shed", "hangar", "factory", "barracks", "shop", "warehouse", 
    "office", "cargo", "bunker", "pier", "building", "supermarket", "garage", 
    "station", "depot", "terminal", "checkpoint", "tower", "quarry", "substation",
    "hospital", "police", "radar", "dome", "mil_barracks", "i_house", "u_house"
]

EXCLUDE_KW = [
    "chair", "table", "pallet", "lamp", "garbage", "item", "clutter",
    "pavements", "decal", "sign", "billboard", "infostand", "marker", "man"
]

# Габариты по типам (Ширина, Длина)
DIMENSIONS = {
    "hangar": (30.0, 36.0),
    "tenthangar": (24.0, 28.0),
    "factory": (26.0, 32.0),
    "supermarket": (22.0, 26.0),
    "barracks": (14.0, 24.0),
    "warehouse": (20.0, 30.0),
    "depot": (18.0, 24.0),
    "office": (16.0, 20.0),
    "shop": (12.0, 16.0),
    "house_big": (16.0, 18.0),
    "house_small": (10.0, 12.0),
    "house": (12.0, 14.0),
    "garage": (10.0, 14.0),
    "shed": (8.0, 12.0),
    "bunker": (12.0, 14.0),
    "tower": (8.0, 8.0),
    "checkpoint": (8.0, 10.0),
    "cargo": (6.0, 14.0)
}

def get_dimensions(obj_type):
    lt = obj_type.lower()
    for kw, (w, l) in DIMENSIONS.items():
        if kw in lt:
            return w, l
    return 14.0, 14.0

buildings = []

for m in re.finditer(r'class Item\d+\s*\{[^;]*dataType="Object";(.*?)(?=\n\t\tclass Item|\n\t\t\};|\Z)', text, re.DOTALL):
    block = m.group(0)
    type_m = re.search(r'type="([^"]+)";', block)
    if not type_m: continue
    obj_type = type_m.group(1)
    lt = obj_type.lower()

    if not any(kw in lt for kw in BUILDING_KW):
        continue
    if any(ex in lt for ex in EXCLUDE_KW):
        continue

    pos_m = re.search(r'position\[\]=\{([^}]+)\};', block)
    id_m = re.search(r'\bid=(\d+);', block)
    angles_m = re.search(r'angles\[\]=\{([^}]+)\};', block)

    if pos_m and id_m:
        pos_parts = [float(x.strip()) for x in pos_m.group(1).split(',')]
        obj_id = int(id_m.group(1))
        yaw = 0.0
        if angles_m:
            ang_parts = [float(a.strip()) for a in angles_m.group(1).split(',')]
            if len(ang_parts) >= 2:
                yaw = round(math.degrees(ang_parts[1]), 1)
        
        w, l = get_dimensions(obj_type)
        is_garage = "garage" in lt

        buildings.append({
            "id": f"b_{obj_id}",
            "type": obj_type,
            "x": round(pos_parts[0], 1),
            "y": round(pos_parts[2], 1),
            "dir": yaw,
            "w": w,
            "l": l,
            "is_garage": is_garage
        })

print(f"Экспортировано {len(buildings)} построек (из них гаражей: {sum(1 for b in buildings if b['is_garage'])})")

with open(r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\постройки_миссии.json", "w", encoding="utf-8") as f:
    json.dump(buildings, f, ensure_ascii=False, indent=2)

print("Файл постройки_миссии.json успешно обновлен!")
