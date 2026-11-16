from PIL import Image

im = Image.open(r"C:\temp\stitch_check.png")
# Center at (730, 678)
crop = im.crop((730 - 400, 678 - 200, 730 + 400, 678 + 200))
crop.save(r"C:\temp\crop_intersection.png")
print("Saved crop_intersection.png (800x400)")
