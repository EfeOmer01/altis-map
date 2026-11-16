import re
import json

cpp_path = r'C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\uploaded_mission.cpp'
with open(cpp_path, 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Pattern for marker items with type "ellipse" or "rectangle"
item_blocks = re.split(r'class Item\d+', text)
territories = []

for block in item_blocks:
    if 'dataType="Marker"' not in block:
        continue
    
    type_m = re.search(r'type\s*=\s*"([^"]+)"', block)
    if not type_m or type_m.group(1).lower() not in ['ellipse', 'rectangle']:
        continue
        
    mtype = type_m.group(1).lower()
    
    pos_m = re.search(r'position\[\]\s*=\s*\{([0-9.,-]+),\s*([0-9.,-]+),\s*([0-9.,-]+)\}', block)
    if not pos_m: continue
    gx = float(pos_m.group(1))
    gy = float(pos_m.group(3))
    
    name_m = re.search(r'name\s*=\s*"([^"]+)"', block)
    name = name_m.group(1) if name_m else "zone"
    
    color_m = re.search(r'colorName\s*=\s*"([^"]+)"', block)
    color = color_m.group(1) if color_m else "ColorGUER"
    
    a_m = re.search(r'\ba\s*=\s*([0-9.,-]+);', block)
    b_m = re.search(r'\bb\s*=\s*([0-9.,-]+);', block)
    a = float(a_m.group(1)) if a_m else 100.0
    b = float(b_m.group(1)) if b_m else 100.0
    
    angle_m = re.search(r'angle\s*=\s*([0-9.,-]+);', block)
    angle = float(angle_m.group(1)) if angle_m else 0.0
    
    territories.append({
        "name": name,
        "type": mtype,
        "x": round(gx, 1),
        "y": round(gy, 1),
        "a": a,
        "b": b,
        "angle": angle,
        "color": color
    })

print(f"Extracted {len(territories)} territory zones:")
for t in territories:
    print(t)
