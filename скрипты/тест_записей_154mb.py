import struct

wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"

with open(wrp_path, 'rb') as f:
    f.seek(154036151)
    buf = f.read(512)

print("Record samples around 154MB:")
for i in range(0, 256, 16):
    chunk = buf[i:i+16]
    if len(chunk) < 16: break
    f1, f2 = struct.unpack('<2f', chunk[:8])
    i1, i2 = struct.unpack('<2I', chunk[8:16])
    print(f"[{i:03d}] floats: ({f1:.1f}, {f2:.1f}), ints: ({i1}, {i2} / 0x{i2:08x})")
