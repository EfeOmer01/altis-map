import struct

wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"

with open(wrp_path, 'rb') as f:
    f.seek(36694910 + 5)
    buf = f.read(2500000)

pos = 0
buildings = []
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
        if any(k in cls.lower() or k in model.lower() for k in ['house', 'shed', 'building', 'stone', 'shop', 'barn', 'garage', 'fuelstation', 'factory', 'church', 'hospital', 'barracks', 'hangar', 'terminal', 'pier', 'lighthouse', 'tower', 'slum', 'addon']):
            buildings.append((cls, x, y, z))

print(f"Total buildings: {len(buildings)}")
xs = [b[1] for b in buildings]
ys = [b[2] for b in buildings]
print(f"X range: {min(xs):.1f} to {max(xs):.1f}")
print(f"Y range: {min(ys):.1f} to {max(ys):.1f}")
