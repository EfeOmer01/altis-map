import os
import json
from PIL import Image, ImageDraw

tiles_dir = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\веб\тайлы\6"
shp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\data\roads\roads.shp"

# Let's test shifts (dx_meters, dy_meters) on Kavala and Sofia
# If we shift the road:
# gx_new = px_shp - 200000 + dx
# gy_new = py_shp + dy

import struct

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
        if stype == 3:
            num_parts, num_pts = struct.unpack('<II', rec_data[36:44])
            pts_offset = 44 + num_parts * 4
            pts = []
            for i in range(num_pts):
                px, py = struct.unpack('<2d', rec_data[pts_offset + i*16 : pts_offset + (i+1)*16])
                pts.append((px - 200000, py))
            raw_roads.append(pts)

# Let's test different (dx, dy) on Kavala [3640, 13100]
# In check_kavala.png:
# The red line needs to move EAST (positive X) and SOUTH (negative Y).
# Let's test dx in [15, 20, 25, 30] and dy in [-15, -20, -25, -30]

tx = int(3640 / 480)
ty = int((30720 - 13100) / 480)
canvas_base = Image.new("RGB", (1024, 1024))
for dtx in range(2):
    for dty in range(2):
        p = os.path.join(tiles_dir, str(tx + dtx), f"{ty + dty}.webp")
        if os.path.exists(p):
            canvas_base.paste(Image.open(p), (dtx * 512, dty * 512))

def test_shift(dx, dy, out_name):
    c = canvas_base.copy()
    draw = ImageDraw.Draw(c)
    def g2c(gx, gy):
        px = (gx + dx) * 16 / 15 - tx * 512
        py = (30720 - (gy + dy)) * 16 / 15 - ty * 512
        return (px, py)
    for r in raw_roads:
        pts = [g2c(p[0], p[1]) for p in r]
        if any(0 <= p[0] < 1024 and 0 <= p[1] < 1024 for p in pts):
            draw.line(pts, fill="lime", width=2)
    cx = 3640 * 16 / 15 - tx * 512
    cy = (30720 - 13100) * 16 / 15 - ty * 512
    crop = c.crop((cx - 200, cy - 200, cx + 200, cy + 200))
    crop.save(out_name)

test_shift(20, -18, r"C:\temp\kavala_shift_20_m18.png")
test_shift(25, -22, r"C:\temp\kavala_shift_25_m22.png")
test_shift(22, -20, r"C:\temp\kavala_shift_22_m20.png")
print("Saved shift tests")
