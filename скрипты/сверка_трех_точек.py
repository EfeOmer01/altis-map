import os
import json
import struct
from PIL import Image, ImageDraw

tiles_dir = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\веб\тайлы\6"
shp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\data\roads\roads.shp"

# Load roads from shp
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
                # Subtract 200000 for preliminary check
                pts.append((px - 200000, py))
            raw_roads.append(pts)

# Control points to test:
# 1. Kavala Pier / waterfront road: [3700, 13000]
# 2. Main airfield runway / highway near Athira: [14000, 16300]
# 3. Sofia main crossroad: [25600, 21300]

def inspect_area(name, target_gx, target_gy):
    # Determine tile
    tx = int(target_gx / 480)
    ty = int((30720 - target_gy) / 480)
    
    # Load 2x2 tiles around (tx, ty)
    canvas = Image.new("RGB", (1024, 1024))
    for dx in range(2):
        for dy in range(2):
            p = os.path.join(tiles_dir, str(tx + dx), f"{ty + dy}.webp")
            if os.path.exists(p):
                canvas.paste(Image.open(p), (dx * 512, dy * 512))
    
    draw = ImageDraw.Draw(canvas)
    
    def g2c(gx, gy):
        px = gx * 16 / 15 - tx * 512
        py = (30720 - gy) * 16 / 15 - ty * 512
        return (px, py)
    
    # Draw roads in red
    for r in raw_roads:
        pts = [g2c(p[0], p[1]) for p in r]
        if any(0 <= p[0] < 1024 and 0 <= p[1] < 1024 for p in pts):
            draw.line(pts, fill="red", width=3)
    
    # Crop 400x400 around target
    cx, cy = g2c(target_gx, target_gy)
    crop = canvas.crop((cx - 200, cy - 200, cx + 200, cy + 200))
    crop_path = f"C:\\temp\\check_{name}.png"
    crop.save(crop_path)
    print(f"Saved {crop_path} centered at ({target_gx}, {target_gy})")

inspect_area("kavala", 3640, 13100)
inspect_area("athira", 14000, 16300)
inspect_area("sofia", 25600, 21350)
