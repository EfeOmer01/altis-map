import re
import json
import os
import math

mission_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\newAmazingLife.AmazingMap\mission.cpp"
out_dir = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные"
os.makedirs(out_dir, exist_ok=True)

with open(mission_path, "r", encoding="latin1") as f:
    text = f.read()

# Ключевые слова для фильтрации именно построек/структур
BUILDING_KEYWORDS = [
    "house", "shed", "shop", "factory", "station", "building", "garage", "hangar",
    "hospital", "police", "pier", "terminal", "cargo", "barracks", "bunker",
    "tower", "warehouse", "depot", "office", "villa", "slum", "supermarket",
    "fuel", "carservice", "military", "gate", "guardhouse", "radar", "dome",
    "dome", "hangar", "quarry", "substation", "transformer"
]

EXCLUDE_KEYWORDS = [
    "man", "chair", "table", "pallet", "lamp", "garbage", "item", "clutter",
    "pavements", "decal", "sign", "billboard", "infostand", "marker"
]

buildings = []

for m in re.finditer(r'class Item\d+\s*\{[^;]*dataType="Object";(.*?)(?=\n\t\tclass Item|\n\t\t\};|\Z)', text, re.DOTALL):
    block = m.group(0)
    pos_m = re.search(r'position\[\]=\{([^}]+)\};', block)
    id_m = re.search(r'\bid=(\d+);', block)
    type_m = re.search(r'type="([^"]+)";', block)
    angles_m = re.search(r'angles\[\]=\{([^}]+)\};', block)

    if not (pos_m and id_m and type_m):
        continue

    obj_id = int(id_m.group(1))
    obj_type = type_m.group(1)
    lower_type = obj_type.lower()

    # Фильтр
    is_building = any(kw in lower_type for kw in BUILDING_KEYWORDS)
    is_excluded = any(ex in lower_type for ex in EXCLUDE_KEYWORDS)

    if not is_building or is_excluded:
        continue

    pos_parts = [float(x.strip()) for x in pos_m.group(1).split(',')]
    x = round(pos_parts[0], 1)
    y = round(pos_parts[2], 1)

    yaw = 0.0
    if angles_m:
        ang_parts = [float(a.strip()) for a in angles_m.group(1).split(',')]
        if len(ang_parts) >= 2:
            yaw = round(math.degrees(ang_parts[1]), 1)

    # Примерные габариты
    w = 14.0
    l = 14.0
    if "hangar" in lower_type or "factory" in lower_type or "supermarket" in lower_type:
        w = 28.0
        l = 28.0
    elif "shed" in lower_type or "garage" in lower_type:
        w = 10.0
        l = 8.0
    elif "tower" in lower_type or "gate" in lower_type:
        w = 6.0
        l = 6.0

    buildings.append({
        "id": f"m_{obj_id}",
        "type": obj_type,
        "x": x,
        "y": y,
        "dir": yaw,
        "w": w,
        "l": l
    })

print(f"Отфильтровано релевантных построек: {len(buildings)}")

with open(os.path.join(out_dir, "постройки_миссии.json"), "w", encoding="utf-8") as f:
    json.dump(buildings, f, ensure_ascii=False)
