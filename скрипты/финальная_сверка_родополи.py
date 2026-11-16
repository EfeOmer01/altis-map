import os
import json
import math
from PIL import Image, ImageDraw

tiles_dir = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\веб\тайлы\6"
roads_path = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\дороги.json"
bldgs_path = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\дома_острова.json"

gx_center = 18925.0
gy_center = 16644.0

# Load 3x3 tiles around (39, 29)
min_tx, min_ty = 38, 28
canvas = Image.new("RGB", (1536, 1536))
for tx in range(min_tx, min_tx + 3):
    for ty in range(min_ty, min_ty + 3):
        tpath = os.path.join(tiles_dir, str(tx), f"{ty}.webp")
        if os.path.exists(tpath):
            canvas.paste(Image.open(tpath), ((tx - min_tx) * 512, (ty - min_ty) * 512))

draw = ImageDraw.Draw(canvas)

def g2c(gx, gy):
    px = gx * 16 / 15 - min_tx * 512
    py = (30720 - gy) * 16 / 15 - min_ty * 512
    return (px, py)

# 1. Draw Buildings
with open(bldgs_path, "r", encoding="utf-8") as f:
    bldgs = json.load(f)

for b in bldgs:
    gx, gy, w, l, yaw = b['x'], b['y'], b['w'], b['l'], b['yaw']
    rad = math.radians(yaw)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    hw, hl = w / 2, l / 2
    corners = [(-hw, -hl), (hw, -hl), (hw, hl), (-hw, hl)]
    poly = []
    for cx, cy in corners:
        rx = cx * cos_a + cy * sin_a
        ry = -cx * sin_a + cy * cos_a
        poly.append(g2c(gx + rx, gy + ry))
    if any(0 <= p[0] < 1536 and 0 <= p[1] < 1536 for p in poly):
        draw.polygon(poly, fill=(124, 133, 145), outline=(60, 66, 73))

# 2. Draw Roads (Highway with casing and white core)
with open(roads_path, "r", encoding="utf-8") as f:
    roads = json.load(f)

for r in roads:
    c_pts = [g2c(p[0], p[1]) for p in r['pts']]
    if any(0 <= p[0] < 1536 and 0 <= p[1] < 1536 for p in c_pts):
        if r['type'] == 1:
            draw.line(c_pts, fill=(28, 32, 37), width=6)
            draw.line(c_pts, fill=(255, 255, 255), width=4)
        elif r['type'] == 2:
            draw.line(c_pts, fill=(44, 49, 56), width=4)
            draw.line(c_pts, fill=(243, 239, 230), width=2)
        elif r['type'] == 3:
            draw.line(c_pts, fill=(150, 125, 96), width=2)
        elif r['type'] == 4:
            draw.line(c_pts, fill=(223, 215, 200), width=2)

cx, cy = g2c(gx_center, gy_center)
crop = canvas.crop((cx - 300, cy - 150, cx + 300, cy + 150))
crop.save(r"C:\temp\rodopoli_final_verification.png")
print("Saved final verification image!")
