import re

with open(r'C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\uploaded_mission.cpp', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

garages = re.findall(r'[^\n]*garage[^\n]*', text, re.IGNORECASE)
print(f"Total lines mentioning garage: {len(garages)}")
for line in garages[:15]:
    print("  ", line.strip())
