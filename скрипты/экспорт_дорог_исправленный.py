import struct
import json
import os

shp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\data\roads\roads.shp"
dbf_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\data\roads\roads.dbf"
out_path = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\дороги.json"

# 1. Читаем типы дорог из DBF
with open(dbf_path, "rb") as f:
    hdr = f.read(32)
    num_recs, = struct.unpack('<I', hdr[4:8])
    hdr_len, rec_len = struct.unpack('<HH', hdr[8:12])
    f.seek(hdr_len)
    road_types = []
    for _ in range(num_recs):
        rec = f.read(rec_len)
        layer = rec[1:31].decode('ascii', errors='ignore').strip()
        rid = rec[31:61].decode('ascii', errors='ignore').strip()
        road_types.append(int(rid) if rid.isdigit() else 3)

print(f"Прочитано {len(road_types)} типов дорог из DBF")

# 2. Калиброванная трансформация Terrain Builder для AmazingMap:
# Easting = 199980.0, Northing = 18.0
OFFSET_X = 199980.0
OFFSET_Y = 18.0

roads_data = []

with open(shp_path, "rb") as f:
    hdr = f.read(100)
    file_len, = struct.unpack('>I', hdr[24:28])
    file_bytes = file_len * 2

    rec_idx = 0
    while f.tell() < file_bytes:
        rec_hdr = f.read(8)
        if len(rec_hdr) < 8: break
        rec_num, rec_len = struct.unpack('>II', rec_hdr)
        rec_data = f.read(rec_len * 2)
        stype, = struct.unpack('<I', rec_data[0:4])
        
        if stype == 3: # PolyLine
            num_parts, num_pts = struct.unpack('<II', rec_data[36:44])
            parts = struct.unpack(f'<{num_parts}I', rec_data[44:44+num_parts*4])
            pts_offset = 44 + num_parts * 4
            pts = []
            for i in range(num_pts):
                px, py = struct.unpack('<2d', rec_data[pts_offset + i*16 : pts_offset + (i+1)*16])
                # Точная привязка к координатам игрового мира Arma 3
                gx = round(px - OFFSET_X, 1)
                gy = round(py - OFFSET_Y, 1)
                pts.append([gx, gy])
            
            rid = road_types[rec_idx] if rec_idx < len(road_types) else 3
            roads_data.append({
                "type": rid,
                "pts": pts
            })
            rec_idx += 1

print(f"Экспортировано {len(roads_data)} дорожных сегментов с точной калибровкой")

with open(out_path, "w", encoding="utf-8") as f:
    json.dump(roads_data, f, ensure_ascii=False)

print(f"Успешно сохранено в {out_path}!")
