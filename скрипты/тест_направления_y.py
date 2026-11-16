import os
import subprocess
from PIL import Image

pal2pace = r"C:\Program Files (x86)\Steam\steamapps\common\Arma 3 Tools\TexView2\Pal2PacE.exe"
layers_dir = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\data\layers"

# In Altis:
# X=7 is Kavala / western side.
# North of Altis is ocean or Syrta (at Y ~ 45..50 in tiles if 0 is south, or Y ~ 10..15 if 0 is north)
# Let's inspect S_007_010 vs S_007_050
subprocess.run([pal2pace, os.path.join(layers_dir, "S_007_010_lco.paa"), r"C:\temp\tile_y10.png"], stdout=subprocess.DEVNULL)
subprocess.run([pal2pace, os.path.join(layers_dir, "S_007_027_lco.paa"), r"C:\temp\tile_y27.png"], stdout=subprocess.DEVNULL)
subprocess.run([pal2pace, os.path.join(layers_dir, "S_007_036_lco.paa"), r"C:\temp\tile_y36.png"], stdout=subprocess.DEVNULL)
subprocess.run([pal2pace, os.path.join(layers_dir, "S_007_050_lco.paa"), r"C:\temp\tile_y50.png"], stdout=subprocess.DEVNULL)

# Let's also check tile at center: X=32, Y=10 vs Y=50
subprocess.run([pal2pace, os.path.join(layers_dir, "S_032_010_lco.paa"), r"C:\temp\tile_32_10.png"], stdout=subprocess.DEVNULL)
subprocess.run([pal2pace, os.path.join(layers_dir, "S_032_050_lco.paa"), r"C:\temp\tile_32_50.png"], stdout=subprocess.DEVNULL)

for name in ["tile_y10", "tile_y27", "tile_y36", "tile_y50", "tile_32_10", "tile_32_50"]:
    p = f"C:\\temp\\{name}.png"
    if os.path.exists(p):
        sz = os.path.getsize(p)
        print(f"{name}: size={sz}")
