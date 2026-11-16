import os
import subprocess
from PIL import Image, ImageDraw

pal2pace = r"C:\Program Files (x86)\Steam\steamapps\common\Arma 3 Tools\TexView2\Pal2PacE.exe"
layers_dir = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\data\layers"

# Convert raw PAA S_007_036_lco.paa and S_008_036_lco.paa
p07 = os.path.join(layers_dir, "S_007_036_lco.paa")
p08 = os.path.join(layers_dir, "S_008_036_lco.paa")

subprocess.run([pal2pace, p07, r"C:\temp\raw_007_036.png"], stdout=subprocess.DEVNULL)
subprocess.run([pal2pace, p08, r"C:\temp\raw_008_036.png"], stdout=subprocess.DEVNULL)

im07 = Image.open(r"C:\temp\raw_007_036.png")
im08 = Image.open(r"C:\temp\raw_008_036.png")

# Stitch them side-by-side using the known 32-pixel overlap:
# im07 is columns 0..480 (width 480)
# im08 is columns 0..480 (width 480)
# Total width = 960, height = 512
raw_stitch = Image.new("RGB", (960, 512))
raw_stitch.paste(im07.crop((0, 0, 480, 512)), (0, 0))
raw_stitch.paste(im08.crop((0, 0, 480, 512)), (480, 0))

# Hospital coordinates:
# gx = 3760.5, gy = 12990.1
# What is gx relative to tile 7?
# Tile 7 begins at: 7 * 480 = 3360 meters!
# So in this raw stitch:
# rx = gx - 3360 = 3760.5 - 3360 = 400.5 meters (pixels)!
# What is gy relative to tile 36?
# In top-down:
# World top is 30720.
# Tile 36 top is 30720 - 36 * 480 = 30720 - 17280 = 13440 meters!
# Tile 36 bottom is 13440 - 480 = 12960 meters!
# gy = 12990.1 meters.
# Distance from tile 36 top:
# ry = 13440 - 12990.1 = 449.9 meters (pixels)!

print(f"Hospital expected raw stitch pixel: rx = {400.5}, ry = {449.9}")

draw = ImageDraw.Draw(raw_stitch)
draw.rectangle([400.5 - 8, 449.9 - 8, 400.5 + 8, 449.9 + 8], outline="red", width=2)

raw_stitch.save(r"C:\temp\raw_hospital_check.png")

# Crop 200x200 around (400.5, 449.9)
crop = raw_stitch.crop((400 - 100, 450 - 100, 400 + 100, 450 + 100))
crop.save(r"C:\temp\raw_hospital_zoom.png")
print("Saved raw_hospital_zoom.png")
