import re

wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"
with open(wrp_path, "rb") as f:
    data = f.read()

matches = set(re.findall(rb'[a-zA-Z0-9_\\/.]+\.p3d', data, re.IGNORECASE))
roads = [m.decode('latin1') for m in matches if 'road' in m.decode('latin1').lower()]
print(f"Total p3d models: {len(matches)}")
print(f"Road p3d models ({len(roads)}):")
for r in roads[:30]:
    print(" ", r)
