import os

pbo_path = r"E:\SteamLibrary\steamapps\common\Arma 3\Addons\map_altis.pbo"

def read_cstring(f):
    s = b""
    while True:
        c = f.read(1)
        if not c or c == b'\x00': break
        s += c
    return s.decode('ascii', errors='ignore')

with open(pbo_path, 'rb') as f:
    # First entry
    fname = read_cstring(f)
    print("First entry fname:", fname)
    # Read headers
    entries = []
    while True:
        fn = read_cstring(f)
        if not fn: break
        # read packing method (4), orig size (4), reserved (4), timestamp (4), data size (4)
        header_data = f.read(20)
        if len(header_data) < 20: break
        # unpack sizes
        import struct
        packing, orig_sz, res, ts, data_sz = struct.unpack('<5I', header_data)
        entries.append((fn, data_sz, orig_sz, packing))

print(f"Total entries in map_altis.pbo: {len(entries)}")
for fn, dsz, osz, p in entries:
    print(f"  {fn}: size {dsz} (orig {osz}, packing {p})")
