import os
import subprocess
import numpy as np
from PIL import Image

pal2pace = r"C:\Program Files (x86)\Steam\steamapps\common\Arma 3 Tools\TexView2\Pal2PacE.exe"
layers_dir = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\data\layers"

# Pick tile (39, 29) which is right where our road is!
# And neighbor tile to the right: (40, 29)
# And neighbor tile below: (39, 30)
p0 = os.path.join(layers_dir, "S_039_029_lco.paa")
p_right = os.path.join(layers_dir, "S_040_029_lco.paa")
p_down = os.path.join(layers_dir, "S_039_030_lco.paa")

subprocess.run([pal2pace, p0, r"C:\temp\t39_29.png"], stdout=subprocess.DEVNULL)
subprocess.run([pal2pace, p_right, r"C:\temp\t40_29.png"], stdout=subprocess.DEVNULL)
subprocess.run([pal2pace, p_down, r"C:\temp\t39_30.png"], stdout=subprocess.DEVNULL)

im0 = np.array(Image.open(r"C:\temp\t39_29.png").convert("RGB"), dtype=float)
im_right = np.array(Image.open(r"C:\temp\t40_29.png").convert("RGB"), dtype=float)
im_down = np.array(Image.open(r"C:\temp\t39_30.png").convert("RGB"), dtype=float)

print(f"im0: {im0.shape}")

# Test 1: Where does im0 match im_right?
# Does the RIGHT edge of im0 match the LEFT edge of im_right?
# Let's test: for offset dx in range(400, 520):
# compare im0[:, dx : 512] with im_right[:, 0 : 512 - dx]
print("\n--- Horizontal Match (im0 right vs im_right left) ---")
best_diff_h = 1e9
best_dx = -1
for dx in range(450, 510):
    w = 512 - dx
    diff = np.mean(np.abs(im0[:, dx:512] - im_right[:, 0:w]))
    if diff < best_diff_h:
        best_diff_h = diff
        best_dx = dx
    if dx in [464, 480, 496]:
        print(f"  dx={dx} (overlap width={w}) -> diff={diff:.4f}")
print(f"BEST dx={best_dx} (overlap width={512-best_dx}) with diff={best_diff_h:.4f}")

# Test 2: Where does im0 match im_down?
# Does the BOTTOM edge of im0 match the TOP edge of im_down?
print("\n--- Vertical Match (im0 bottom vs im_down top) ---")
best_diff_v = 1e9
best_dy = -1
for dy in range(450, 510):
    h = 512 - dy
    diff = np.mean(np.abs(im0[dy:512, :] - im_down[0:h, :]))
    if diff < best_diff_v:
        best_diff_v = diff
        best_dy = dy
    if dy in [464, 480, 496]:
        print(f"  dy={dy} (overlap height={h}) -> diff={diff:.4f}")
print(f"BEST dy={best_dy} (overlap height={512-best_dy}) with diff={best_diff_v:.4f}")

# Test 3: What about the TOP and LEFT edge of tile (0, 0)?
p_0_0 = os.path.join(layers_dir, "S_000_000_lco.paa")
print(f"\nS_000_000_lco.paa exists: {os.path.exists(p_0_0)}")
