import os
import glob
from PIL import Image
import subprocess

layers_dir = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\data\layers"
pal2pace = r"C:\Program Files (x86)\Steam\steamapps\common\Arma 3 Tools\TexView2\Pal2PacE.exe"
temp_dir = r"C:\temp\tb_check"
os.makedirs(temp_dir, exist_ok=True)

# Find tiles with land (size > 1000 bytes)
land_tiles = []
for f in glob.glob(os.path.join(layers_dir, "S_*_lco.paa")):
    sz = os.path.getsize(f)
    if sz > 5000:
        base = os.path.basename(f)
        parts = base.split('_')
        x, y = int(parts[1]), int(parts[2])
        land_tiles.append((x, y, sz, f))

xs = [t[0] for t in land_tiles]
ys = [t[1] for t in land_tiles]
print(f"Total land tiles: {len(land_tiles)}")
print(f"X range with land: {min(xs)} to {max(xs)}")
print(f"Y range with land: {min(ys)} to {max(ys)}")

# Kavala is at X=3700, Y=13000 in game coordinates
# If tile is 480m:
# 3700 / 480 = 7.7 (tile X = 7 or 8)
# In game Y: 13000 / 480 = 27.08
# If Y is bottom-up: tile Y = 27
# If Y is top-down: tile Y = 63 - 27 = 36
print("\nChecking Kavala area tiles...")
for ty in [26, 27, 28, 35, 36, 37]:
    p = os.path.join(layers_dir, f"S_007_{ty:03d}_lco.paa")
    if os.path.exists(p):
        print(f"S_007_{ty:03d}_lco.paa size: {os.path.getsize(p)}")
