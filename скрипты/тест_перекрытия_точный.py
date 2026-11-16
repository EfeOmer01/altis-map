import subprocess
import os
import numpy as np
from PIL import Image

pal2pace = r"C:\Program Files (x86)\Steam\steamapps\common\Arma 3 Tools\TexView2\Pal2PacE.exe"
layers_dir = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\data\layers"

# Pick two adjacent land tiles that have rich details (like roads or buildings)
# Tile (7, 27) and (8, 27) (Kavala area) or (20, 25) and (21, 25)
p0 = os.path.join(layers_dir, "S_020_025_lco.paa")
p1 = os.path.join(layers_dir, "S_021_025_lco.paa")
p_down = os.path.join(layers_dir, "S_020_026_lco.paa")

subprocess.run([pal2pace, p0, r"C:\temp\tile_0.png"], stdout=subprocess.DEVNULL)
subprocess.run([pal2pace, p1, r"C:\temp\tile_1.png"], stdout=subprocess.DEVNULL)
subprocess.run([pal2pace, p_down, r"C:\temp\tile_down.png"], stdout=subprocess.DEVNULL)

im0 = np.array(Image.open(r"C:\temp\tile_0.png").convert("RGB"))
im1 = np.array(Image.open(r"C:\temp\tile_1.png").convert("RGB"))
im_down = np.array(Image.open(r"C:\temp\tile_down.png").convert("RGB"))

print(f"im0 shape: {im0.shape}, im1 shape: {im1.shape}")

# Find horizontal match between im0 and im1:
# For various overlap widths W in range 0..64:
print("\nTesting horizontal overlap between tile (20,25) and (21,25):")
best_diff = 999999
best_w = -1
for w in range(0, 65):
    # If tile 0 right edge overlaps with tile 1 left edge:
    if w == 0:
        continue
    strip0 = im0[:, 512-w : 512]
    strip1 = im1[:, 0 : w]
    diff = np.mean(np.abs(strip0.astype(float) - strip1.astype(float)))
    if diff < best_diff:
        best_diff = diff
        best_w = w
    if w in [0, 8, 16, 24, 30, 32, 34, 48, 64]:
        print(f"  w={w:2d} -> mean diff = {diff:.3f}")

print(f"--> BEST horizontal overlap: w={best_w} with diff = {best_diff:.4f}")

# Find vertical match between im0 and im_down:
print("\nTesting vertical overlap between tile (20,25) and (20,26):")
best_diff_v = 999999
best_w_v = -1
for w in range(1, 65):
    strip0 = im0[512-w : 512, :]
    strip_down = im_down[0 : w, :]
    diff = np.mean(np.abs(strip0.astype(float) - strip_down.astype(float)))
    if diff < best_diff_v:
        best_diff_v = diff
        best_w_v = w
    if w in [8, 16, 24, 30, 32, 34, 48, 64]:
        print(f"  w={w:2d} -> mean diff = {diff:.3f}")

print(f"--> BEST vertical overlap: w={best_w_v} with diff = {best_diff_v:.4f}")
