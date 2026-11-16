import struct
from collections import Counter

wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"

with open(wrp_path, 'rb') as f:
    f.seek(36694910 + 5)
    buf = f.read(2500000)

pos = 0
objects = []
while pos < len(buf) - 20:
    end_cls = buf.find(b'\x00', pos)
    if end_cls == -1 or end_cls - pos > 100: break
    try:
        cls = buf[pos:end_cls].decode('ascii')
    except: break
    if not cls or not all(c.isalnum() or c == '_' for c in cls): break
        
    pos = end_cls + 1
    end_model = buf.find(b'\x00', pos)
    if end_model == -1 or end_model - pos > 200: break
    try:
        model = buf[pos:end_model].decode('ascii')
    except: break
    if not model.endswith('.p3d'): break
        
    pos = end_model + 1
    x, z, y = struct.unpack('<3f', buf[pos:pos+12])
    obj_id = struct.unpack('<I', buf[pos+12:pos+16])[0]
    pos += 16
    
    if 0 <= x <= 30720 and 0 <= y <= 30720:
        objects.append((cls, model, x, y, z, obj_id))

print(f"Total objects parsed: {len(objects)}")
class_counts = Counter(obj[0] for obj in objects)
print("\nTop 30 object classes:")
for cls, count in class_counts.most_common(30):
    print(f"  {cls}: {count}")

# Check houses/buildings specifically
houses = [obj for obj in objects if any(k in obj[0].lower() or k in obj[1].lower() for k in ['house', 'shed', 'building', 'stone', 'shop', 'barn', 'garage', 'fuelstation', 'factory', 'church', 'hospital', 'barracks', 'hangar', 'terminal', 'pier', 'lighthouse', 'tower', 'slum', 'addon'])]
print(f"\nTotal buildings/structures found: {len(houses)}")
house_classes = Counter(h[0] for h in houses)
print("Top 20 building classes:")
for cls, count in house_classes.most_common(20):
    print(f"  {cls}: {count}")
