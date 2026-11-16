"""Создаёт прозрачные тайлы зданий для Leaflet из точных координат WRP.

Слой не меняет спутниковую подложку: вода, реки и текстура земли остаются
видимыми. На максимальном нативном масштабе он рисует контуры крыш и их тени.
"""
import json
import math
import os
from collections import defaultdict

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "данные", "дома_острова.json")
OUT = os.path.join(ROOT, "веб", "слой_зданий", "6")

WORLD = 30720
GRID = 64
TILE_METERS = WORLD / GRID
PIXELS = 512
SCALE = PIXELS / TILE_METERS


def roof_corners(building):
    """Возвращает четыре угла крыши в игровых метрах."""
    x, y = float(building["x"]), float(building["y"])
    width = max(3.0, float(building.get("w", 8)))
    length = max(3.0, float(building.get("l", 8)))
    angle = math.radians(float(building.get("yaw", 0)))
    ca, sa = math.cos(angle), math.sin(angle)
    points = []
    for dx, dy in ((-width / 2, -length / 2), (width / 2, -length / 2),
                   (width / 2, length / 2), (-width / 2, length / 2)):
        points.append((x + dx * ca - dy * sa, y + dx * sa + dy * ca))
    return points


with open(DATA, encoding="utf-8") as source:
    buildings = json.load(source)

# Кладём здание во все тайлы, которых касается его крыша и тень.
by_tile = defaultdict(list)
for building in buildings:
    corners = roof_corners(building)
    shadow = [(x + 3.5, y - 4.5) for x, y in corners]
    all_points = corners + shadow
    min_x = max(0, int(min(p[0] for p in all_points) // TILE_METERS))
    max_x = min(GRID - 1, int(max(p[0] for p in all_points) // TILE_METERS))
    # Игровой Y растёт на север, а номер тайла Leaflet — вниз экрана.
    min_y = max(0, int((WORLD - max(p[1] for p in all_points)) // TILE_METERS))
    max_y = min(GRID - 1, int((WORLD - min(p[1] for p in all_points)) // TILE_METERS))
    for tx in range(min_x, max_x + 1):
        for ty in range(min_y, max_y + 1):
            by_tile[(tx, ty)].append(corners)

os.makedirs(OUT, exist_ok=True)
blank = Image.new("RGBA", (PIXELS, PIXELS), (0, 0, 0, 0))
blank.save(os.path.join(os.path.dirname(OUT), "пустой.webp"), "WEBP", lossless=True)

for (tx, ty), roofs in by_tile.items():
    image = Image.new("RGBA", (PIXELS, PIXELS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image, "RGBA")

    def to_pixel(point):
        x, y = point
        return ((x - tx * TILE_METERS) * SCALE,
                ((WORLD - y) - ty * TILE_METERS) * SCALE)

    # Тень и затем крыша: очертания остаются различимы над спутниковой картой.
    for roof in roofs:
        draw.polygon([to_pixel((x + 3.5, y - 4.5)) for x, y in roof], fill=(18, 22, 24, 96))
    for roof in roofs:
        draw.polygon([to_pixel(point) for point in roof], fill=(92, 96, 100, 145))
        draw.line([to_pixel(point) for point in roof + [roof[0]]], fill=(47, 50, 52, 190), width=1)

    directory = os.path.join(OUT, str(tx))
    os.makedirs(directory, exist_ok=True)
    image.save(os.path.join(directory, f"{ty}.webp"), "WEBP", lossless=True)

print(f"Создано тайлов: {len(by_tile)}; зданий: {len(buildings)}")
