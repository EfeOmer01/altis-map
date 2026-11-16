import json

with open(r'C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\маркеры_миссии.json', 'r', encoding='utf-8') as f:
    markers = json.load(f)

for m in markers:
    if 'atm' in m.get('name', '').lower():
        print("Sample ATM marker:", m)
        break
