import os
import json
from PIL import Image, ImageDraw

tiles_dir = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\веб\тайлы\6"
out_img_path = r"C:\temp\stitch_check.png"

# We want tile_x in [38, 39, 40], tile_y in [28, 29, 30]
# Total size = 3*512 x 3*512 = 1536 x 1536
canvas = Image.new("RGB", (1536, 1536))

min_tx, min_ty = 38, 28

for tx in range(min_tx, min_tx + 3):
    for ty in range(min_ty, min_ty + 3):
        tpath = os.path.join(tiles_dir, str(tx), f"{ty}.webp")
        if os.path.exists(tpath):
            tile = Image.open(tpath)
            canvas.paste(tile, ((tx - min_tx) * 512, (ty - min_ty) * 512))

draw = ImageDraw.Draw(canvas)

# Convert game coords (gx, gy) to canvas pixel (cx, cy):
# px_x = gx * 16 / 15
# px_y = (30720 - gy) * 16 / 15
# cx = px_x - min_tx * 512
# cy = px_y - min_ty * 512

def g2c(gx, gy):
    px = gx * 16 / 15
    py = (30720 - gy) * 16 / 15
    return (px - min_tx * 512, py - min_ty * 512)

# Load roads
with open(r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\дороги.json", "r", encoding="utf-8") as f:
    roads = json.load(f)

for r in roads:
    pts = r['pts']
    # Check if road passes through our canvas bbox:
    # min gx = min_tx * 480 = 38 * 480 = 18240
    # max gx = (min_tx+3) * 480 = 19680
    # min gy = 30720 - (min_ty+3)*480 = 30720 - 31*480 = 15840
    # max gy = 30720 - min_ty*480 = 30720 - 28*480 = 17280
    c_pts = [g2c(p[0], p[1]) for p in pts]
    # Filter points near canvas
    if any(0 <= p[0] < 1536 and 0 <= p[1] < 1536 for p in c_pts):
        color = "yellow" if r.get('type') == 1 else "cyan"
        width = 4 if r.get('type') == 1 else 2
        draw.line(c_pts, fill=color, width=width)

# Load buildings
with open(r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\дома_острова.json", "r", encoding="utf-8") as f:
    bldgs = json.load(f)

for b in bldgs:
    bx, by = g2c(b['x'], b['y'])
    if 0 <= bx < 1536 and 0 <= by < 1536:
        # Draw small rectangle for bldg
        draw.rectangle([bx-4, by-4, bx+4, by+4], outline="red", width=1)

canvas.save(out_img_path)
print(f"Saved stitch to {out_img_path}")
