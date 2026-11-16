import subprocess
import os
from PIL import Image

pal2pace = r"C:\Program Files (x86)\Steam\steamapps\common\Arma 3 Tools\TexView2\Pal2PacE.exe"
layers_dir = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\data\layers"

subprocess.run([pal2pace, os.path.join(layers_dir, "S_049_038_lco.paa"), r"C:\temp\salt_038.png"], stdout=subprocess.DEVNULL)
subprocess.run([pal2pace, os.path.join(layers_dir, "S_049_025_lco.paa"), r"C:\temp\salt_025.png"], stdout=subprocess.DEVNULL)

for name in ["salt_038", "salt_025"]:
    p = f"C:\\temp\\{name}.png"
    if os.path.exists(p):
        im = Image.open(p).convert('RGB')
        # Check if there are bright white pixels (salt lake)
        white_pixels = sum(1 for px in im.getdata() if px[0] > 200 and px[1] > 200 and px[2] > 200)
        print(f"{name}: white pixels count: {white_pixels}")
