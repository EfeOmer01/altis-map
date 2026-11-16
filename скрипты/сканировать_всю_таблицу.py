import struct

wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"

# Models
models = []
with open(wrp_path, 'rb') as f:
    f.seek(36652646)
    while True:
        line = b""
        ch = f.read(1)
        if not ch: break
        while ch != b'\x00':
            line += ch
            ch = f.read(1)
            if len(line) > 500: break
        if not line or not line.endswith(b'.p3d'): break
        models.append(line.decode('ascii', errors='ignore'))

# Step backward from 154036154
curr = 154036154
with open(wrp_path, 'rb') as f:
    # Walk backward
    while curr > 100000000:
        f.seek(curr - 16)
        rec = f.read(16)
        x, y = struct.unpack('<2f', rec[:8])
        mid, oid = struct.unpack('<2I', rec[8:16])
        if not (0 <= x <= 30720 and 0 <= y <= 30720 and mid < len(models)):
            break
        curr -= 16

start_pos = curr
print(f"Table starts at: {start_pos} (0x{start_pos:x})")

# Now walk forward to find end
with open(wrp_path, 'rb') as f:
    f.seek(start_pos)
    count = 0
    model_counts = {}
    objects = []
    while True:
        rec = f.read(16)
        if len(rec) < 16: break
        x, y = struct.unpack('<2f', rec[:8])
        mid, oid = struct.unpack('<2I', rec[8:16])
        if not (0 <= x <= 30720 and 0 <= y <= 30720 and mid < len(models)):
            break
        count += 1
        model_counts[mid] = model_counts.get(mid, 0) + 1
        # Check if house/building
        mname = models[mid].lower()
        if any(k in mname for k in ['house', 'shed', 'shop', 'church', 'hospital', 'factory', 'building', 'garage', 'stone', 'slum', 'addon', 'hangar', 'terminal', 'fuelstation', 'pier', 'barracks', 'tower', 'wall']):
            objects.append((mname, x, y, mid, oid))

print(f"Total objects in binary table: {count}!")
print(f"Total building/wall/structure objects: {len(objects)}!")
sorted_m = sorted(model_counts.items(), key=lambda kv: kv[1], reverse=True)
print("\nTop 20 models:")
for mid, cnt in sorted_m[:20]:
    print(f"  [{mid}] {models[mid]}: {cnt}")
