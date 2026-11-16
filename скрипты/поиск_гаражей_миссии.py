import json
import re

with open(r'C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\uploaded_mission.cpp', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Find all Item with dataType="Object"
blocks = re.findall(r'class Item\d+\s*\{[^}]*dataType="Object"[^}]*class Value\s*\{[^}]*\}\s*\};', text, re.DOTALL)
print(f"Total Object items in mission: {len(blocks)}")

garage_blocks = []
for b in blocks:
    if 'garage' in b.lower():
        type_m = re.search(r'type="([^"]+)"', b)
        pos_m = re.search(r'position\[\]=\{([0-9.,-]+),([0-9.,-]+),([0-9.,-]+)\}', b)
        name_m = re.search(r'name="([^"]+)"', b)
        cls = type_m.group(1) if type_m else "unknown"
        pos = [float(x) for x in pos_m.groups()] if pos_m else None
        name = name_m.group(1) if name_m else ""
        garage_blocks.append((cls, pos, name))

print(f"Found {len(garage_blocks)} garage objects:")
for g in garage_blocks:
    print(f"  {g[0]} at {g[1]} (name: '{g[2]}')")
