import os
import struct

addons_dir = r"E:\SteamLibrary\steamapps\common\Arma 3\Addons"

def read_cstring(f):
    s = b""
    while True:
        c = f.read(1)
        if not c or c == b'\x00': break
        s += c
    return s.decode('ascii', errors='ignore')

def inspect_pbo(pbo_name):
    pbo_path = os.path.join(addons_dir, pbo_name)
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
            f.read(20)
            entries.append(fn)
    print(f"\n{pbo_name}: total entries = {len(entries)}")
    # Count S_ files
    s_files = [e for e in entries if 'S_' in e and '_lco' in e]
    print(f"  S_*_lco files count: {len(s_files)}")
    if s_files:
        print("  Sample:", s_files[:3])
        # Find ranges of x and y
        xs = [int(e.split('_')[1]) for e in s_files if len(e.split('_')) >= 3 and e.split('_')[1].isdigit()]
        ys = [int(e.split('_')[2]) for e in s_files if len(e.split('_')) >= 3 and e.split('_')[2].isdigit()]
        if xs and ys:
            print(f"  X range: {min(xs)} to {max(xs)}, Y range: {min(ys)} to {max(ys)}")

for pbo in [
    "map_altis_data_layers.pbo",
    "map_altis_data_layers_00_00.pbo",
    "map_altis_data_layers_00_01.pbo",
    "map_altis_data_layers_01_00.pbo",
    "map_altis_data_layers_01_01.pbo"
]:
    inspect_pbo(pbo)
