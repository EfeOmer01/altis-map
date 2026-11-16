import struct

pbo_path = r"E:\SteamLibrary\steamapps\common\Arma 3\Addons\map_altis.pbo"

with open(pbo_path, 'rb') as f:
    f.seek(155)
    magic = f.read(4)
    ver = struct.unpack('<I', f.read(4))[0]
    print("Offset 155 magic:", magic, "ver:", ver)
    
    # If not at 155, search for 'OPRW' in first 2000 bytes
    if magic != b'OPRW':
        f.seek(0)
        buf = f.read(2048)
        idx = buf.find(b'OPRW')
        print(f"Found OPRW at offset {idx}")
