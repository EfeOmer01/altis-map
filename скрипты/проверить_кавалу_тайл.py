import subprocess
import os

pal2pace = r"C:\Program Files (x86)\Steam\steamapps\common\Arma 3 Tools\TexView2\Pal2PacE.exe"
layers_dir = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\data\layers"

# Check Kavala: Kavala has castle and pier at [3742, 12993]
# In 64x64 grid (each tile 480m):
# If Y is bottom-to-top (0 at South): 12993 / 480 = 27 -> S_007_027
# If Y is top-to-bottom (0 at North): (30720 - 12993) / 480 = 36.9 -> S_007_036 or S_007_037

subprocess.run([pal2pace, os.path.join(layers_dir, "S_007_027_lco.paa"), r"C:\temp\t_027.png"], stdout=subprocess.DEVNULL)
subprocess.run([pal2pace, os.path.join(layers_dir, "S_007_036_lco.paa"), r"C:\temp\t_036.png"], stdout=subprocess.DEVNULL)
subprocess.run([pal2pace, os.path.join(layers_dir, "S_007_037_lco.paa"), r"C:\temp\t_037.png"], stdout=subprocess.DEVNULL)

from PIL import Image
print("t_027 exists?", os.path.exists(r"C:\temp\t_027.png"))
print("t_036 exists?", os.path.exists(r"C:\temp\t_036.png"))
print("t_037 exists?", os.path.exists(r"C:\temp\t_037.png"))

# Check image content
for name in ["t_027", "t_036", "t_037"]:
    p = f"C:\\temp\\{name}.png"
    if os.path.exists(p):
        im = Image.open(p)
        print(f"{name}: size={im.size}, colors={len(set(im.getdata()))}")
