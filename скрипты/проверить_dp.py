from PIL import Image

img_path = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\веб\иконки\amazing_marker_DP.png"
im = Image.open(img_path)
print("DP image format:", im.format, "mode:", im.mode, "size:", im.size)
# Sample pixels
pixels = list(im.getdata())
unique_colors = set(pixels)
print("Unique colors count:", len(unique_colors))
print("Sample colors:", list(unique_colors)[:10])
