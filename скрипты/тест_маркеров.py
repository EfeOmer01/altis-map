with open(r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\uploaded_mission.cpp", "r", encoding="latin1") as f:
    text = f.read()

import re
matches = list(re.finditer(r'class Item\d+\s*\{[^;]*dataType="Marker";(.*?)(?=\n\t\tclass Item|\n\t\t\};|\Z)', text, re.DOTALL))
print(f"Total markers found: {len(matches)}")
for m in matches[10:15]:
    print("--- MARKER ---")
    print(m.group(0)[:400])
