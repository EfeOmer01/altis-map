import json

in_path = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\дома_острова.json"
out_path = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\постройки_миссии.json"

with open(in_path, "r", encoding="utf-8") as f:
    all_bldgs = json.load(f)

# Filter ONLY intact garages:
# Land_i_garage_v1_f (new)
# Land_i_garage_v2_f (old)
# Explicitly EXCLUDE damaged (dam) and ruins

garages = []
g_idx = 1

for b in all_bldgs:
    cls_lower = b['class'].lower()
    
    # Check if damaged or ruins
    if 'dam' in cls_lower or 'ruin' in cls_lower:
        continue
        
    if cls_lower == 'land_i_garage_v1_f':
        garages.append({
            "id": f"garage_{g_idx}",
            "class": "Land_i_Garage_V1_F",
            "type": "Land_i_Garage_V1_F",
            "name": f"Гараж #{g_idx} (Новый)",
            "x": round(b['x'], 1),
            "y": round(b['y'], 1),
            "dir": round(b['yaw'], 1),
            "yaw": round(b['yaw'], 1),
            "w": 7.0,
            "l": 9.5,
            "owner": "",
            "squad": "",
            "password": ""
        })
        g_idx += 1
    elif cls_lower == 'land_i_garage_v2_f':
        garages.append({
            "id": f"garage_{g_idx}",
            "class": "Land_i_Garage_V2_F",
            "type": "Land_i_Garage_V2_F",
            "name": f"Гараж #{g_idx} (Старый)",
            "x": round(b['x'], 1),
            "y": round(b['y'], 1),
            "dir": round(b['yaw'], 1),
            "yaw": round(b['yaw'], 1),
            "w": 7.0,
            "l": 9.5,
            "owner": "",
            "squad": "",
            "password": ""
        })
        g_idx += 1

print(f"Экспортировано {len(garages)} целых гаражей с карты острова!")
v1_cnt = sum(1 for g in garages if g['class'] == 'Land_i_Garage_V1_F')
v2_cnt = sum(1 for g in garages if g['class'] == 'Land_i_Garage_V2_F')
print(f"  Новых гаражей (V1): {v1_cnt}")
print(f"  Старых гаражей (V2): {v2_cnt}")

with open(out_path, "w", encoding="utf-8") as f:
    json.dump(garages, f, ensure_ascii=False, indent=2)

print(f"Успешно сохранено в {out_path}!")
