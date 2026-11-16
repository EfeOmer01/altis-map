import os
import json
import struct
from PIL import Image, ImageDraw

tiles_dir = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\веб\тайлы\6"
shp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\data\roads\roads.shp"

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

# In Sofia:
# Look at the highway running at 45 degrees:
# Let's test dx=20, dy=-18 vs dx=19, dy=-19 vs dx=21, dy=-18
for dx, dy in [(19, -17), (20, -18), (21, -19)]:
    tx = int(25600 / 480)
    ty = int((30720 - 21350) / 480)
    canvas = Image.new("RGB", (1024, 1024))
    for dtx in range(2):
        for dty in range(2):
            p = os.path.join(tiles_dir, str(tx + dtx), f"{ty + dty}.webp")
            if os.path.exists(p):
                canvas.paste(Image.open(p), (dtx * 512, dty * 512))
    draw = ImageDraw.Draw(canvas)
    def g2c(rx, ry):
        px = (rx + dx) * 16 / 15 - tx * 512
        py = (30720 - (ry + dy)) * 16 / 15 - ty * 512
        return (px, py)
    for r in raw_roads:
        pts = [g2c(p[0], p[1]) for p in r]
        if any(0 <= p[0] < 1024 and 0 <= p[1] < 1024 for p in pts):
            draw.line(pts, fill="lime", width=2)
    cx = 25600 * 16 / 15 - tx * 512
    cy = (30720 - 21350) * 16 / 15 - ty * 512
    crop = canvas.crop((cx - 150, cy - 150, cx + 150, cy + 150))
    crop.save(f"C:\\temp\\sofia_tune_{dx}_{dy}.png")

print("Saved tuning crops")
