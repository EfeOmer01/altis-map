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
        
    while True:
        fn = read_cstring(f)
        if not fn: break
        packing, orig_sz, res, ts, data_sz = struct.unpack('<5I', f.read(20))
        print(f"File {fn}: packing={hex(packing)}, orig_sz={orig_sz}, data_sz={data_sz}")
