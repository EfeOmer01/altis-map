import struct

wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"

with open(wrp_path, 'rb') as f:
    buf = f.read(512)

# Unpack first 64 uint32s
ints = struct.unpack('<64I', buf[:256])
floats = struct.unpack('<64f', buf[:256])

print("Header uint32s and floats:")
for i in range(32):
    print(f"[{i:02d}] 0x{i*4:03x}: int={ints[i]:<10} (0x{ints[i]:08x})  float={floats[i]:.4f}")
