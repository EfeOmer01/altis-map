import re
import json
import math

markers_path = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\маркеры_миссии.json"
mission_cpp = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\uploaded_mission.cpp"
territories_path = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\территории.json"

# 1. Читаем и категоризируем маркеры
with open(markers_path, "r", encoding="utf-8") as f:
    markers = json.load(f)

def categorize(m):
    t = m.get('type', '').lower()
    name = m.get('name', '').lower()
    text = m.get('text', '').lower()

    # 1. DP (Курьерские точки)
    if 'dp' in t or name.startswith('dp') or 'dp' in text:
        return 'dp'

    # 2. Нелегальные точки (Наркотики, уран, контрабанда, перебивка)
    if ('illegal' in t or 'illegal' in name or 'cocaine' in t or 'heroine' in t or 
        'canabis' in t or 'weed' in t or 'gera' in t or 'narko' in t or 'drug' in t or 
        'uran' in t or 'perebivka' in t or 'moneylaundering' in t or 'slaver' in t):
        return 'illegal'

    # 3. Базы и особняки (Группировки, сквады, базы)
    if t.startswith('amazing_group_') or 'rebelcamp' in t or 'rentbase' in t or 'база' in text or 'особняк' in text or 'мафия' in text:
        return 'bases'

    # 4. Недвижимость (Гаражи, аренда)
    if 'garage' in t or 'garage' in name or 'гараж' in text or 'недвиж' in text:
        return 'realestate'

    # 5. Территории
    if t in ['ellipse', 'rectangle'] or 'zone' in name or 'зона' in text:
        return 'territories'

    # 6. Ресурсы (Добыча первичных ресурсов)
    if any(k in t for k in [
        'oil', 'salt', 'sand', 'water', 'beans', 'minerals', 'jasperquartz', 
        'gornorudka', 'fish', 'meteorite', 'wastes', 'huntarea'
    ]) and not any(k in t for k in ['factory', 'sell', 'store']):
        return 'resources'

    # 7. Маршруты добычи (Заводы, фабрики, сбыт, переработка, лицензии)
    if any(k in t for k in [
        'factory', 'sell', 'license', 'delivery', 'storage', 'depot'
    ]):
        return 'routes'

    # 8. Магазины (Транспорт, оружие, одежда, еда, аптеки)
    if any(k in t for k in [
        'car', 'truck', 'richcar', 'conceptcar', 'motorcycle', 'gunstore', 
        'clothes', 'grocery', 'univermag', 'marketplace', 'pharmacy', 
        'garden_shop', 'beautysaloon', 'piercing', 'mask', 'drivingschool'
    ]):
        return 'shops'

    # 9. Инфраструктура (Банкоматы, родники, банки, полиция, больницы, порты)
    if any(k in t for k in [
        'atm', 'loc_fountain', 'bank', 'hospital', 'policestation', 'jail', 
        'gasstation', 'parkingfine', 'pochtomat', 'government', 'harbor', 
        'boat', 'airplane', 'helicopter', 'bridge', 'checkpoing'
    ]) or 'atm' in name or 'банкомат' in text or 'родник' in text:
        return 'infra'

    # 10. Прочее
    return 'other'

for m in markers:
    m['category'] = categorize(m)

with open(markers_path, "w", encoding="utf-8") as f:
    json.dump(markers, f, ensure_ascii=False, indent=2)

print(f"Обновлено категорий для {len(markers)} маркеров!")

# 2. Экспорт зон и территорий из uploaded_mission.cpp
with open(mission_cpp, "r", encoding="latin1") as f:
    text = f.read()

matches = list(re.finditer(r'class Item\d+\s*\{[^;]*dataType="Marker";(.*?)(?=\n\t\tclass Item|\n\t\t\};|\Z)', text, re.DOTALL))
territories = []

color_map = {
    'ColorGUER': '#22c55e',   # Зеленый (сейфзоны)
    'ColorRed': '#ef4444',    # Красный (радиация / охота)
    'ColorYellow': '#eab308', # Желтый
    'ColorCIV': '#3b82f6',    # Синий
    'ColorWEST': '#3b82f6',
    'ColorEAST': '#ef4444'
}

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
        angle_m = re.search(r'angle=([0-9.,-]+);', b)
        col_m = re.search(r'colorName="([^"]*)";', b)
        
        name = name_m.group(1) if name_m else "zone"
        parts = [float(x.strip()) for x in pos_m.group(1).split(',')] if pos_m else [0, 0, 0]
        a = float(a_m.group(1)) if a_m else 100.0
        b_rad = float(b_m.group(1)) if b_m else 100.0
        angle = float(angle_m.group(1)) if angle_m else 0.0
        col_name = col_m.group(1) if col_m else "ColorGUER"
        
        # Красивое название
        label = name
        if 'safe_zone' in name: label = f"Безопасная зона ({name})"
        elif 'uran_zone' in name: label = "Зона радиации / Уран"
        elif 'hunting_zone' in name: label = "Охотничьи угодья"
        
        territories.append({
            "name": name,
            "label": label,
            "shape": t,
            "x": round(parts[0], 1),
            "y": round(parts[2], 1),
            "radius_x": a,
            "radius_y": b_rad,
            "angle": angle,
            "color": color_map.get(col_name, '#22c55e'),
            "category": "territories"
        })

print(f"Экспортировано {len(territories)} зон территорий!")
with open(territories_path, "w", encoding="utf-8") as f:
    json.dump(territories, f, ensure_ascii=False, indent=2)

print(f"Зоны сохранены в {territories_path}!")
