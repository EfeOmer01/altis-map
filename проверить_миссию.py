import re

path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\newAmazingLife.AmazingMap\mission.cpp"
with open(path, "r", encoding="latin1") as f:
    text = f.read()

# Find markers
marker_blocks = re.findall(r'class Item\d+\s*\{[^\}]+dataType="Marker";[^\}]+\};', text)
print(f"Total marker blocks: {len(marker_blocks)}")

# Sample a marker block
if marker_blocks:
    print("Sample marker:\n", marker_blocks[0][:300])

# Find custom placed objects
object_blocks = re.findall(r'dataType="Object";\s*class PositionInfo\s*\{\s*position\[\]=\{([^\}]+)\};', text)
print(f"Total custom placed objects: {len(object_blocks)}")
