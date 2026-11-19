# -*- coding: utf-8 -*-
import os
import shutil
import struct
import math
import json
import armaio.binary as b

uploaded_sqm = r"C:\Users\efeom\.gemini\antigravity\brain\aa98ea14-c161-44e8-a122-0dc0ebe5fba5\.user_uploaded\media_1795127165664_e2aff826.sqm"
data_dir = r"E:\карта-алтис\данные"
icons_dir = r"E:\карта-алтис\веб\иконки"

target_sqm = os.path.join(data_dir, "mission.sqm")
buildings_json_path = os.path.join(data_dir, "постройки_миссии.json")
island_buildings_path = os.path.join(data_dir, "дома_острова.json")
markers_json_path = os.path.join(data_dir, "маркеры_миссии.json")
territories_json_path = os.path.join(data_dir, "территории.json")
dict_defs_path = os.path.join(data_dir, "amazing_markers_dict.json")

# 0. Backup uploaded sqm to data/mission.sqm
print("1. Copying mission.sqm to data folder...")
shutil.copy2(uploaded_sqm, target_sqm)
print(f"   Saved copy to {target_sqm} ({os.path.getsize(target_sqm)} bytes)")

# 1. Binary raP parser
def read_array(f):
    n_elems = b.read_compressed_uint(f)
    elems = []
    for _ in range(n_elems):
        stype = struct.unpack('B', f.read(1))[0]
        if stype in (0, 4):
            elems.append(b.read_asciiz(f))
        elif stype == 1:
            elems.append(struct.unpack('<f', f.read(4))[0])
        elif stype == 2:
            elems.append(struct.unpack('<i', f.read(4))[0])
        elif stype == 3:
            elems.append(read_array(f))
        else:
            raise ValueError(f"Unknown array elem stype: {stype} at {f.tell()}")
    return elems

def parse_class_body(f, offset=None):
    if offset is not None:
        f.seek(offset)
    inherited = b.read_asciiz(f)
    n_entries = b.read_compressed_uint(f)
    cls_dict = {}
    entries = []
    for _ in range(n_entries):
        etype = struct.unpack('B', f.read(1))[0]
        if etype == 0:
            cname = b.read_asciiz(f)
            boffset = struct.unpack('<I', f.read(4))[0]
            entries.append((0, cname, boffset))
        elif etype == 1:
            stype = struct.unpack('B', f.read(1))[0]
            vname = b.read_asciiz(f)
            if stype in (0, 4):
                val = b.read_asciiz(f)
            elif stype == 1:
                val = struct.unpack('<f', f.read(4))[0]
            elif stype == 2:
                val = struct.unpack('<i', f.read(4))[0]
            entries.append((1, vname, val))
        elif etype == 2:
            aname = b.read_asciiz(f)
            arr = read_array(f)
            entries.append((2, aname, arr))
        elif etype in (3, 4):
            cname = b.read_asciiz(f)
            entries.append((etype, cname, None))
        elif etype == 5:
            flags = struct.unpack('<I', f.read(4))[0]
            aname = b.read_asciiz(f)
            arr = read_array(f)
            entries.append((5, aname, (flags, arr)))
        else:
            raise ValueError(f"Unknown etype {etype} at {f.tell()}")
            
    for item in entries:
        kind = item[0]
        if kind == 0:
            cls_dict[item[1]] = parse_class_body(f, item[2])
        elif kind == 1:
            cls_dict[item[1]] = item[2]
        elif kind in (2, 5):
            cls_dict[item[1]] = item[2]
    return cls_dict

print("2. Parsing mission.sqm tree...")
with open(uploaded_sqm, "rb") as f:
    f.seek(16)
    root = parse_class_body(f)
print("   Tree parsed successfully!")

# Recursive entity collector
all_objects = []
all_markers = []

def collect_entities(d):
    if not isinstance(d, dict): return
    dt = d.get('dataType')
    if dt == 'Object':
        all_objects.append(d)
    elif dt == 'Marker':
        all_markers.append(d)
    if 'Entities' in d and isinstance(d['Entities'], dict):
        for k, v in d['Entities'].items():
            collect_entities(v)

if 'Mission' in root and 'Entities' in root['Mission']:
    for k, v in root['Mission']['Entities'].items():
        collect_entities(v)

print(f"   Collected {len(all_objects)} objects and {len(all_markers)} markers.")

# ======================================================================
# 3. BUILDINGS / GARAGES EXPORT
# ======================================================================
print("\n3. Processing garages...")
with open(island_buildings_path, "r", encoding="utf-8") as f:
    island = json.load(f)

garages = []
island_count = 0
for b_isl in island:
    c = b_isl['class'].lower()
    if 'dam' in c or 'ruin' in c:
        continue
    if c in ['land_i_garage_v1_f', 'land_i_garage_v2_f']:
        is_v1 = (c == 'land_i_garage_v1_f')
        island_count += 1
        garages.append({
            "id": f"garage_isl_{b_isl['id']}",
            "class": "Land_i_Garage_V1_F" if is_v1 else "Land_i_Garage_V2_F",
            "type": "Land_i_Garage_V1_F" if is_v1 else "Land_i_Garage_V2_F",
            "source": "island",
            "name": f"Гараж {b_isl['id']} (Остров, {'Новый' if is_v1 else 'Старый'})",
            "x": round(b_isl['x'], 1),
            "y": round(b_isl['y'], 1),
            "z": 0.0,
            "dir": round(b_isl['yaw'], 1),
            "yaw": round(b_isl['yaw'], 1),
            "w": 16.0,
            "l": 18.0,
            "owner": "",
            "squad": "",
            "password": ""
        })
print(f"   Exported {island_count} island garages.")

mission_garages_count = 0
for obj in all_objects:
    cls = obj.get('type', '')
    if not any(k in cls.lower() for k in ['garage', 'i_garage_v1_f', 'i_garage_v2_f']):
        continue
    if 'marker' in cls.lower():
        continue
        
    pos = obj.get('PositionInfo', {}).get('position', [0, 0, 0])
    angles = obj.get('PositionInfo', {}).get('angles', [0, 0, 0])
    
    gx = round(pos[0], 1)
    gz = round(pos[1], 1)
    gy = round(pos[2], 1)
    
    yaw_rad = float(angles[1]) if len(angles) > 1 else 0.0
    yaw_deg = round((yaw_rad * 180.0 / math.pi) % 360.0, 1)
    
    obj_id = str(obj.get('id', f'custom_{mission_garages_count}'))
    label_type = "Новый" if "v1" in cls.lower() else ("Старый" if "v2" in cls.lower() else "Навес")
    
    mission_garages_count += 1
    garages.append({
        "id": f"garage_{obj_id}",
        "class": cls,
        "type": cls,
        "source": "mission",
        "name": f"Гараж #{obj_id} (Кастомный, {label_type})",
        "x": gx,
        "y": gy,
        "z": gz,
        "dir": yaw_deg,
        "yaw": yaw_deg,
        "w": 16.0,
        "l": 18.0,
        "owner": "",
        "squad": "",
        "password": ""
    })

print(f"   Exported {mission_garages_count} mission custom garages.")
print(f"   Total garages in постройки_миссии.json: {len(garages)}")

with open(buildings_json_path, "w", encoding="utf-8") as f:
    json.dump(garages, f, ensure_ascii=False, indent=2)
print(f"   Successfully wrote {buildings_json_path}")

# ======================================================================
# 4. MARKERS EXPORT
# ======================================================================
print("\n4. Processing markers...")
with open(dict_defs_path, "r", encoding="utf-8") as f:
    dict_defs = json.load(f)

available_icons = {f.lower(): f for f in os.listdir(icons_dir)}

def find_icon(icon_name_or_path):
    if not icon_name_or_path:
        return ""
    base = os.path.basename(icon_name_or_path).replace('.paa', '').replace('.png', '')
    png_name = f"{base}.png".lower()
    if png_name in available_icons:
        return f"/icons/{available_icons[png_name]}"
    return ""

def categorize(m_type, name, text):
    t = m_type.lower()
    n = name.lower()
    tx = text.lower()

    # 1. DP
    if 'dp' in t or n.startswith('dp') or 'dp' in tx:
        return 'dp'

    # 2. Нелегал
    if any(k in t or k in n or k in tx for k in [
        'illegal', 'cocaine', 'heroine', 'canabis', 'weed', 'gera', 'narko', 'drug',
        'uran', 'perebivka', 'moneylaundering', 'slaver', 'нелегал', 'уран', 'кокаин', 'героин'
    ]):
        return 'illegal'

    # 3. Базы и особняки
    if t.startswith('amazing_group_') or any(k in t or k in n or k in tx for k in [
        'rebelcamp', 'rentbase', 'база', 'особняк', 'мафия', 'групп'
    ]):
        return 'bases'

    # 4. Недвижимость
    if any(k in t or k in n or k in tx for k in ['garage', 'гараж', 'недвиж', 'realtor', 'estate']):
        return 'realestate'

    # 5. Территории
    if t in ['ellipse', 'rectangle'] or 'zone' in n or 'зона' in tx:
        return 'territories'

    # 6. Ресурсы
    if any(k in t or k in n or k in tx for k in [
        'oil', 'salt', 'sand', 'water', 'beans', 'minerals', 'jasperquartz', 
        'gornorudka', 'fish', 'meteorite', 'wastes', 'huntarea', 'нефть', 'соль', 'песок', 'руда', 'алмаз'
    ]) and not any(k in t or k in n or k in tx for k in ['factory', 'sell', 'store', 'перераб', 'завод']):
        return 'resources'

    # 7. Маршруты добычи
    if any(k in t or k in n or k in tx for k in [
        'factory', 'sell', 'license', 'delivery', 'storage', 'depot', 'завод', 'фабрика', 'сбыт', 'переработка', 'лиценз'
    ]):
        return 'routes'

    # 8. Магазины
    if any(k in t or k in n or k in tx for k in [
        'car', 'truck', 'richcar', 'conceptcar', 'motorcycle', 'gunstore', 
        'clothes', 'grocery', 'univermag', 'marketplace', 'pharmacy', 
        'garden_shop', 'beautysaloon', 'piercing', 'mask', 'drivingschool',
        'автосалон', 'оружие', 'одежда', 'магазин', 'рынок', 'аптека'
    ]):
        return 'shops'

    # 9. Инфраструктура
    if any(k in t or k in n or k in tx for k in [
        'atm', 'loc_fountain', 'bank', 'hospital', 'policestation', 'jail', 
        'gasstation', 'parkingfine', 'pochtomat', 'government', 'harbor', 
        'boat', 'airplane', 'helicopter', 'bridge', 'checkpoing', 'fountain',
        'банкомат', 'родник', 'банк', 'больница', 'полиция', 'заправка', 'порт'
    ]):
        return 'infra'

    return 'other'

markers_out = []
for m in all_markers:
    m_type = m.get('type', 'mil_dot')
    if m_type.lower() == 'empty':
        continue
    if m_type.lower() in ['ellipse', 'rectangle']:
        continue
        
    pos = m.get('position', [0, 0, 0])
    name = m.get('name', 'Маркер')
    raw_text = m.get('text') or ''
    
    dict_info = dict_defs.get(m_type, {})
    dict_name = dict_info.get("name", "")
    dict_icon = dict_info.get("icon", "")

    icon_url = find_icon(dict_icon)
    if not icon_url:
        icon_url = find_icon(m_type)

    if 'atm' in name.lower() or 'atm' in m_type.lower():
        display_text = "Банкомат"
        icon_url = "/icons/atm.png"
    elif name == 'marker_286' or 'fountain' in m_type.lower():
        display_text = "Родник"
        icon_url = "/icons/loc_Fountain.png"
    elif raw_text.startswith("DP") or name.lower().startswith("dp"):
        display_text = raw_text if raw_text else name.upper()
        icon_url = "/icons/amazing_marker_DP.png"
    elif raw_text:
        display_text = raw_text
    elif dict_name:
        display_text = dict_name
    else:
        display_text = name

    cat = categorize(m_type, name, display_text)
    color = m.get('colorName', 'ColorYellow')

    markers_out.append({
        "name": name,
        "text": display_text,
        "type": m_type,
        "icon": icon_url,
        "color": color,
        "x": round(pos[0], 1),
        "y": round(pos[2], 1),
        "category": cat
    })

print(f"   Exported {len(markers_out)} active markers.")
cats = {}
for m in markers_out:
    cats[m['category']] = cats.get(m['category'], 0) + 1
print("   Category distribution:", cats)

with open(markers_json_path, "w", encoding="utf-8") as f:
    json.dump(markers_out, f, ensure_ascii=False, indent=2)
print(f"   Successfully wrote {markers_json_path}")

# ======================================================================
# 5. TERRITORIES EXPORT
# ======================================================================
print("\n5. Processing territories...")
color_map = {
    'ColorGUER': '#22c55e',
    'ColorRed': '#ef4444',
    'ColorYellow': '#eab308',
    'ColorCIV': '#3b82f6',
    'ColorWEST': '#3b82f6',
    'ColorEAST': '#ef4444'
}

territories_out = []
for m in all_markers:
    t = m.get('type', '').lower()
    if t not in ['ellipse', 'rectangle']:
        continue
        
    pos = m.get('position', [0, 0, 0])
    name = m.get('name', 'zone')
    a = float(m.get('a', 100.0))
    b_rad = float(m.get('b', 100.0))
    angle = float(m.get('angle', 0.0))
    col_name = m.get('colorName', 'ColorGUER')
    
    label = name
    if 'safe_zone' in name: label = f"Безопасная зона ({name})"
    elif 'uran_zone' in name: label = "Зона радиации / Уран"
    elif 'hunting_zone' in name: label = "Охотничьи угодья"
    
    territories_out.append({
        "name": name,
        "label": label,
        "shape": t,
        "x": round(pos[0], 1),
        "y": round(pos[2], 1),
        "radius_x": a,
        "radius_y": b_rad,
        "angle": angle,
        "color": color_map.get(col_name, '#22c55e'),
        "category": "territories"
    })

print(f"   Exported {len(territories_out)} territories.")
with open(territories_json_path, "w", encoding="utf-8") as f:
    json.dump(territories_out, f, ensure_ascii=False, indent=2)
print(f"   Successfully wrote {territories_json_path}")

print("\n--- ALL DATA UPDATED SUCCESSFULLY! ---")
