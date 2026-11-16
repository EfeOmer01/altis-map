import os
import json
import math
from PIL import Image, ImageDraw

tiles_dir = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\веб\тайлы\6"

# Garage b_253: x = 3448.4, y = 13001.8, yaw = 205.8, w = 6.5, l = 9.5
gx, gy = 3448.4, 13001.8
yaw = 205.8
w, l = 7.0, 9.5

tx = int(gx / 480)
ty = int((30720 - gy) / 480)

canvas = Image.new("RGB", (1024, 1024))
for dtx in range(2):
    for dty in range(2):
        p = os.path.join(tiles_dir, str(tx + dtx), f"{ty + dty}.webp")
        if os.path.exists(p):
            canvas.paste(Image.open(p), (dtx * 512, dty * 512))

draw = ImageDraw.Draw(canvas)
def g2c(rx, ry):
    px = rx * 16 / 15 - tx * 512
    py = (30720 - ry) * 16 / 15 - ty * 512
    return (px, py)

rad = math.radians(yaw)
cos_a, sin_a = math.cos(rad), math.sin(rad)
hw, hl = w / 2, l / 2
corners = [(-hw, -hl), (hw, -hl), (hw, hl), (-hw, hl)]
poly = []
for cx, cy in corners:
    rx = cx * cos_a + cy * sin_a
    ry = -cx * sin_a + cy * cos_a
    poly.append(g2c(gx + rx, gy + ry))

draw.polygon(poly, fill=(6, 182, 212, 120), outline=(6, 182, 212))

cx, cy = g2c(gx, gy)
crop = canvas.crop((cx - 100, cy - 100, cx + 100, cy + 100))
crop.save(r"C:\temp\garage_b253_check.png")
print("Saved garage_b253_check.png")
