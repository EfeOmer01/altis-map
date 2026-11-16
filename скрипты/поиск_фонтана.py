import struct

def search_pbo(pbo_path, query):
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
            if not fn: break
            packing, orig_sz, res, ts, data_sz = struct.unpack('<5I', f.read(20))
            if query.lower() in fn.lower():
                entries.append((fn, data_sz))
        return entries

for pbo in [r"E:\SteamLibrary\steamapps\common\Arma 3\Addons\ui_f.pbo", r"E:\SteamLibrary\steamapps\common\Arma 3\Addons\ui_f_data.pbo"]:
    matches = search_pbo(pbo, "fountain")
    if matches:
        print(f"Found in {pbo}:", matches)
