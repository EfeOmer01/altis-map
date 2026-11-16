import re
import json

dict_path = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\amazing_markers_dict.json"
with open(dict_path, "r", encoding="utf-8") as f:
    dict_defs = json.load(f)

f = open('../данные/uploaded_mission.cpp', 'r', encoding='latin1').read()
matches = re.finditer(r'class Item\d+\s*\{[^;]*dataType="Marker";(.*?)(?=\n\t\tclass Item|\n\t\t\};|\Z)', f, re.DOTALL)
for m in matches:
    block = m.group(0)
    if 'name="atm_marker"' in block:
        name_m = re.search(r'name="([^"]+)";', block)
        text_m = re.search(r'text="([^"]*)";', block)
        type_m = re.search(r'type="([^"]*)";', block)
        name = name_m.group(1) if name_m else ""
        raw_text = text_m.group(1) if text_m else ""
        m_type = type_m.group(1) if type_m else ""
        
        print("name:", repr(name), "raw_text:", repr(raw_text), "m_type:", repr(m_type))
        
        display_text = "Банкомат"
        print("Банкомат bytes:", [ord(c) for c in display_text])
        break
