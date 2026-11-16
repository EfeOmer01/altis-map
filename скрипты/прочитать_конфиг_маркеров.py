import os
import re
import json

folder = r"C:\Users\efeom\OneDrive\Рабочий стол\1\amazing_markers"
config_file = None
for f in os.listdir(folder):
    if len(f.replace('\t', '').replace('%9', '')) == 0:
        config_file = os.path.join(folder, f)
        break

if not config_file:
    print("Не найден конфигурационный файл")
    exit(1)

with open(config_file, "r", encoding="latin1") as fp:
    text = fp.read()

pattern = re.compile(r'class\s+([a-zA-Z0-9_]+)\s*:[^\{]+\{([^\}]+)\}', re.DOTALL)
marker_defs = {}

for m in pattern.finditer(text):
    cls = m.group(1)
    body = m.group(2)
    name_m = re.search(r'name\s*=\s*"([^"]+)";', body)
    icon_m = re.search(r'icon\s*=\s*"([^"]+)";', body)
    color_m = re.search(r'color\[\]\s*=\s*\{([^}]+)\};', body)

    # Декодируем русские символы из windows-1251
    raw_name = name_m.group(1) if name_m else cls
    try:
        clean_name = raw_name.encode('latin1').decode('windows-1251')
    except:
        clean_name = raw_name

    marker_defs[cls] = {
        "class": cls,
        "name": clean_name,
        "icon": icon_m.group(1).replace('\\\\', '\\') if icon_m else ""
    }

print(f"Всего определений маркеров: {len(marker_defs)}")

with open(r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\определения_маркеров.json", "w", encoding="utf-8") as f:
    json.dump(marker_defs, f, ensure_ascii=False, indent=2)

print("Успешно сохранены определения маркеров с русскими названиями!")
