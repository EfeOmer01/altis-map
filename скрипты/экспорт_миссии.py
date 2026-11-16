import re
import json
import math

mission_path = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\uploaded_mission.cpp"
with open(mission_path, "r", encoding="latin1") as f:
    text = f.read()

# 1. МАРКЕРЫ (ИКОНКИ)
markers = []
marker_matches = re.finditer(r'class Item\d+\s*\{[^;]*dataType="Marker";(.*?)(?=\n\t\tclass Item|\n\t\t\};|\Z)', text, re.DOTALL)

for m in marker_matches:
    block = m.group(0)
    pos_m = re.search(r'position\[\]=\{([^}]+)\};', block)
    name_m = re.search(r'name="([^"]+)";', block)
    text_m = re.search(r'text="([^"]*)";', block)
    type_m = re.search(r'type="([^"]*)";', block)
    color_m = re.search(r'colorName="([^"]*)";', block)

    if not pos_m:
        continue

    m_type = type_m.group(1) if type_m else "mil_dot"

    # Пропускаем только пустые невидимые триггеры движка (type="Empty")
    if m_type.lower() == "empty":
        continue

    pos_parts = [float(x.strip()) for x in pos_m.group(1).split(',')]
    name = name_m.group(1) if name_m else "Маркер"
    marker_text = text_m.group(1) if text_m else ""

    # Человекопонятное название по типу если текста нет
    if not marker_text:
        t_lower = m_type.lower()
        if "rentbase" in t_lower: marker_text = "База в аренду"
        elif "gunstore" in t_lower: marker_text = "Оружейный магазин"
        elif "policestation" in t_lower: marker_text = "Полицейский участок"
        elif "rebelcamp" in t_lower: marker_text = "Лагерь повстанцев"
        elif "aircraftgarage" in t_lower: marker_text = "Авиагараж"
        elif "garage" in t_lower: marker_text = "Гараж"
        elif "hospital" in t_lower: marker_text = "Больница"
        elif "storage" in t_lower: marker_text = "Склад"
        elif "pharmacy" in t_lower: marker_text = "Аптека"
        elif "clothes" in t_lower: marker_text = "Магазин одежды"
        elif "richcar" in t_lower: marker_text = "Элитный автосалон"
        elif "car" in t_lower: marker_text = "Автосалон"
        elif "truck" in t_lower: marker_text = "Грузовой автосалон"
        elif "pochtomat" in t_lower: marker_text = "Почтомат"
        elif "dp" in t_lower: marker_text = name.upper()
        else: marker_text = name

    color = color_m.group(1) if color_m else "ColorYellow"

    markers.append({
        "name": name,
        "text": marker_text,
        "type": m_type,
        "color": color,
        "x": round(pos_parts[0], 1),
        "y": round(pos_parts[2], 1)
    })

print(f"Экспортировано иконок/маркеров: {len(markers)}")

# 2. ОБЪЕКТЫ: ТОЛЬКО GARAGE (по требованию пользователя)
garages = []
obj_matches = re.finditer(r'class Item\d+\s*\{[^;]*dataType="Object";(.*?)(?=\n\t\tclass Item|\n\t\t\};|\Z)', text, re.DOTALL)

for m in obj_matches:
    block = m.group(0)
    type_m = re.search(r'type="([^"]+)";', block)
    if not type_m:
        continue
    obj_type = type_m.group(1)

    # Строго объекты гаражей
    if "garage" in obj_type.lower():
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
            garages.append({
                "id": f"garage_{obj_id}",
                "type": obj_type,
                "x": round(pos_parts[0], 1),
                "y": round(pos_parts[2], 1),
                "dir": yaw,
                "w": 12.0,
                "l": 14.0,
                "is_garage": True
            })

print(f"Экспортировано гаражей (всегда видимых построек): {len(garages)}")

with open(r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\маркеры_миссии.json", "w", encoding="utf-8") as f:
    json.dump(markers, f, ensure_ascii=False, indent=2)

with open(r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\постройки_миссии.json", "w", encoding="utf-8") as f:
    json.dump(garages, f, ensure_ascii=False, indent=2)

print("Файлы маркеры_миссии.json и постройки_миссии.json обновлены!")
