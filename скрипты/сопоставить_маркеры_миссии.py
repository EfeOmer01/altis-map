import json
import os
import re

with open(r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\uploaded_mission.cpp", "r", encoding="latin1") as f:
    text = f.read()

with open(r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\amazing_markers_dict.json", "r", encoding="utf-8") as f:
    dict_defs = json.load(f)

# Собираем типы маркеров из миссии
marker_types = set()
for m in re.finditer(r'class Item\d+\s*\{[^;]*dataType="Marker";(.*?)(?=\n\t\tclass Item|\n\t\t\};|\Z)', text, re.DOTALL):
    block = m.group(0)
    tm = re.search(r'type="([^"]+)";', block)
    if tm and tm.group(1).lower() != "empty":
        marker_types.add(tm.group(1))

print(f"Уникальных типов маркеров в миссии: {len(marker_types)}")
for t in sorted(marker_types):
    info = dict_defs.get(t, {})
    name = info.get("name", "НЕИЗВЕСТНО")
    icon = info.get("icon", "НЕТ ИКОНКИ")
    print(f"  {t:35} -> {name} ({icon})")
