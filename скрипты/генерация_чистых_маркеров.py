# -*- coding: utf-8 -*-
import os
import re
import json

mission_path = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\uploaded_mission.cpp"
dict_path = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\amazing_markers_dict.json"
icons_dir = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\веб\иконки"
output_path = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\маркеры_миссии.json"

with open(mission_path, "r", encoding="latin1") as f:
    text = f.read()

with open(dict_path, "r", encoding="utf-8") as f:
    dict_defs = json.load(f)

# Список доступных файлов иконок (без расширения и с ним)
available_icons = {f.lower(): f for f in os.listdir(icons_dir)}

def find_icon(icon_name_or_path):
    if not icon_name_or_path:
        return ""
    # Очищаем от пути
    base = os.path.basename(icon_name_or_path).replace('.paa', '').replace('.png', '')
    png_name = f"{base}.png".lower()
    if png_name in available_icons:
        return f"/icons/{available_icons[png_name]}"
    return ""

def categorize(m_type, name, text):
    t = m_type.lower()
    n = name.lower()
    tx = text.lower()

    # 1. DP (Курьерские точки)
    if 'dp' in t or n.startswith('dp') or 'dp' in tx:
        return 'dp'

    # 2. Нелегальные точки (Наркотики, уран, контрабанда, перебивка)
    if any(k in t or k in n or k in tx for k in [
        'illegal', 'cocaine', 'heroine', 'canabis', 'weed', 'gera', 'narko', 'drug',
        'uran', 'perebivka', 'moneylaundering', 'slaver', 'нелегал', 'уран', 'кокаин', 'героин'
    ]):
        return 'illegal'

    # 3. Базы и особняки (Группировки, сквады, базы)
    if t.startswith('amazing_group_') or any(k in t or k in n or k in tx for k in [
        'rebelcamp', 'rentbase', 'база', 'особняк', 'мафия', 'групп'
    ]):
        return 'bases'

    # 4. Недвижимость (Гаражи, риелторы)
    if any(k in t or k in n or k in tx for k in ['garage', 'гараж', 'недвиж', 'realtor', 'estate']):
        return 'realestate'

    # 5. Территории
    if t in ['ellipse', 'rectangle'] or 'zone' in n or 'зона' in tx:
        return 'territories'

    # 6. Ресурсы (Добыча первичных ресурсов)
    if any(k in t or k in n or k in tx for k in [
        'oil', 'salt', 'sand', 'water', 'beans', 'minerals', 'jasperquartz', 
        'gornorudka', 'fish', 'meteorite', 'wastes', 'huntarea', 'нефть', 'соль', 'песок', 'руда', 'алмаз'
    ]) and not any(k in t or k in n or k in tx for k in ['factory', 'sell', 'store', 'перераб', 'завод']):
        return 'resources'

    # 7. Маршруты добычи (Заводы, фабрики, сбыт, переработка, лицензии)
    if any(k in t or k in n or k in tx for k in [
        'factory', 'sell', 'license', 'delivery', 'storage', 'depot', 'завод', 'фабрика', 'сбыт', 'переработка', 'лиценз'
    ]):
        return 'routes'

    # 8. Магазины (Транспорт, оружие, одежда, еда, аптеки)
    if any(k in t or k in n or k in tx for k in [
        'car', 'truck', 'richcar', 'conceptcar', 'motorcycle', 'gunstore', 
        'clothes', 'grocery', 'univermag', 'marketplace', 'pharmacy', 
        'garden_shop', 'beautysaloon', 'piercing', 'mask', 'drivingschool',
        'автосалон', 'оружие', 'одежда', 'магазин', 'рынок', 'аптека'
    ]):
        return 'shops'

    # 9. Инфраструктура (Банкоматы, родники, банки, полиция, больницы, порты, заправки)
    if any(k in t or k in n or k in tx for k in [
        'atm', 'loc_fountain', 'bank', 'hospital', 'policestation', 'jail', 
        'gasstation', 'parkingfine', 'pochtomat', 'government', 'harbor', 
        'boat', 'airplane', 'helicopter', 'bridge', 'checkpoing', 'fountain',
        'банкомат', 'родник', 'банк', 'больница', 'полиция', 'заправка', 'порт'
    ]):
        return 'infra'

    # 10. Прочее
    return 'other'

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
    if m_type.lower() == "empty":
        continue

    # Не включаем эллипсы/прямоугольники в маркеры-иконки (они идут в территории.json)
    if m_type.lower() in ['ellipse', 'rectangle']:
        continue

    pos_parts = [float(x.strip()) for x in pos_m.group(1).split(',')]
    name = name_m.group(1) if name_m else "Маркер"
    raw_text = text_m.group(1) if text_m else ""

    # Определяем название и иконку из словаря маркеров
    dict_info = dict_defs.get(m_type, {})
    dict_name = dict_info.get("name", "")
    dict_icon = dict_info.get("icon", "")

    icon_url = find_icon(dict_icon)
    if not icon_url:
        icon_url = find_icon(m_type)

    # Кастомные спец-правила по требованиям пользователя:
    # 1) Банкомат
    if 'atm' in name.lower() or 'atm' in m_type.lower():
        display_text = "Банкомат"
        icon_url = "/icons/atm.png"
    # 2) Родник (marker_286 или loc_Fountain)
    elif name == 'marker_286' or 'fountain' in m_type.lower():
        display_text = "Родник"
        icon_url = "/icons/loc_Fountain.png"
    # 3) DP (курьер)
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

    color = color_m.group(1) if color_m else "ColorYellow"

    markers.append({
        "name": name,
        "text": display_text,
        "type": m_type,
        "icon": icon_url,
        "color": color,
        "x": round(pos_parts[0], 1),
        "y": round(pos_parts[2], 1),
        "category": cat
    })

print(f"Экспортировано {len(markers)} маркеров!")
cats = {}
for m in markers:
    cats[m['category']] = cats.get(m['category'], 0) + 1
print("Категории маркеров:", cats)

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(markers, f, ensure_ascii=False, indent=2)

print(f"Файл {output_path} успешно записан в UTF-8!")
