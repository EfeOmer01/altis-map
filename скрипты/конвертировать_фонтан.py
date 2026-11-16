import os
import sys

# Load convert function from скрипты/конвертировать_иконки.py
sys.path.append(r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\скрипты")

# Let's inspect the PAA reading in конвертировать_иконки
with open(r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\скрипты\конвертировать_иконки.py", 'r', encoding='utf-8') as f:
    code = f.read()

# Execute code to get paa_to_image
loc = {}
exec(code, loc)

paa_to_image = loc['paa_to_image']
paa_path = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\fountain_CA.paa"
png_path = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\веб\иконки\loc_Fountain.png"

im = paa_to_image(paa_path)
if im:
    im.save(png_path)
    print("Successfully converted fountain_CA.paa to loc_Fountain.png!")
else:
    print("Failed to convert fountain_CA.paa")
