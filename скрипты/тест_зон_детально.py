import re

mission_path = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\uploaded_mission.cpp"
with open(mission_path, "r", encoding="latin1") as f:
    text = f.read()

matches = list(re.finditer(r'class Item\d+\s*\{[^;]*dataType="Marker";(.*?)(?=\n\t\tclass Item|\n\t\t\};|\Z)', text, re.DOTALL))
print("Total marker matches:", len(matches))

zones = []
for m in matches:
    b = m.group(0)
    type_m = re.search(r'type="([^"]*)";', b)
    if not type_m: continue
    t = type_m.group(1).lower()
    if t in ['ellipse', 'rectangle']:
        name_m = re.search(r'name="([^"]*)";', b)
        pos_m = re.search(r'position\[\]=\{([^}]+)\};', b)
        a_m = re.search(r'\ba=([0-9.,-]+);', b)
        b_m = re.search(r'\bb=([0-9.,-]+);', b)
        col_m = re.search(r'colorName="([^"]*)";', b)
        
        name = name_m.group(1) if name_m else "zone"
        parts = [float(x.strip()) for x in pos_m.group(1).split(',')] if pos_m else [0, 0, 0]
        a = float(a_m.group(1)) if a_m else 100.0
        b_rad = float(b_m.group(1)) if b_m else 100.0
        col = col_m.group(1) if col_m else "ColorGUER"
        
        zones.append({
            "name": name,
            "type": t,
            "x": parts[0],
            "y": parts[2],
            "a": a,
            "b": b_rad,
            "color": col
        })

print(f"Total zones ({len(zones)}):")
for z in zones:
    print(z)
