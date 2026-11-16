from PIL import Image

im = Image.open(r"C:\temp\crop_intersection.png")
w, h = im.size
print(f"crop_intersection size: {w}x{h}")

# Recall that in crop_intersection.png:
# crop was taken from stitch_check.png at:
# crop_x0 = 730 - 400 = 330
# crop_y0 = 678 - 200 = 478
# And stitch_check.png was:
# min_tx = 38, min_ty = 28
# So full leaflet pixel of pixel (cx, cy) in crop_intersection is:
# full_px = cx + 330 + 38 * 512 = cx + 330 + 19456 = cx + 19786
# full_py = cy + 478 + 28 * 512 = cy + 478 + 14336 = cy + 14814
# And game coordinates from full_px, full_py:
# gx = full_px * 15 / 16
# gy = 30720 - full_py * 15 / 16

# The vector intersection in crop_intersection.png was:
# gx_shp = 218924.31 - 200000 = 18924.31
# gy_shp = 16645.46
# full_px = 18924.31 * 16 / 15 = 20185.93
# full_py = (30720 - 16645.46) * 16 / 15 = 14074.54 * 16 / 15 = 15012.84
# cx_vec = 20185.93 - 19786 = 399.93 ~ 400
# cy_vec = 15012.84 - 14814 = 198.84 ~ 199

print(f"Vector junction in crop: cx={400}, cy={199}")
