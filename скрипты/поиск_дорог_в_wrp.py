import re

wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"

with open(wrp_path, 'rb') as f:
    data = f.read()

# Search for road p3ds
road_p3ds = re.findall(rb'[a-zA-Z0-9_\\]*road[a-zA-Z0-9_\\]*\.p3d', data, re.IGNORECASE)
print(f"Total road .p3d occurrences: {len(road_p3ds)}")
unique_roads = set(r.decode('ascii', errors='ignore').lower() for r in road_p3ds)
print(f"Unique road models ({len(unique_roads)}):")
for r in list(unique_roads)[:20]:
    print(" ", r)
