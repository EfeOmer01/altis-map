import struct

wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"

with open(wrp_path, 'rb') as f:
    f.seek(42619700)
    buf = f.read(512)

# Unpack floats
floats = struct.unpack('<128f', buf)
for i in range(0, 64, 12):
    sub = floats[i:i+12]
    print(f"[{i}] R: {[round(x, 3) for x in sub[:9]]} Pos: {[round(x, 1) for x in sub[9:12]]}")
