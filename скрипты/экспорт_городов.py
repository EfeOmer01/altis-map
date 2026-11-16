import re
import json

config_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\config.cpp"
with open(config_path, "r", encoding="latin1") as f:
    text = f.read()

names_pos = text.find("class Names")
if names_pos == -1:
    print("Не найден class Names")
    exit(1)

cities = []
pattern = re.compile(
    r'class\s+([a-zA-Z0-9_]+)\s*\{'
    r'[^}]*?name\s*=\s*"([^"]*)";'
    r'[^}]*?position\[\]\s*=\s*\{([^}]+)\};'
    r'[^}]*?type\s*=\s*"([^"]*)";',
    re.DOTALL
)

for m in pattern.finditer(text, names_pos, names_pos + 80000):
    cls = m.group(1)
    if cls == "Names":
        continue
    name = m.group(2).strip()
    pos_str = m.group(3)
    ltype = m.group(4)

    clean_cls = re.sub(r'^(CityC_|City_|Village_|Hill_|Mount_|Local_|Airport_)', '', cls)
    clean_cls = re.sub(r'([a-z])([A-Z])', r'\1 \2', clean_cls) # AgiosDionysios -> Agios Dionysios

    if not name or name.startswith("$") or name == "" or name == "Names":
        name = clean_cls

    parts = [float(p.strip()) for p in pos_str.split(",")]
    if len(parts) >= 2:
        cities.append({
            "name": name,
            "type": ltype,
            "x": round(parts[0], 1),
            "y": round(parts[1], 1)
        })

print(f"Экспортировано локаций/городов: {len(cities)}")
with open(r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\города.json", "w", encoding="utf-8") as f:
    json.dump(cities, f, ensure_ascii=False, indent=2)

for c in cities[:10]:
    print(f"  {c['name']} ({c['type']}) at X:{c['x']} Y:{c['y']}")
