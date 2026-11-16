import struct

wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"

# Read model table first
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

print(f"Loaded {len(models)} models from table.")

# Find start of the 16-byte record table
# Around 154036151 we saw:
# b40b00 d0d22d46 47069646 02000000 6eb40b00
with open(wrp_path, 'rb') as f:
    # Let's search backward and forward from 154036151
    f.seek(140000000)
    data = f.read(20886218) # till end of file

# Search for sequence of valid (x, y) where 0 <= x <= 30720 and 0 <= y <= 30720 and model_id < len(models)
print("Scanning for start of object table...")
valid_streak = 0
start_offset = None
for offset in range(0, len(data) - 1600, 16):
    is_valid_block = True
    for j in range(10): # check 10 consecutive records
        rec = data[offset + j*16 : offset + (j+1)*16]
        x, y = struct.unpack('<2f', rec[:8])
        mid, oid = struct.unpack('<2I', rec[8:16])
        if not (0 <= x <= 30720 and 0 <= y <= 30720 and mid < len(models)):
            is_valid_block = False
            break
    if is_valid_block:
        start_offset = 140000000 + offset
        print(f"Found table start around {start_offset} (0x{start_offset:x})!")
        break

if start_offset:
    # Now find the exact count
    with open(wrp_path, 'rb') as f:
        f.seek(start_offset)
        obj_count = 0
        model_counts = {}
        while True:
            rec = f.read(16)
            if len(rec) < 16: break
            x, y = struct.unpack('<2f', rec[:8])
            mid, oid = struct.unpack('<2I', rec[8:16])
            if not (0 <= x <= 30720 and 0 <= y <= 30720 and mid < len(models)):
                break
            obj_count += 1
            model_counts[mid] = model_counts.get(mid, 0) + 1
            
        print(f"Total objects in binary table: {obj_count}!")
        print("Top 10 models placed:")
        sorted_m = sorted(model_counts.items(), key=lambda kv: kv[1], reverse=True)
        for mid, cnt in sorted_m[:10]:
            print(f"  [{mid}] {models[mid]}: {cnt}")
