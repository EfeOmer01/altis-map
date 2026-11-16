"""Собирает уровни обзора 2 и 3 из готовых тайлов топографической карты."""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "веб" / "topo-tiles" / "12"
OUTPUT = ROOT / "веб" / "topo-tiles" / "overview"

full = Image.new("RGB", (2304, 2304), (180, 200, 220))
for y in range(9):
    for x in range(9):
        with Image.open(SOURCE / f"map_{x}_{y}.jpg") as tile:
            full.paste(tile, (x * 256, y * 256))

for zoom in (2, 3):
    size = 144 * (2 ** zoom)
    image = full.resize((size, size), Image.Resampling.LANCZOS)
    tiles_per_side = (size + 255) // 256
    for x in range(tiles_per_side):
        directory = OUTPUT / str(zoom) / str(x)
        directory.mkdir(parents=True, exist_ok=True)
        for y in range(tiles_per_side):
            image.crop((x * 256, y * 256, (x + 1) * 256, (y + 1) * 256)).save(
                directory / f"{y}.jpg", quality=88
            )
