import struct

wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"

with open(wrp_path, 'rb') as f:
    f.seek(59664311)
    buf = f.read(512)

# Unpack as floats
floats = struct.unpack('<128f', buf)
for i in range(0, 64, 16):
    print(f"\nBlock at float offset {i}:")
    for row in range(4):
        idx = i + row * 4
        print(f"  {floats[idx]:.4f}, {floats[idx+1]:.4f}, {floats[idx+2]:.4f}, {floats[idx+3]:.4f}")
