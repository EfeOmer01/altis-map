import os
import re
import json
import subprocess
from PIL import Image

MARKERS_ROOT = r"C:\Users\efeom\OneDrive\Рабочий стол\1\amazing_markers"
OUT_ICONS_DIR = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\веб\иконки"
PAL2PACE = r"C:\Program Files (x86)\Steam\steamapps\common\Arma 3 Tools\TexView2\Pal2PacE.exe"
TEMP_DIR = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\скрипты\temp_icons"

os.makedirs(OUT_ICONS_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

with open(r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\amazing_markers_dict.json", "r", encoding="utf-8") as f:
    dict_defs = json.load(f)

# Названия на русском для маркеров
TRANSLATIONS = {
    "amazingrp.ru | DP": "Курьер DP",
    "amazingrp.ru | Aircraft Garage": "Авиагараж",
    "amazingrp.ru | Aircraft Garage (Illegal)": "Нелегальный авиагараж",
    "amazingrp.ru | Airplane Shop": "Магазин самолетов",
    "amazingrp.ru | Alcohol Sell": "Скупка алкоголя",
    "amazingrp.ru | Amber Factory": "Янтарный завод",
    "amazingrp.ru | Bank": "Банк",
    "amazingrp.ru | Beans": "Сбор фасоли",
    "amazingrp.ru | Beans Factory": "Завод фасоли",
    "amazingrp.ru | Beauty Saloon": "Салон красоты",
    "amazingrp.ru | Boat Shop": "Лодочный салон",
    "amazingrp.ru | Botanica": "Ботаника",
    "amazingrp.ru | Brewery": "Пивоварня",
    "amazingrp.ru | Bridge": "Мост",
    "amazingrp.ru | Canabis Plantation": "Плантация каннабиса",
    "amazingrp.ru | Car Shop": "Автосалон",
    "amazingrp.ru | Casino #2": "Казино",
    "amazingrp.ru | Cement Factory": "Цементный завод",
    "amazingrp.ru | Cement Sell": "Сбыт цемента",
    "amazingrp.ru | Checkpoint": "Блокпост",
    "amazingrp.ru | Clothes Shop": "Магазин одежды",
    "amazingrp.ru | Coal & Sulfur Sell": "Скупка угля и серы",
    "amazingrp.ru | Cocaine Factory": "Завод кокаина",
    "amazingrp.ru | Cocaine Plantation": "Плантация коки",
    "amazingrp.ru | Concept Car Shop": "Салон концепт-каров",
    "amazingrp.ru | Crops": "Урожай",
    "amazingrp.ru | Customs": "Таможня",
    "amazingrp.ru | Diamond Sell": "Скупка алмазов",
    "amazingrp.ru | Diamonds": "Добыча алмазов",
    "amazingrp.ru | Diving Shop": "Дайвинг магазин",
    "amazingrp.ru | Drive School": "Автошкола",
    "amazingrp.ru | Drug Dealer": "Наркодилер",
    "amazingrp.ru | Drug Sell": "Сбыт наркотиков",
    "amazingrp.ru | Energy Factory": "Электростанция",
    "amazingrp.ru | Expensive Car Shop": "Элитный автосалон",
    "amazingrp.ru | Factory": "Завод",
    "amazingrp.ru | Fish": "Рыбалка",
    "amazingrp.ru | Fish Sell": "Сбыт рыбы",
    "amazingrp.ru | Garage": "Гараж",
    "amazingrp.ru | Garden": "Сад",
    "amazingrp.ru | Garden Shop": "Садовый магазин",
    "amazingrp.ru | Gas Station": "Заправка АЗС",
    "amazingrp.ru | Geroine Plantation": "Плантация героина",
    "amazingrp.ru | Glass Factory": "Стекольный завод",
    "amazingrp.ru | Gornorudka": "Горнорудка",
    "amazingrp.ru | Grocery": "Продуктовый магазин",
    "amazingrp.ru | Gun Shop": "Оружейный магазин",
    "amazingrp.ru | Gun Shop (Illegal)": "Нелегальное оружие",
    "amazingrp.ru | Helicopter Shop": "Вертолетный салон",
    "amazingrp.ru | Heroine Factory": "Героиновый завод",
    "amazingrp.ru | Hospital": "Больница EMS",
    "amazingrp.ru | Iron & Copper Sell": "Сбыт железа и меди",
    "amazingrp.ru | Iron & Copper Supply": "Месторождение железа/меди",
    "amazingrp.ru | Jasper & Quartz Factory": "Завод кварца и яшмы",
    "amazingrp.ru | Marketplace": "Рынок",
    "amazingrp.ru | Meteorite": "Метеорит",
    "amazingrp.ru | Minefactory": "Горный комбинат",
    "amazingrp.ru | Minerals": "Минералы",
    "amazingrp.ru | Minerals Sell": "Сбыт минералов",
    "amazingrp.ru | Money Laundering": "Отмыв денег",
    "amazingrp.ru | Motorcycle Shop": "Мотосалон",
    "amazingrp.ru | Narco Lab": "Нарколаборатория",
    "amazingrp.ru | No-Fly Zone": "Бесполетная зона",
    "amazingrp.ru | Oil": "Нефтяное месторождение",
    "amazingrp.ru | Oil Factory": "Нефтеперерабатывающий завод",
    "amazingrp.ru | Parking Fine": "Штрафстоянка",
    "amazingrp.ru | Perebivka": "Перебивка номеров",
    "amazingrp.ru | Pharmacy": "Аптека",
    "amazingrp.ru | Piercing": "Пирсинг-салон",
    "amazingrp.ru | Plastic Factory": "Завод пластика",
    "amazingrp.ru | Pochtomat": "Почтомат",
    "amazingrp.ru | Policestation": "Полицейский участок",
    "amazingrp.ru | Rebel Camp": "Лагерь повстанцев",
    "amazingrp.ru | Rent Base #1": "База в аренду",
    "amazingrp.ru | Salt": "Соляное месторождение",
    "amazingrp.ru | Salt Factory": "Соляной завод",
    "amazingrp.ru | Salt Sell": "Сбыт соли",
    "amazingrp.ru | Sand": "Песчаный карьер",
    "amazingrp.ru | Slaver": "Работорговец",
    "amazingrp.ru | Special Vehicle Shop": "Салон спецтехники",
    "amazingrp.ru | Storage": "Склад",
    "amazingrp.ru | Truck Shop": "Грузовой автосалон",
    "amazingrp.ru | Turtle": "Ловля черепах",
    "amazingrp.ru | Turtle Sell": "Сбыт черепах",
    "amazingrp.ru | Univermag": "Универмаг",
    "amazingrp.ru | Uran 235 Factory": "Завод Уран-235",
    "amazingrp.ru | Uran 236 Factory": "Завод Уран-236",
    "amazingrp.ru | Uran 237 Factory": "Завод Уран-237",
    "amazingrp.ru | Uran Quarry": "Урановый карьер",
    "amazingrp.ru | Uran Sell": "Сбыт урана",
    "amazingrp.ru | Wastes": "Свалка отходов",
    "amazingrp.ru | Water Well": "Водный источник",
    "amazingrp.ru | Cannabis Factory": "Завод каннабиса"
}

# Конвертируем PAA в PNG
converted_icons = {}
print("Конвертируем иконки маркеров...")

for cls, info in dict_defs.items():
    icon_rel = info.get("icon", "")
    if not icon_rel:
        continue
        
    # Путь в amazing_markers
    clean_rel = icon_rel.replace("\\amazing_markers\\", "").replace("amazing_markers\\", "").lstrip("\\")
    paa_path = os.path.join(MARKERS_ROOT, clean_rel)
    
    if not os.path.exists(paa_path):
        # Попробуем добавить .paa если нет
        if not paa_path.endswith(".paa"):
            paa_path += ".paa"
            
    if os.path.exists(paa_path):
        out_png = os.path.join(OUT_ICONS_DIR, f"{cls}.png")
        if not os.path.exists(out_png) or os.path.getsize(out_png) < 100:
            try:
                tmp_out = os.path.join(TEMP_DIR, f"{cls}.png")
                subprocess.run([PAL2PACE, paa_path, tmp_out], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if os.path.exists(tmp_out):
                    with Image.open(tmp_out) as img:
                        # Ресайзим до аккуратных 32x32 для четкого отображения на карте
                        img = img.resize((32, 32), Image.Resampling.LANCZOS)
                        img.save(out_png, "PNG")
                    os.remove(tmp_out)
            except Exception as e:
                pass
                
        if os.path.exists(out_png):
            converted_icons[cls] = f"/иконки/{cls}.png"

print(f"Успешно конвертировано оригинальных иконок: {len(converted_icons)}")

# Теперь обновляем данные маркеров миссии
with open(r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\uploaded_mission.cpp", "r", encoding="latin1") as f:
    text = f.read()

markers = []
marker_matches = re.finditer(r'class Item\d+\s*\{[^;]*dataType="Marker";(.*?)(?=\n\t\tclass Item|\n\t\t\};|\Z)', text, re.DOTALL)

for m in marker_matches:
    block = m.group(0)
    pos_m = re.search(r'position\[\]=\{([^}]+)\};', block)
    name_m = re.search(r'name="([^"]+)";', block)
    text_m = re.search(r'text="([^"]*)";', block)
    type_m = re.search(r'type="([^"]*)";', block)
    color_m = re.search(r'colorName="([^"]*)";', block)

    if not pos_m: continue
    m_type = type_m.group(1) if type_m else ""
    if m_type.lower() == "empty": continue

    pos_parts = [float(x.strip()) for x in pos_m.group(1).split(',')]
    name = name_m.group(1) if name_m else "Маркер"
    raw_text = text_m.group(1) if text_m else ""

    # Берем определение из словаря
    def_info = dict_defs.get(m_type, {})
    raw_def_name = def_info.get("name", "")
    display_title = TRANSLATIONS.get(raw_def_name, raw_def_name)

    # Итоговый текст маркера
    if raw_text:
        final_text = raw_text
    elif display_title:
        final_text = display_title
    else:
        final_text = name

    icon_url = converted_icons.get(m_type, "")

    markers.append({
        "name": name,
        "text": final_text,
        "type": m_type,
        "icon": icon_url,
        "color": color_m.group(1) if color_m else "ColorYellow",
        "x": round(pos_parts[0], 1),
        "y": round(pos_parts[2], 1)
    })

print(f"Всего сохранено маркеров миссии: {len(markers)}")
with open(r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\маркеры_миссии.json", "w", encoding="utf-8") as f:
    json.dump(markers, f, ensure_ascii=False, indent=2)

try:
    os.rmdir(TEMP_DIR)
except: pass

print("Готово!")
