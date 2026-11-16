from PIL import Image

img_path = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\веб\иконки\amazing_marker_DP.png"
im = Image.open(img_path).convert('RGBA')

w, h = im.size
out = Image.new('RGBA', (w, h))

for y in range(h):
    for x in range(w):
        r, g, b, a = im.getpixel((x, y))
        if a > 20:
            # Check brightness
            brightness = (r + g + b) / 3.0
            if brightness > 120:
                # Tint to yellow inside: Arma 3 ColorYellow #e5b300 / #ffd700
                factor = brightness / 255.0
                nr = int(255 * factor)
                ng = int(210 * factor)
                nb = int(20 * factor)
                out.putpixel((x, y), (nr, ng, nb, a))
            else:
                out.putpixel((x, y), (r, g, b, a))
        else:
            out.putpixel((x, y), (0, 0, 0, 0))

out.save(img_path)
print("Updated amazing_marker_DP.png with yellow interior!")
