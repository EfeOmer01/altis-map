import re
import math
import json

out_path = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\постройки_миссии.json"

# 1. Загружаем островные гаражи из дома_острова.json
with open(r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\дома_острова.json", "r", encoding="utf-8") as f:
    island = json.load(f)

garages = []

# Островные гаражи
island_count = 0
for b in island:
    c = b['class'].lower()
    if 'dam' in c or 'ruin' in c:
        continue
    if c in ['land_i_garage_v1_f', 'land_i_garage_v2_f']:
        is_v1 = (c == 'land_i_garage_v1_f')
        island_count += 1
        garages.append({
            "id": f"garage_isl_{b['id']}",
            "class": "Land_i_Garage_V1_F" if is_v1 else "Land_i_Garage_V2_F",
            "type": "Land_i_Garage_V1_F" if is_v1 else "Land_i_Garage_V2_F",
            "source": "island",
            "name": f"Гараж {b['id']} (Остров, {'Новый' if is_v1 else 'Старый'})",
            "x": round(b['x'], 1),
            "y": round(b['y'], 1),
            "z": 0.0,
            "dir": round(b['yaw'], 1),
            "yaw": round(b['yaw'], 1),
            "w": 16.0,  # Увеличенный размер для отличной видимости
            "l": 18.0,
            "owner": "",
            "squad": "",
            "password": ""
        })

print(f"Экспортировано {island_count} целых гаражей острова.")

# 2. Загружаем кастомные гаражи из uploaded_mission.cpp
cpp_path = r'C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\uploaded_mission.cpp'
with open(cpp_path, 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

item_blocks = re.split(r'class Item\d+', text)
mission_count = 0

for block in item_blocks:
    if 'garage' not in block.lower():
        continue
    type_m = re.search(r'type\s*=\s*"([^"]+)"', block)
    if not type_m:
        continue
    cls = type_m.group(1)
    if not any(k in cls.lower() for k in ['garage', 'i_garage_v1_f', 'i_garage_v2_f']):
        continue
    if 'marker' in cls.lower():
        continue
        
    pos_m = re.search(r'position\[\]\s*=\s*\{([0-9.,-]+),\s*([0-9.,-]+),\s*([0-9.,-]+)\}', block)
    if not pos_m:
        continue
    x = float(pos_m.group(1))
    z = float(pos_m.group(2))
    y = float(pos_m.group(3))
    
    # Eden id
    id_m = re.search(r'\bid\s*=\s*(\d+);', block)
    obj_id = id_m.group(1) if id_m else str(1000 + mission_count)
    
    # Angles (yaw is the 2nd value in radians)
    dir_m = re.search(r'angles\[\]\s*=\s*\{([0-9.,-]+),\s*([0-9.,-]+),\s*([0-9.,-]+)\}', block)
    yaw_deg = 0.0
    if dir_m:
        yaw_rad = float(dir_m.group(2))
        yaw_deg = (yaw_rad * 180.0 / math.pi) % 360.0
    
    # Name or text
    name_m = re.search(r'name\s*=\s*"([^"]+)"', block)
    custom_label = name_m.group(1) if name_m else f"Миссия #{obj_id}"
    
    label_type = "Новый" if "v1" in cls.lower() else ("Старый" if "v2" in cls.lower() else "Навес")
    
    mission_count += 1
    garages.append({
        "id": f"garage_{obj_id}",
        "class": cls,
        "type": cls,
        "source": "mission",
        "name": f"Гараж #{obj_id} (Кастомный, {label_type})",
        "x": round(x, 1),
        "y": round(y, 1),
        "z": round(z, 1),
        "dir": round(yaw_deg, 1),
        "yaw": round(yaw_deg, 1),
        "w": 16.0,
        "l": 18.0,
        "owner": "",
        "squad": "",
        "password": ""
    })

print(f"Экспортировано {mission_count} кастомных гаражей из миссии.")
print(f"ИТОГО всех гаражей на карте: {len(garages)}")

with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(garages, f, ensure_ascii=False, indent=2)

print(f"Успешно сохранено в {out_path}!")
