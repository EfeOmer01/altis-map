import os
import re
import json

folder = r"C:\Users\efeom\OneDrive\Рабочий стол\1\amazing_markers"
for f in os.listdir(folder):
    if len(f.replace('\t', '').replace('%9', '')) == 0:
        with open(os.path.join(folder, f), 'r', encoding='latin1') as fp:
            text = fp.read()

# Разделяем по 'class '
parts = text.split("class ")
res = {}

for p in parts[1:]:
    lines = p.splitlines()
    header = lines[0].strip()
    cls_match = re.match(r'^([a-zA-Z0-9_]+)', header)
    if not cls_match:
        continue
    cls_name = cls_match.group(1)
    
    # Находим name="..." и icon="..." в блоке
    body = "\n".join(lines[:30])
    name_m = re.search(r'name\s*=\s*"([^"]+)";', body)
    icon_m = re.search(r'icon\s*=\s*"([^"]+)";', body)
    
    clean_name = ""
    if name_m:
        raw = name_m.group(1)
        try:
            clean_name = raw.encode('latin1').decode('windows-1251')
        except:
            clean_name = raw
            
    icon_path = icon_m.group(1) if icon_m else ""
    res[cls_name] = {
        "name": clean_name or cls_name,
        "icon": icon_path
    }

print(f"Всего распознано классов: {len(res)}")
amazing = {k: v for k, v in res.items() if "amazing" in k.lower()}
print(f"Из них amazing: {len(amazing)}")

with open(r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\amazing_markers_dict.json", "w", encoding="utf-8") as out:
    json.dump(res, out, ensure_ascii=False, indent=2)

# Выведем маркеры
count = 0
for k, v in amazing.items():
    if "marker" in k and count < 35:
        # Безопасный вывод
        safe_name = v['name'].encode('ascii', errors='replace').decode('ascii')
        print(f"  {k} -> {safe_name} ({v['icon']})")
        count += 1
