import struct

pbo_path = r"E:\SteamLibrary\steamapps\common\Arma 3\Addons\ui_f_data.pbo"

def read_cstring(f):
    s = b""
    while True:
        c = f.read(1)
        if not c or c == b'\x00': break
        s += c
    return s.decode('ascii', errors='ignore')

with open(pbo_path, 'rb') as f:
    read_cstring(f)
    f.read(20)
    while True:
        k = read_cstring(f)
        if not k: break
        read_cstring(f)
        
    entries = []
    while True:
        fn = read_cstring(f)
        if not fn:
            # Check what's here
            dummy_header = f.read(20)
            print(f"End of headers reached at {f.tell()}! Dummy header: {dummy_header.hex()}")
            break
        packing, orig_sz, res, ts, data_sz = struct.unpack('<5I', f.read(20))
        entries.append((fn, data_sz))
        
    start_of_data = f.tell()
    print("Start of file data is exactly at:", start_of_data)
