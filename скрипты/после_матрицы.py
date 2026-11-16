import struct

wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"

with open(wrp_path, 'rb') as f:
    f.seek(41867497 + 35 + 5 + 48) # right after the 48 bytes
    buf = f.read(128)

print("Bytes right after transform matrix:")
print("Hex:", buf[:64].hex())
# Check ints / floats
ints = struct.unpack('<16I', buf[:64])
floats = struct.unpack('<16f', buf[:64])
print("Ints:", ints[:8])
print("Floats:", [round(x, 2) for x in floats[:8]])
