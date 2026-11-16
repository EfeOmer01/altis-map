from PIL import Image

im = Image.open(r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\веб\иконки\amazing_marker_DP.png").convert("RGBA")
print("Image size:", im.size)
colors = im.getcolors(maxcolors=2000)
print("Unique colors count:", len(colors) if colors else ">2000")
# Print some of the colors
if colors:
    for count, col in sorted(colors, reverse=True)[:10]:
        print(f"  {count} pixels of {col}")
