import struct

wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"

# Look around 154036151
# Earlier snippet at 154036151:
# Hex: b40b00d0d22d4647069646020000006eb40b00c0772d46c51896460200000070
# Notice that d0d22d46 is at 154036151 + 3 = 154036154!
target = 154036154
print("Offset mod 16:", target % 16)

with open(wrp_path, 'rb') as f:
    f.seek(target)
    for i in range(5):
        rec = f.read(16)
        x, y = struct.unpack('<2f', rec[:8])
        mid, oid = struct.unpack('<2I', rec[8:16])
        print(f"rec {i}: X={x:.1f}, Y={y:.1f}, mid={mid}, oid={oid}")
