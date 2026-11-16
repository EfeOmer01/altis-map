import re

with open(r'C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\uploaded_mission.cpp', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

garages = re.findall(r'[^\n]*i_garage_v1_f[^\n]*', text, re.IGNORECASE)
print(f"Total lines mentioning i_garage_v1_f in mission: {len(garages)}")
for line in garages[:10]:
    print("  ", line.strip())

# Also search for Land_i_Garage in mission
garages2 = re.findall(r'[^\n]*garage_v[^\n]*', text, re.IGNORECASE)
print(f"Total lines mentioning garage_v in mission: {len(garages2)}")
for line in garages2[:10]:
    print("  ", line.strip())
