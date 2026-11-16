import json
from PIL import Image, ImageDraw

# Game coordinate [18925, 16644]
# In Leaflet at zoom 6:
# 64x64 tiles, each 512x512 pixels. Total map = 32768 x 32768 pixels.
# Each pixel = 30720 / 32768 = 0.9375 meters (or 1 tile = 512 px = 480 meters).
# Pixel X in full map = (gx / 30720) * 32768 = gx * (32768 / 30720) = gx * (64 / 60) = gx / 0.9375 = gx * 16 / 15.
# Wait! In app.js:
# latLngToGame: gx = ll.lng * K where K = 30720 / 512 = 60.
# At zoom 6, Leaflet map is 32768x32768.
# In Leaflet CRS.Simple:
# lat goes from 0 down to -512.
# lng goes from 0 to 512.
# gx = lng * 60  ->  lng = gx / 60.
# gy = 30720 + lat * 60  ->  lat = (gy - 30720) / 60.
# At zoom 6, pixel coordinate in Leaflet:
# px_x = lng * (2^6) = (gx / 60) * 64 = gx * (64 / 60) = gx * 16 / 15.
# px_y = -lat * (2^6) = ((30720 - gy) / 60) * 64 = (30720 - gy) * 16 / 15.

gx_center = 18925.0
gy_center = 16644.0

# Tile containing center:
tile_x = int(gx_center / 480)
tile_y = int((30720 - gy_center) / 480)

print(f"Target is in tile ({tile_x}, {tile_y})")
print(f"Leaflet full pixel coords: px_x = {gx_center * 16 / 15:.1f}, px_y = {(30720 - gy_center) * 16 / 15:.1f}")
