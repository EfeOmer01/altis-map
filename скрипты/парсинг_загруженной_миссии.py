import re
import json

mission_path = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\uploaded_mission.cpp"
with open(mission_path, "r", encoding="latin1") as f:
    text = f.read()

print("Размер uploaded_mission.cpp:", len(text))

# 1. Поиск маркеров
markers = []
marker_matches = re.finditer(r'class Item\d+\s*\{[^;]*dataType="Marker";(.*?)(?=\n\t\tclass Item|\n\t\t\};|\Z)', text, re.DOTALL)
for m in marker_matches:
    block = m.group(0)
    pos_m = re.search(r'position\[\]=\{([^}]+)\};', block)
    name_m = re.search(r'name="([^"]+)";', block)
    text_m = re.search(r'text="([^"]*)";', block)
    type_m = re.search(r'type="([^"]*)";', block)
    color_m = re.search(r'colorName="([^"]*)";', block)

    if pos_m:
        pos_parts = [float(x.strip()) for x in pos_m.group(1).split(',')]
        name = name_m.group(1) if name_m else "Marker"
        marker_text = text_m.group(1) if text_m else ""
        m_type = type_m.group(1) if type_m else "mil_dot"
        color = color_m.group(1) if color_m else "ColorBlack"

        markers.append({
            "name": name,
            "text": marker_text,
            "type": m_type,
            "color": color,
            "x": round(pos_parts[0], 1),
            "y": round(pos_parts[2], 1)
        })

print(f"Всего маркеров в миссии: {len(markers)}")
markers_with_text = [m for m in markers if m["text"]]
print(f"Из них с текстом: {len(markers_with_text)}")
for m in markers_with_text[:10]:
    print(" ", m)

# 2. Поиск объектов гаражей
garage_objs = []
obj_matches = re.finditer(r'class Item\d+\s*\{[^;]*dataType="Object";(.*?)(?=\n\t\tclass Item|\n\t\t\};|\Z)', text, re.DOTALL)
for m in obj_matches:
    block = m.group(0)
    type_m = re.search(r'type="([^"]+)";', block)
    if not type_m:
        continue
    obj_type = type_m.group(1)
    if "garage" in obj_type.lower():
        pos_m = re.search(r'position\[\]=\{([^}]+)\};', block)
        id_m = re.search(r'\bid=(\d+);', block)
        angles_m = re.search(r'angles\[\]=\{([^}]+)\};', block)
        if pos_m and id_m:
            pos_parts = [float(x.strip()) for x in pos_m.group(1).split(',')]
            obj_id = int(id_m.group(1))
            yaw = 0.0
            if angles_m:
                import math
                ang_parts = [float(a.strip()) for a in angles_m.group(1).split(',')]
                if len(ang_parts) >= 2:
                    yaw = round(math.degrees(ang_parts[1]), 1)
            garage_objs.append({
                "id": f"garage_{obj_id}",
                "type": obj_type,
                "x": round(pos_parts[0], 1),
                "y": round(pos_parts[2], 1),
                "dir": yaw,
                "w": 12.0,
                "l": 14.0,
                "is_garage": True
            })

print(f"Найдено объектов типа garage: {len(garage_objs)}")
for g in garage_objs[:10]:
    print(" ", g)
