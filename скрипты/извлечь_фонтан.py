import struct
from PIL import Image
import os
import sys

# Import PAA reader from previous scripts or write lightweight PAA extractor
pbo_path = r"E:\SteamLibrary\steamapps\common\Arma 3\Addons\ui_f_data.pbo"

def read_cstring(f):
    s = b""
    while True:
        c = f.read(1)
        if not c or c == b'\x00': break
        s += c
    return s.decode('ascii', errors='ignore')

paa_data = None
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
        entries.append((fn, data_sz))
        
    header_end = f.tell() + 21 # empty entry
    offset = header_end
    for fn, sz in entries:
        if fn.lower() == 'map\\mapcontrol\\fountain_ca.paa':
            f.seek(offset)
            paa_data = f.read(sz)
            print(f"Found fountain_CA.paa at {offset}, size {sz}")
            break
        offset += sz

if paa_data:
    raw_paa_path = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\fountain_CA.paa"
    with open(raw_paa_path, 'wb') as f:
        f.write(paa_data)
    print("Saved raw PAA to", raw_paa_path)
