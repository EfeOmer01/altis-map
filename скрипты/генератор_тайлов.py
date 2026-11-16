import os
import glob
import re
import time
import subprocess
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

# Пути
LAYERS_DIR = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\data\layers"
OUT_BASE = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\веб\тайлы"
PAL2PACE = r"C:\Program Files (x86)\Steam\steamapps\common\Arma 3 Tools\TexView2\Pal2PacE.exe"
TEMP_DIR = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\скрипты\temp_png"

os.makedirs(OUT_BASE, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# 1. Создаем эталонный тайл океана
OCEAN_COLOR = (74, 72, 69)
ocean_img = Image.new("RGB", (512, 512), OCEAN_COLOR)
ocean_bytes = None

def get_ocean_bytes():
    global ocean_bytes
    if ocean_bytes is None:
        ocean_path = os.path.join(TEMP_DIR, "ocean.webp")
        ocean_img.save(ocean_path, "WEBP", quality=80)
        with open(ocean_path, "rb") as f:
            ocean_bytes = f.read()
    return ocean_bytes

print("=== Генератор тайлов карты Altis (AmazingMap) ===")
print("Подготовка Zoom 6 (исходные 64x64 тайла)...")

z6_dir = os.path.join(OUT_BASE, "6")
os.makedirs(z6_dir, exist_ok=True)

all_paa = glob.glob(os.path.join(LAYERS_DIR, "S_*_lco.paa"))
print(f"Найдено PAA файлов: {len(all_paa)}")

# Таблица для отслеживания океанических тайлов на зуме 6
is_ocean_z6 = {}

def process_tile_z6(f):
    m = re.search(r"S_(\d+)_(\d+)_lco\.paa", os.path.basename(f))
    if not m:
        return
    x = int(m.group(1))
    y = int(m.group(2))

    col_dir = os.path.join(z6_dir, str(x))
    os.makedirs(col_dir, exist_ok=True)
    out_file = os.path.join(col_dir, f"{y}.webp")

    # Если уже сгенерирован
    if os.path.exists(out_file) and os.path.getsize(out_file) > 100:
        is_ocean_z6[(x, y)] = (os.path.getsize(f) <= 1000)
        return

    # Проверка на океан
    if os.path.getsize(f) <= 1000:
        with open(out_file, "wb") as out:
            out.write(get_ocean_bytes())
        is_ocean_z6[(x, y)] = True
        return

    is_ocean_z6[(x, y)] = False

    # Конвертируем PAA -> PNG -> WebP
    tmp_png = os.path.join(TEMP_DIR, f"{x}_{y}.png")
    try:
        subprocess.run([PAL2PACE, f, tmp_png], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        if os.path.exists(tmp_png):
            with Image.open(tmp_png) as img:
                rgb = img.convert("RGB")
                if rgb.size != (512, 512):
                    rgb = rgb.resize((512, 512), Image.Resampling.BILINEAR)
                rgb.save(out_file, "WEBP", quality=82)
            os.remove(tmp_png)
    except Exception as e:
        # В случае ошибки пишем океан
        with open(out_file, "wb") as out:
            out.write(get_ocean_bytes())

t0 = time.time()
with ThreadPoolExecutor(max_workers=8) as executor:
    list(executor.map(process_tile_z6, all_paa))
print(f"Zoom 6 сгенерирован за {time.time() - t0:.1f} сек.")

# 2. Генерация пирамиды зумов (Zoom 5 -> Zoom 0)
for z in range(5, -1, -1):
    tz0 = time.time()
    cur_dim = 2 ** z
    z_dir = os.path.join(OUT_BASE, str(z))
    os.makedirs(z_dir, exist_ok=True)
    prev_dir = os.path.join(OUT_BASE, str(z + 1))
    print(f"Генерация Zoom {z} (размер сетки {cur_dim}x{cur_dim})...")

    def make_tile(x, y):
        col_dir = os.path.join(z_dir, str(x))
        os.makedirs(col_dir, exist_ok=True)
        out_file = os.path.join(col_dir, f"{y}.webp")

        # 4 дочерних тайла на зуме z+1: (2x, 2y), (2x+1, 2y), (2x, 2y+1), (2x+1, 2y+1)
        c00 = os.path.join(prev_dir, str(2 * x), f"{2 * y}.webp")
        c10 = os.path.join(prev_dir, str(2 * x + 1), f"{2 * y}.webp")
        c01 = os.path.join(prev_dir, str(2 * x), f"{2 * y + 1}.webp")
        c11 = os.path.join(prev_dir, str(2 * x + 1), f"{2 * y + 1}.webp")

        # Если все 4 - океан (размер около 530 байт), не делаем ресайз
        children = [c00, c10, c01, c11]
        all_ocean = all(os.path.exists(c) and os.path.getsize(c) < 600 for c in children)
        if all_ocean:
            with open(out_file, "wb") as out:
                out.write(get_ocean_bytes())
            return

        # Склеиваем 2x2 в 1024x1024 и уменьшаем в 512x512
        comp = Image.new("RGB", (1024, 1024), OCEAN_COLOR)
        coords = [(0, 0), (512, 0), (0, 512), (512, 512)]
        for child_path, (cx, cy) in zip(children, coords):
            if os.path.exists(child_path):
                try:
                    with Image.open(child_path) as cimg:
                        comp.paste(cimg, (cx, cy))
                except:
                    pass

        downscaled = comp.resize((512, 512), Image.Resampling.BILINEAR)
        downscaled.save(out_file, "WEBP", quality=82)

    tasks = [(x, y) for x in range(cur_dim) for y in range(cur_dim)]
    with ThreadPoolExecutor(max_workers=8) as executor:
        executor.map(lambda pt: make_tile(pt[0], pt[1]), tasks)
    print(f"Zoom {z} готов за {time.time() - tz0:.1f} сек.")

# Очистка временных файлов
try:
    for f in glob.glob(os.path.join(TEMP_DIR, "*")):
        os.remove(f)
    os.rmdir(TEMP_DIR)
except:
    pass

print("=== Все тайлы успешно сгенерированы! ===")
