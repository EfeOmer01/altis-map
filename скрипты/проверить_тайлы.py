import os

base = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\веб\тайлы"
for z in range(0, 9):
    z_dir = os.path.join(base, str(z))
    if not os.path.exists(z_dir):
        print(f"Zoom {z}: NOT FOUND!")
        continue
    # Count files
    count = 0
    for root, dirs, files in os.walk(z_dir):
        count += len(files)
    print(f"Zoom {z}: {count} files")
