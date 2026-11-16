import re

cpp_path = r'C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\uploaded_mission.cpp'
with open(cpp_path, 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

types = re.findall(r'type\s*=\s*"([^"]+)"', text)
garages = [t for t in types if 'garage' in t.lower()]
counts = {}
for g in garages:
    counts[g] = counts.get(g, 0) + 1

print("Mission garages count:", len(garages))
for g, c in sorted(counts.items()):
    print(f"  {g}: {c}")
