with open(r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\uploaded_mission.cpp", "r", encoding="latin1") as f:
    text = f.read()

import re
from collections import Counter

matches = list(re.finditer(r'class Item\d+\s*\{[^;]*dataType="Marker";(.*?)(?=\n\t\tclass Item|\n\t\t\};|\Z)', text, re.DOTALL))
types = []
for m in matches:
    block = m.group(0)
    tm = re.search(r'type="([^"]+)";', block)
    if tm:
        types.append(tm.group(1))

print("All marker types in uploaded mission:")
for t, c in Counter(types).most_common(30):
    print(f"  {t}: {c}")
