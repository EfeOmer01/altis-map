import os
import json
from PIL import Image, ImageDraw

tiles_dir = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\веб\тайлы\6"

# Hospital at gx = 3760.5, gy = 12990.1
# tile_x = int(3760.5 / 480) = 7
# tile_y = int((30720 - 12990.1) / 480) = int(17729.9 / 480) = 36
tx, ty = 7, 36

# Let's load 2x2 tiles around (7, 36): (7,36), (8,36), (7,37), (8,37)
canvas = Image.new("RGB", (1024, 1024))
for dx in range(2):
    for dy in range(2):
        tpath = os.path.join(tiles_dir, str(tx + dx), f"{ty + dy}.webp")
        if os.path.exists(tpath):
            canvas.paste(Image.open(tpath), (dx * 512, dy * 512))

draw = ImageDraw.Draw(canvas)

def g2c(gx, gy):
    px = gx * 16 / 15
    py = (30720 - gy) * 16 / 15
    return (px - tx * 512, py - ty * 512)

# Load hospital buildings
with open(r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\дома_острова.json", "r", encoding="utf-8") as f:
    bldgs = json.load(f)

for b in bldgs:
    if abs(b['x'] - 3760) < 300 and abs(b['y'] - 12990) < 300:
        bx, by = g2c(b['x'], b['y'])
        draw.rectangle([bx-5, by-5, bx+5, by+5], outline="red", width=2)

canvas.save(r"C:\temp\kavala_hospital.png")

# Crop 400x400 around hospital
hx, hy = g2c(3760.5, 12990.1)
crop = canvas.crop((hx - 200, hy - 200, hx + 200, hy + 200))
crop.save(r"C:\temp\kavala_hospital_zoom.png")
print(f"Hospital at canvas ({hx:.1f}, {hy:.1f})")
