from PIL import Image, ImageDraw, ImageFont

# Create a crisp 32x32 green ATM icon
img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Dark circular border
draw.ellipse([1, 1, 30, 30], fill=(22, 163, 74, 255), outline=(15, 23, 42, 230), width=2)
# Inner ATM text or card symbol
# Draw a stylized card/slot and "ATM"
try:
    font = ImageFont.truetype("arial.ttf", 10)
    draw.text((16, 16), "ATM", fill=(255, 255, 255, 255), anchor="mm", font=font)
except:
    draw.text((8, 10), "ATM", fill=(255, 255, 255, 255))

img.save(r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\веб\иконки\atm.png")
print("Saved atm.png successfully!")
