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
    # First entry (dummy / prefix)
    fname = read_cstring(f)
    packing, orig_sz, res, ts, data_sz = struct.unpack('<5I', f.read(20))
    if packing == 0x56657273: # "sreV"
        # Read key-value pairs until empty key
        props = {}
        while True:
            k = read_cstring(f)
            if not k: break
            v = read_cstring(f)
            props[k] = v
        print("PBO Properties:", props)
        
    # Now read real entries
    entries = []
    while True:
        fn = read_cstring(f)
        if not fn: break
        packing, orig_sz, res, ts, data_sz = struct.unpack('<5I', f.read(20))
        entries.append((fn, data_sz, orig_sz, packing))

print(f"Total entries in map_altis.pbo: {len(entries)}")
for fn, dsz, osz, p in entries:
    print(f"  {fn}: size {dsz} bytes")
