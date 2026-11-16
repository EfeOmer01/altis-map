from PIL import Image

# Let's inspect tile_y27 and tile_y36
im27 = Image.open(r"C:\temp\tile_y27.png")
im36 = Image.open(r"C:\temp\tile_y36.png")

# Let's check average color of 4 quadrants (NW, NE, SW, SE)
# In Kavala: the town is on the coast, ocean is to the West/South.
def stats(im, name):
    w, h = im.size
    print(f"--- {name} ({w}x{h}) ---")
    for qname, box in [("NW", (0, 0, w//2, h//2)),
                       ("NE", (w//2, 0, w, h//2)),
                       ("SW", (0, h//2, w//2, h)),
                       ("SE", (w//2, h//2, w, h))]:
        sub = im.crop(box)
        pixels = list(sub.getdata())
        # rough ocean count: blueish/greyish
        print(f"  {qname}: sample pixel = {pixels[0]}")

stats(im27, "tile_y27")
stats(im36, "tile_y36")
