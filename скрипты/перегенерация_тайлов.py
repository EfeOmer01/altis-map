"""
Перегенерация тайлов с улучшенной яркостью/контрастом + качество 95
"""
import os
import glob
import re
import time
import subprocess
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageEnhance

LAYERS_DIR = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\data\layers"
OUT_BASE   = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\веб\тайлы"
PAL2PACE   = r"C:\Program Files (x86)\Steam\steamapps\common\Arma 3 Tools\TexView2\Pal2PacE.exe"
TEMP_DIR   = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\скрипты\temp_png2"

BRIGHTNESS = 1.35
CONTRAST   = 1.08
WEBP_Q     = 95

OCEAN_COLOR = (36, 58, 82)   # Тёмно-синий океан (приятнее серого)

os.makedirs(OUT_BASE, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

ocean_bytes = None
def get_ocean_bytes():
    global ocean_bytes
    if ocean_bytes is None:
        p = os.path.join(TEMP_DIR, "ocean.webp")
        Image.new("RGB", (512, 512), OCEAN_COLOR).save(p, "WEBP", quality=WEBP_Q)
        with open(p, "rb") as f:
            ocean_bytes = f.read()
    return ocean_bytes

print("=== Перегенерация тайлов (яркость +35%, контраст +8%) ===")

all_paa = glob.glob(os.path.join(LAYERS_DIR, "S_*_lco.paa"))
z6_dir  = os.path.join(OUT_BASE, "6")

def process_z6(f):
    m = re.search(r"S_(\d+)_(\d+)_lco\.paa", os.path.basename(f))
    if not m: return
    x, y = int(m.group(1)), int(m.group(2))

    col_dir = os.path.join(z6_dir, str(x))
    os.makedirs(col_dir, exist_ok=True)
    out_file = os.path.join(col_dir, f"{y}.webp")

    if os.path.getsize(f) <= 1000:
        with open(out_file, "wb") as o:
            o.write(get_ocean_bytes())
        return

    tmp_png = os.path.join(TEMP_DIR, f"{x}_{y}.png")
    try:
        subprocess.run([PAL2PACE, f, tmp_png],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        with Image.open(tmp_png) as img:
            rgb = img.convert("RGB")
            if rgb.size != (512, 512):
                rgb = rgb.resize((512, 512), Image.Resampling.LANCZOS)
            # Яркость и контраст
            rgb = ImageEnhance.Brightness(rgb).enhance(BRIGHTNESS)
            rgb = ImageEnhance.Contrast(rgb).enhance(CONTRAST)
            rgb.save(out_file, "WEBP", quality=WEBP_Q)
        os.remove(tmp_png)
    except Exception:
        with open(out_file, "wb") as o:
            o.write(get_ocean_bytes())

t0 = time.time()
with ThreadPoolExecutor(max_workers=8) as ex:
    list(ex.map(process_z6, all_paa))
print(f"Zoom 6 готов за {time.time() - t0:.1f} с")

# Пирамида зумов 5..0
for z in range(5, -1, -1):
    tz = time.time()
    dim = 2 ** z
    z_dir = os.path.join(OUT_BASE, str(z))
    os.makedirs(z_dir, exist_ok=True)
    prev = os.path.join(OUT_BASE, str(z + 1))

    def mk(args):
        x, y = args
        os.makedirs(os.path.join(z_dir, str(x)), exist_ok=True)
        out = os.path.join(z_dir, str(x), f"{y}.webp")

        children = [
            os.path.join(prev, str(2*x),   f"{2*y}.webp"),
            os.path.join(prev, str(2*x+1), f"{2*y}.webp"),
            os.path.join(prev, str(2*x),   f"{2*y+1}.webp"),
            os.path.join(prev, str(2*x+1), f"{2*y+1}.webp"),
        ]
        if all(os.path.exists(c) and os.path.getsize(c) < 700 for c in children):
            with open(out, "wb") as o:
                o.write(get_ocean_bytes())
            return

        comp = Image.new("RGB", (1024, 1024), OCEAN_COLOR)
        for path, (cx, cy) in zip(children, [(0,0),(512,0),(0,512),(512,512)]):
            if os.path.exists(path):
                try:
                    with Image.open(path) as ci:
                        comp.paste(ci, (cx, cy))
                except: pass
        comp.resize((512, 512), Image.Resampling.LANCZOS).save(out, "WEBP", quality=WEBP_Q)

    tasks = [(x, y) for x in range(dim) for y in range(dim)]
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(mk, tasks))
    print(f"  Zoom {z} готов за {time.time() - tz:.1f} с")

try:
    for f in glob.glob(os.path.join(TEMP_DIR, "*")):
        os.remove(f)
    os.rmdir(TEMP_DIR)
except: pass

print("=== Все тайлы перегенерированы! ===")
