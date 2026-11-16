import struct
import subprocess
import os

pbo_path = r"E:\SteamLibrary\steamapps\common\Arma 3\Addons\ui_f_data.pbo"
pal2pace = r"C:\Program Files (x86)\Steam\steamapps\common\Arma 3 Tools\TexView2\Pal2PacE.exe"

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
            f.read(20) # dummy header
            break
        packing, orig_sz, res, ts, data_sz = struct.unpack('<5I', f.read(20))
        entries.append((fn, data_sz))
        
    start_of_data = f.tell()
    offset = start_of_data
    for fn, sz in entries:
        if fn.lower() == 'map\\mapcontrol\\fountain_ca.paa':
            f.seek(offset)
            paa_data = f.read(sz)
            print(f"Extracted {fn} at {offset}, size {sz}, magic: {paa_data[:8]}")
            with open(r"C:\temp\fountain_exact.paa", "wb") as pf:
                pf.write(paa_data)
            break
        offset += sz

# Convert with Pal2PacE
subprocess.run([pal2pace, r"C:\temp\fountain_exact.paa", r"C:\temp\loc_Fountain.png"])
print("Converted loc_Fountain.png exists?", os.path.exists(r"C:\temp\loc_Fountain.png"))
if os.path.exists(r"C:\temp\loc_Fountain.png"):
    import shutil
    shutil.copy(r"C:\temp\loc_Fountain.png", r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\веб\иконки\loc_Fountain.png")
    print("Copied to веб/иконки/loc_Fountain.png successfully!")
