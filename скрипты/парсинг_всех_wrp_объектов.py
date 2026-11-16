import struct
import time

wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"

t0 = time.time()
with open(wrp_path, 'rb') as f:
    f.seek(36694910 + 5) # start at Land_lighthouse_small_f
    buf = f.read(15000000) # read 15MB

pos = 0
count = 0
objects = []

while pos < len(buf) - 20:
    end_cls = buf.find(b'\x00', pos)
    if end_cls == -1 or end_cls - pos > 100:
        break
    try:
        cls = buf[pos:end_cls].decode('ascii')
    except:
        break
    
    # Check if cls looks valid (alphanumeric + underscores)
    if not cls or not all(c.isalnum() or c == '_' for c in cls):
        break
        
    pos = end_cls + 1
    end_model = buf.find(b'\x00', pos)
    if end_model == -1 or end_model - pos > 200:
        break
    try:
        model = buf[pos:end_model].decode('ascii')
    except:
        break
        
    if not model.endswith('.p3d'):
        break
        
    pos = end_model + 1
    if pos + 16 > len(buf):
        break
        
    x, z, y = struct.unpack('<3f', buf[pos:pos+12])
    obj_id = struct.unpack('<I', buf[pos+12:pos+16])[0]
    pos += 16
    
    count += 1
    # Check bounds of Altis (0..30720)
    if 0 <= x <= 30720 and 0 <= y <= 30720:
        objects.append((cls, model, x, y, z, obj_id))

t1 = time.time()
print(f"Parsed {count} objects in {t1 - t0:.2f}s! Valid in-bounds objects: {len(objects)}")
print("Sample parsed objects:")
for obj in objects[:10]:
    print(f"  {obj[0]}: ({obj[2]:.1f}, {obj[3]:.1f})")
