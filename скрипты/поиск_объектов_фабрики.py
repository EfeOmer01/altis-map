import struct

wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"

with open(wrp_path, 'rb') as f:
    f.seek(36694910 + 5)
    buf = f.read(2500000)

pos = 0
found_objects = []

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
    extra = struct.unpack('<I', buf[pos+12:pos+16])[0]
    pos += 16
    
    # Check if near Factory02 (12577, 16352)
    if 12300 <= x <= 12900 and 16000 <= y <= 16800:
        found_objects.append((cls, model, x, y, z, extra))

print(f"Found {len(found_objects)} objects near Factory02:")
for obj in found_objects:
    print(f"  {obj[0]:<30} at ({obj[2]:.1f}, {obj[3]:.1f}, Z={obj[4]:.1f}) extra={hex(obj[5])}")
