from PIL import Image

im = Image.open(r"C:\temp\stitch_check.png")

# Let's crop 3 buildings from stitch_check:
# Building 1: near (18666.9, 16665.5)
# Building 2: near (18937.5, 16625.3)
# Building 3: near (19085.7, 16633.8)

min_tx, min_ty = 38, 28
def g2c(gx, gy):
    px = gx * 16 / 15
    py = (30720 - gy) * 16 / 15
    return (int(px - min_tx * 512), int(py - min_ty * 512))

for name, (gx, gy) in [("bldg1", (18667, 16666)), ("bldg2", (18938, 16625)), ("bldg3", (19086, 16634))]:
    cx, cy = g2c(gx, gy)
    sub = im.crop((cx - 50, cy - 50, cx + 50, cy + 50))
    sub.save(f"C:\\temp\\zoom_{name}.png")
    print(f"Saved zoom_{name}.png around ({cx}, {cy})")
