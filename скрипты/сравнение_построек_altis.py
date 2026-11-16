import struct
import re

pbo_path = r"E:\SteamLibrary\steamapps\common\Arma 3\Addons\map_altis.pbo"

with open(pbo_path, 'rb') as f:
    f.seek(154)
    # Search for model table
    # Find first .p3d
    chunk = f.read(50000000)
    idx = chunk.find(b'a3\\rocks_f\\sharp\\sharpstone_01_lc.p3d')
    print("Found model table at rel offset:", idx)
    
    # Let's search for Land_lighthouse_small_f
    l_idx = chunk.find(b'Land_lighthouse_small_f\x00')
    print("Found first object at rel offset:", l_idx)
    
    # Parse objects from Altis.wrp
    pos = l_idx
    objects = []
    while pos < len(chunk) - 20:
        end_cls = chunk.find(b'\x00', pos)
        if end_cls == -1 or end_cls - pos > 100: break
        try:
            cls = chunk[pos:end_cls].decode('ascii')
        except: break
        if not cls or not all(c.isalnum() or c == '_' for c in cls): break
            
        pos = end_cls + 1
        end_model = chunk.find(b'\x00', pos)
        if end_model == -1 or end_model - pos > 200: break
        try:
            model = chunk[pos:end_model].decode('ascii')
        except: break
        if not model.endswith('.p3d'): break
            
        pos = end_model + 1
        x, z, y = struct.unpack('<3f', chunk[pos:pos+12])
        pos += 16
        
        if 0 <= x <= 30720 and 0 <= y <= 30720:
            objects.append((cls, model, x, y, z))

print(f"Altis.wrp parsed {len(objects)} objects!")
houses = [obj for obj in objects if any(k in obj[0].lower() or k in obj[1].lower() for k in ['house', 'shed', 'building', 'stone', 'shop', 'barn', 'garage', 'fuelstation', 'factory', 'church', 'hospital', 'barracks', 'hangar', 'terminal', 'pier', 'lighthouse', 'tower', 'slum', 'addon'])]
print(f"Altis.wrp structures: {len(houses)}")
