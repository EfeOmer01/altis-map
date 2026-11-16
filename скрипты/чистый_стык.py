import os
from PIL import Image

tiles_dir = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\веб\тайлы\6"

# Load clean tile 39, 29
t39_29 = Image.open(os.path.join(tiles_dir, "39", "29.webp"))
# Full_px of tile (39, 29) is:
# left = 39 * 512 = 19968
# top = 29 * 512 = 14848

# Our vector junction was at:
# full_px = 20185.93
# full_py = 15012.84
# In tile 39, 29:
# tx = full_px - 19968 = 217.93 ~ 218
# ty = full_py - 14848 = 164.84 ~ 165

# Crop 200x200 around (218, 165)
clean_crop = t39_29.crop((218 - 100, 165 - 100, 218 + 100, 165 + 100))
clean_crop.save(r"C:\temp\clean_junction.png")
print("Saved clean_junction.png (center is vector junction 218, 165)")
