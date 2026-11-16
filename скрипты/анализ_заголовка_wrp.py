import struct

wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"

with open(wrp_path, 'rb') as f:
    # Read header
    magic = f.read(4)
    version = struct.unpack('<I', f.read(4))[0]
    layer_x = struct.unpack('<I', f.read(4))[0]
    layer_y = struct.unpack('<I', f.read(4))[0]
    print(f"Magic: {magic}, Version: {version}, LayerX: {layer_x}, LayerY: {layer_y}")

    # Let's read some more header ints/floats
    f.seek(16)
    data = struct.unpack('<16I', f.read(64))
    print("Header ints:", data)
