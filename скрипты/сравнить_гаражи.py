import re
import json

# 1. Load island garages (from дома_острова.json)
with open(r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\дома_острова.json", "r", encoding="utf-8") as f:
    island = json.load(f)

island_garages = []
for b in island:
    c = b['class'].lower()
    if 'dam' in c or 'ruin' in c:
        continue
    if c in ['land_i_garage_v1_f', 'land_i_garage_v2_f']:
        is_v1 = (c == 'land_i_garage_v1_f')
        island_garages.append({
            "class": "Land_i_Garage_V1_F" if is_v1 else "Land_i_Garage_V2_F",
            "type": "Land_i_Garage_V1_F" if is_v1 else "Land_i_Garage_V2_F",
            "source": "island",
            "tag": "Островной",
            "x": round(b['x'], 1),
            "y": round(b['y'], 1),
            "dir": round(b['yaw'], 1),
            "yaw": round(b['yaw'], 1),
            "w": 12.0,  # larger size as requested!
            "l": 16.0
        })

print(f"Island intact garages: {len(island_garages)}")

# 2. Load mission garages (from uploaded_mission.cpp)
cpp_path = r'C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\uploaded_mission.cpp'
with open(cpp_path, 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

item_blocks = re.split(r'class Item\d+', text)
mission_garages = []
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
    
    dir_m = re.search(r'angles\[\]\s*=\s*\{([0-9.,-]+),\s*([0-9.,-]+),\s*([0-9.,-]+)\}', block)
    # in Arma sqm: angles[] = {pitch, yaw, roll} (in radians or degrees? let's check!)
    yaw = 0.0
    if dir_m:
        yaw = float(dir_m.group(2))
        # If in radians (between -3.15 and 3.15):
        # Let's check angles values in mission
    
    name_m = re.search(r'name\s*=\s*"([^"]+)"', block)
    custom_name = name_m.group(1) if name_m else ""
    
    mission_garages.append({
        "class": cls,
        "type": cls,
        "source": "mission",
        "tag": "Кастомный",
        "custom_name": custom_name,
        "x": round(x, 1),
        "y": round(y, 1),
        "dir": round(yaw, 1),
        "yaw": round(yaw, 1),
        "w": 12.0,
        "l": 16.0
    })

print(f"Mission garages: {len(mission_garages)}")

# Check duplicate / close positions (< 2m):
close_count = 0
for mg in mission_garages:
    for ig in island_garages:
        dist = ((mg['x']-ig['x'])**2 + (mg['y']-ig['y'])**2)**0.5
        if dist < 2.0:
            close_count += 1
            print(f"Overlap at ({mg['x']}, {mg['y']})")
print(f"Overlaps between mission and island: {close_count}")
