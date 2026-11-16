import re

cpp_path = r'C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\uploaded_mission.cpp'
with open(cpp_path, 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

for z in ['safe_zone_1', 'uran_zone', 'hunting_zone']:
    pattern = r'class Item\d+\s*\{[^}]*name\s*=\s*"' + z + r'"[^}]*\}'
    m = re.search(pattern, text)
    if m:
        print("---", z, "---")
        print(m.group(0))
