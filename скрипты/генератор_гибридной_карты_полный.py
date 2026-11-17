import os
import sys
import time
import numpy as np
from PIL import Image, ImageEnhance

TIFF_PATH = r"C:\Users\efeom\OneDrive\Рабочий стол\1\altis_map\altis_maps\altis_map\source\gotov sat.tif"
RIVER_PATH = r"E:\карта-алтис\веб\river-overlay.webp"
TOPO_DIR = r"E:\карта-алтис\веб\topo-tiles"
OUT_DIR = r"E:\карта-алтис\веб\hybrid-tiles"

Image.MAX_IMAGE_PIXELS = None

def blend_tile(sat_crop_256, topo_img):
    # Enhance satellite colors
    enh = ImageEnhance.Brightness(sat_crop_256).enhance(1.45)
    enh = ImageEnhance.Contrast(enh).enhance(1.15)
    enh = ImageEnhance.Color(enh).enhance(1.30)
    
    t_arr = np.array(topo_img, dtype=np.float32) / 255.0
    s_arr = np.array(enh, dtype=np.float32) / 255.0
    
    # Normalize topo ground (off-white around 0.95 -> 1.0)
    topo_norm = np.clip(t_arr / 0.95, 0, 1)
    
    res = np.clip(s_arr * topo_norm, 0, 1) * 255
    return Image.fromarray(res.astype(np.uint8))

def process_zoom_15(sat, river):
    print("--- Starting Zoom 15 (72x72) ---")
    out_dir = os.path.join(OUT_DIR, "15")
    os.makedirs(out_dir, exist_ok=True)
    
    start_total = time.time()
    for ty in range(72):
        t0 = time.time()
        y0 = int(round(ty * 426.666667))
        y1 = int(round((ty + 1) * 426.666667))
        
        # Read strip from sat
        strip = sat.crop((0, y0, 30720, y1)).convert('RGBA')
        
        # Paste river if in range
        # River is X: 12000..15360, Y: 7200..15840
        if y1 > 7200 and y0 < 15840:
            ry0 = max(0, y0 - 7200)
            ry1 = min(8640, y1 - 7200)
            rc = river.crop((0, ry0, 3360, ry1))
            strip.paste(rc, (12000, max(0, 7200 - y0)), rc)
            
        for tx in range(72):
            topo_file = os.path.join(TOPO_DIR, "15", f"map_{tx}_{ty}.jpg")
            if not os.path.exists(topo_file):
                continue
                
            x0 = int(round(tx * 426.666667))
            x1 = int(round((tx + 1) * 426.666667))
            
            tile_sat = strip.crop((x0, 0, x1, y1 - y0)).convert('RGB')
            tile_sat = tile_sat.resize((256, 256), Image.Resampling.LANCZOS)
            
            topo = Image.open(topo_file).convert('RGB')
            blended = blend_tile(tile_sat, topo)
            blended.save(os.path.join(out_dir, f"map_{tx}_{ty}.jpg"), quality=90)
            
        elapsed = time.time() - t0
        if (ty + 1) % 6 == 0 or ty == 71:
            print(f"Zoom 15: Row {ty + 1}/72 ({((ty + 1)/72)*100:.1f}%) processed in {elapsed:.2f}s | Total: {time.time() - start_total:.1f}s")

def process_zoom_14(sat, river):
    print("--- Starting Zoom 14 (36x36) ---")
    out_dir = os.path.join(OUT_DIR, "14")
    os.makedirs(out_dir, exist_ok=True)
    
    # Each tile is 30720 / 36 = 853.333333 meters
    M_PER_TILE = 30720.0 / 36.0
    for ty in range(36):
        y0 = int(round(ty * M_PER_TILE))
        y1 = int(round((ty + 1) * M_PER_TILE))
        
        strip = sat.crop((0, y0, 30720, y1)).convert('RGBA')
        if y1 > 7200 and y0 < 15840:
            ry0 = max(0, y0 - 7200)
            ry1 = min(8640, y1 - 7200)
            rc = river.crop((0, ry0, 3360, ry1))
            strip.paste(rc, (12000, max(0, 7200 - y0)), rc)
            
        for tx in range(36):
            topo_file = os.path.join(TOPO_DIR, "14", f"map_{tx}_{ty}.jpg")
            if not os.path.exists(topo_file):
                continue
            x0 = int(round(tx * M_PER_TILE))
            x1 = int(round((tx + 1) * M_PER_TILE))
            
            tile_sat = strip.crop((x0, 0, x1, y1 - y0)).convert('RGB')
            tile_sat = tile_sat.resize((256, 256), Image.Resampling.LANCZOS)
            
            topo = Image.open(topo_file).convert('RGB')
            blended = blend_tile(tile_sat, topo)
            blended.save(os.path.join(out_dir, f"map_{tx}_{ty}.jpg"), quality=90)
            
        if (ty + 1) % 12 == 0 or ty == 35:
            print(f"Zoom 14: Row {ty + 1}/36 completed")

def process_zoom_13(sat, river):
    print("--- Starting Zoom 13 (18x18) ---")
    out_dir = os.path.join(OUT_DIR, "13")
    os.makedirs(out_dir, exist_ok=True)
    
    M_PER_TILE = 30720.0 / 18.0
    for ty in range(18):
        y0 = int(round(ty * M_PER_TILE))
        y1 = int(round((ty + 1) * M_PER_TILE))
        
        strip = sat.crop((0, y0, 30720, y1)).convert('RGBA')
        if y1 > 7200 and y0 < 15840:
            ry0 = max(0, y0 - 7200)
            ry1 = min(8640, y1 - 7200)
            rc = river.crop((0, ry0, 3360, ry1))
            strip.paste(rc, (12000, max(0, 7200 - y0)), rc)
            
        for tx in range(18):
            topo_file = os.path.join(TOPO_DIR, "13", f"map_{tx}_{ty}.jpg")
            if not os.path.exists(topo_file):
                continue
            x0 = int(round(tx * M_PER_TILE))
            x1 = int(round((tx + 1) * M_PER_TILE))
            
            tile_sat = strip.crop((x0, 0, x1, y1 - y0)).convert('RGB')
            tile_sat = tile_sat.resize((256, 256), Image.Resampling.LANCZOS)
            
            topo = Image.open(topo_file).convert('RGB')
            blended = blend_tile(tile_sat, topo)
            blended.save(os.path.join(out_dir, f"map_{tx}_{ty}.jpg"), quality=90)
            
    print("Zoom 13 completed")

def process_zoom_12(sat, river):
    print("--- Starting Zoom 12 (9x9) ---")
    out_dir = os.path.join(OUT_DIR, "12")
    os.makedirs(out_dir, exist_ok=True)
    
    M_PER_TILE = 30720.0 / 9.0
    for ty in range(9):
        y0 = int(round(ty * M_PER_TILE))
        y1 = int(round((ty + 1) * M_PER_TILE))
        
        strip = sat.crop((0, y0, 30720, y1)).convert('RGBA')
        if y1 > 7200 and y0 < 15840:
            ry0 = max(0, y0 - 7200)
            ry1 = min(8640, y1 - 7200)
            rc = river.crop((0, ry0, 3360, ry1))
            strip.paste(rc, (12000, max(0, 7200 - y0)), rc)
            
        for tx in range(9):
            topo_file = os.path.join(TOPO_DIR, "12", f"map_{tx}_{ty}.jpg")
            if not os.path.exists(topo_file):
                continue
            x0 = int(round(tx * M_PER_TILE))
            x1 = int(round((tx + 1) * M_PER_TILE))
            
            tile_sat = strip.crop((x0, 0, x1, y1 - y0)).convert('RGB')
            tile_sat = tile_sat.resize((256, 256), Image.Resampling.LANCZOS)
            
            topo = Image.open(topo_file).convert('RGB')
            blended = blend_tile(tile_sat, topo)
            blended.save(os.path.join(out_dir, f"map_{tx}_{ty}.jpg"), quality=90)
            
    print("Zoom 12 completed")

def process_overview(sat, river):
    print("--- Starting Overview (2 and 3) ---")
    # For overview 3: 5x5 grid
    M_PER_TILE_3 = 30720.0 / 5.0
    for x in range(5):
        os.makedirs(os.path.join(OUT_DIR, "overview", "3", str(x)), exist_ok=True)
        for y in range(5):
            topo_file = os.path.join(TOPO_DIR, "overview", "3", str(x), f"{y}.jpg")
            if not os.path.exists(topo_file):
                continue
            x0 = int(round(x * M_PER_TILE_3))
            x1 = int(round((x + 1) * M_PER_TILE_3))
            y0 = int(round(y * M_PER_TILE_3))
            y1 = int(round((y + 1) * M_PER_TILE_3))
            
            tile_sat = sat.crop((x0, y0, x1, y1)).convert('RGB')
            tile_sat = tile_sat.resize((256, 256), Image.Resampling.LANCZOS)
            topo = Image.open(topo_file).convert('RGB')
            blended = blend_tile(tile_sat, topo)
            blended.save(os.path.join(OUT_DIR, "overview", "3", str(x), f"{y}.jpg"), quality=90)
            
    # For overview 2: 3x3 grid
    M_PER_TILE_2 = 30720.0 / 3.0
    for x in range(3):
        os.makedirs(os.path.join(OUT_DIR, "overview", "2", str(x)), exist_ok=True)
        for y in range(3):
            topo_file = os.path.join(TOPO_DIR, "overview", "2", str(x), f"{y}.jpg")
            if not os.path.exists(topo_file):
                continue
            x0 = int(round(x * M_PER_TILE_2))
            x1 = int(round((x + 1) * M_PER_TILE_2))
            y0 = int(round(y * M_PER_TILE_2))
            y1 = int(round((y + 1) * M_PER_TILE_2))
            
            tile_sat = sat.crop((x0, y0, x1, y1)).convert('RGB')
            tile_sat = tile_sat.resize((256, 256), Image.Resampling.LANCZOS)
            topo = Image.open(topo_file).convert('RGB')
            blended = blend_tile(tile_sat, topo)
            blended.save(os.path.join(OUT_DIR, "overview", "2", str(x), f"{y}.jpg"), quality=90)
            
    print("Overview completed")

def main():
    print("Loading Master Satellite TIFF and River Overlay...")
    sat = Image.open(TIFF_PATH)
    river = Image.open(RIVER_PATH)
    print("Files loaded. Starting full hybrid generation...")
    
    t0 = time.time()
    process_zoom_15(sat, river)
    process_zoom_14(sat, river)
    process_zoom_13(sat, river)
    process_zoom_12(sat, river)
    process_overview(sat, river)
    
    print(f"=== ALL TILES GENERATED SUCCESSFULLY IN {time.time() - t0:.1f}s ===")

if __name__ == "__main__":
    main()
