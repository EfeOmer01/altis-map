import re
import json

cpp_path = r'C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\uploaded_mission.cpp'
out_path = r'C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\постройки_миссии.json'

with open(cpp_path, 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Pattern for Item blocks in SQM / de-binarized CPP
# We look for class ItemX { ... dataType="Object"; ... class Attributes { ... } } or similar
# Let's find every block with garage class
item_blocks = re.split(r'class Item\d+', text)

garages = []
garage_idx = 1

for block in item_blocks:
    if 'garage' not in block.lower():
        continue
    
    # Check type
    type_m = re.search(r'type\s*=\s*"([^"]+)"', block)
    if not type_m:
        continue
    cls = type_m.group(1)
    
    # Only keep actual garage buildings
    if not any(k in cls.lower() for k in ['garage', 'i_garage_v1_f', 'i_garage_v2_f']):
        continue
        
    pos_m = re.search(r'position\[\]\s*=\s*\{([0-9.,-]+),\s*([0-9.,-]+),\s*([0-9.,-]+)\}', block)
    if not pos_m:
        continue
        
    x = float(pos_m.group(1))
    z = float(pos_m.group(2))
    y = float(pos_m.group(3))
    
    # Read name or text if any
    name_m = re.search(r'name\s*=\s*"([^"]+)"', block)
    name = name_m.group(1) if name_m else f"garage_{garage_idx}"
    
    # Read angles/dir
    dir_m = re.search(r'angles\[\]\s*=\s*\{([0-9.,-]+),\s*([0-9.,-]+),\s*([0-9.,-]+)\}', block)
    yaw = 0.0
    if dir_m:
        yaw = float(dir_m.group(2))
    
    garages.append({
        "id": f"garage_{garage_idx}",
        "class": cls,
        "name": f"Гараж #{garage_idx}",
        "x": round(x, 2),
        "y": round(y, 2),
        "z": round(z, 2),
        "dir": round(yaw, 1),
        "type": "garage",
        "owner": "",
        "squad": "",
        "password": ""
    })
    garage_idx += 1

print(f"Extracted {len(garages)} garages from mission.")
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(garages, f, ensure_ascii=False, indent=2)

print("Saved to", out_path)
