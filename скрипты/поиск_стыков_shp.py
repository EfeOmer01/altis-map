import struct
import json

shp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\data\roads\roads.shp"

# Let's read all raw polylines from roads.shp (WITHOUT subtracting 200000)
raw_roads = []
with open(shp_path, "rb") as f:
    hdr = f.read(100)
    file_len, = struct.unpack('>I', hdr[24:28])
    file_bytes = file_len * 2

    while f.tell() < file_bytes:
        rec_hdr = f.read(8)
        if len(rec_hdr) < 8: break
        rec_num, rec_len = struct.unpack('>II', rec_hdr)
        rec_data = f.read(rec_len * 2)
        stype, = struct.unpack('<I', rec_data[0:4])
        if stype == 3: # PolyLine
            num_parts, num_pts = struct.unpack('<II', rec_data[36:44])
            pts_offset = 44 + num_parts * 4
            pts = []
            for i in range(num_pts):
                px, py = struct.unpack('<2d', rec_data[pts_offset + i*16 : pts_offset + (i+1)*16])
                pts.append((px, py))
            raw_roads.append(pts)

print(f"Total raw roads: {len(raw_roads)}")

# Let's check Rodopoli intersection:
# In roads.shp, Rodopoli intersection point:
# Road 11 starts at raw px ~ 218924, py ~ 16645.
# Let's find all endpoints in raw_roads near (218924, 16645):
for idx, r in enumerate(raw_roads):
    for p in [r[0], r[-1]]:
        if abs(p[0] - 218924) < 10 and abs(p[1] - 16645) < 10:
            print(f"Road {idx} connects at raw: ({p[0]:.2f}, {p[1]:.2f})")
