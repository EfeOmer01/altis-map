import struct

pbo_path = r"E:\SteamLibrary\steamapps\common\Arma 3\Addons\map_altis.pbo"

def read_cstring(f):
    s = b""
    while True:
        c = f.read(1)
        if not c or c == b'\x00': break
        s += c
    return s.decode('ascii', errors='ignore')

with open(pbo_path, 'rb') as f:
    fname = read_cstring(f)
    f.read(20)
    while True:
        k = read_cstring(f)
        if not k: break
        v = read_cstring(f)
        
    entries = []
    while True:
        fn = read_cstring(f)
        if not fn: break
        packing, orig_sz, res, ts, data_sz = struct.unpack('<5I', f.read(20))
        entries.append((fn, data_sz))
        
    # Calculate offset of Altis.wrp
    header_end = f.tell()
    print("Header ends at:", header_end)
    offset = header_end
    for fn, sz in entries:
        print(f"File {fn} at offset {offset}, size {sz}")
        if fn.lower() == 'altis.wrp':
            altis_offset = offset
            altis_size = sz
        offset += sz

# Inspect Altis.wrp header
with open(pbo_path, 'rb') as f:
    f.seek(altis_offset)
    magic = f.read(4)
    ver = struct.unpack('<I', f.read(4))[0]
    print(f"Altis.wrp magic: {magic}, version: {ver}")
