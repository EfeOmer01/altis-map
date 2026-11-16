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
TEMP_DIR   = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\скрипты\temp_seamless"

# Параметры сочности и цвета (точно как в дневной Arma 3)
BRIGHTNESS = 1.48
CONTRAST   = 1.14
SATURATION = 1.30
WEBP_Q     = 85

# Натуральный цвет морской воды Altis
OCEAN_COLOR = (40, 70, 96)

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

print("=== Генератор бесшовных ярких тайлов Altis ===")
print("1. Обработка Zoom 6 с обрезкой перекрытия (480x480 -> 512x512)...")

z6_dir = os.path.join(OUT_BASE, "6")
os.makedirs(z6_dir, exist_ok=True)
all_paa = glob.glob(os.path.join(LAYERS_DIR, "S_*_lco.paa"))

def process_z6(f):
    m = re.search(r"S_(\d+)_(\d+)_lco\.paa", os.path.basename(f))
    if not m: return
    x, y = int(m.group(1)), int(m.group(2))

    col_dir = os.path.join(z6_dir, str(x))
    os.makedirs(col_dir, exist_ok=True)
    out_file = os.path.join(col_dir, f"{y}.webp")

    # Чистый океан
    if os.path.getsize(f) <= 1000:
        with open(out_file, "wb") as o:
            o.write(get_ocean_bytes())
        return

    tmp_png = os.path.join(TEMP_DIR, f"{x}_{y}.png")
    try:
        subprocess.run([PAL2PACE, f, tmp_png],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        with Image.open(tmp_png) as img:
            # Обрезаем 32px перекрытия: берем честные 480x480 пикселей (1 px = 1 метр)
            cropped = img.convert("RGB").crop((0, 0, 480, 480))
            # Масштабируем до стандартных 512x512 тайла Leaflet
            scaled = cropped.resize((512, 512), Image.Resampling.BILINEAR)
            # Применяем цветокоррекцию
            b = ImageEnhance.Brightness(scaled).enhance(BRIGHTNESS)
            c = ImageEnhance.Contrast(b).enhance(CONTRAST)
            s = ImageEnhance.Color(c).enhance(SATURATION)
            s.save(out_file, "WEBP", quality=WEBP_Q)
        os.remove(tmp_png)
    except Exception as e:
        with open(out_file, "wb") as o:
            o.write(get_ocean_bytes())

t0 = time.time()
with ThreadPoolExecutor(max_workers=8) as ex:
    list(ex.map(process_z6, all_paa))
print(f"Zoom 6 завершен за {time.time() - t0:.1f} сек.")

# 2. Пирамида зумов 5..0 (все уровни одинаково яркие!)
for z in range(5, -1, -1):
    tz = time.time()
    dim = 2 ** z
    z_dir = os.path.join(OUT_BASE, str(z))
    os.makedirs(z_dir, exist_ok=True)
    prev = os.path.join(OUT_BASE, str(z + 1))

    def make_pyramid_tile(pt):
        x, y = pt
        col_dir = os.path.join(z_dir, str(x))
        os.makedirs(col_dir, exist_ok=True)
        out = os.path.join(col_dir, f"{y}.webp")

        children = [
            os.path.join(prev, str(2*x),   f"{2*y}.webp"),
            os.path.join(prev, str(2*x+1), f"{2*y}.webp"),
            os.path.join(prev, str(2*x),   f"{2*y+1}.webp"),
            os.path.join(prev, str(2*x+1), f"{2*y+1}.webp"),
        ]
        # Если все 4 океан
        if all(os.path.exists(c) and os.path.getsize(c) < 700 for c in children):
            with open(out, "wb") as o:
                o.write(get_ocean_bytes())
            return

        comp = Image.new("RGB", (1024, 1024), OCEAN_COLOR)
        for cpath, (cx, cy) in zip(children, [(0,0),(512,0),(0,512),(512,512)]):
            if os.path.exists(cpath):
                try:
                    with Image.open(cpath) as ci:
                        comp.paste(ci, (cx, cy))
                except: pass

        downscaled = comp.resize((512, 512), Image.Resampling.BILINEAR)
        downscaled.save(out, "WEBP", quality=WEBP_Q)

    tasks = [(x, y) for x in range(dim) for y in range(dim)]
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(make_pyramid_tile, tasks))
    print(f"Zoom {z} готов за {time.time() - tz:.1f} сек.")

try:
    for f in glob.glob(os.path.join(TEMP_DIR, "*")):
        os.remove(f)
    os.rmdir(TEMP_DIR)
except: pass

print("=== Бесшовная яркая пирамида тайлов успешно сгенерирована! ===")
