import struct
import json
import time

wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"
out_json = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\дома_острова.json"

t0 = time.time()
with open(wrp_path, 'rb') as f:
    f.seek(36694910 + 5)
    buf = f.read(3000000)

pos = 0
buildings = []
b_idx = 1

# Classification helper
def classify_building(cls_lower, model_lower):
    if any(k in cls_lower for k in ['church', 'hospital', 'lighthouse', 'tower', 'barracks']):
        return 'special', 14, 14
    if any(k in cls_lower for k in ['factory', 'hangar', 'terminal', 'warehouse', 'ind_']):
        return 'industrial', 20, 16
    if any(k in cls_lower for k in ['shop', 'fuelstation', 'office']):
        return 'commercial', 12, 10
    if any(k in cls_lower for k in ['shed', 'slum', 'addon']):
        return 'shed', 7, 6
    if any(k in cls_lower for k in ['housebig', 'house_big', 'stone_housebig']):
        return 'house_big', 14, 11
    if any(k in cls_lower for k in ['housesmall', 'house_small', 'stone_housesmall']):
        return 'house_small', 10, 8
    if 'house' in cls_lower or 'stone' in cls_lower:
        return 'house', 11, 9
    return 'structure', 8, 8

while pos < len(buf) - 20:
    end_cls = buf.find(b'\x00', pos)
    if end_cls == -1 or end_cls - pos > 100: break
    try:
        cls = buf[pos:end_cls].decode('ascii')
    except: break
    if not cls or not all(c.isalnum() or c == '_' for c in cls): break
        
    pos = end_cls + 1
    end_model = buf.find(b'\x00', pos)
    if end_model == -1 or end_model - pos > 200: break
    try:
        model = buf[pos:end_model].decode('ascii')
    except: break
    if not model.endswith('.p3d'): break
        
    pos = end_model + 1
    x, z, y = struct.unpack('<3f', buf[pos:pos+12])
    obj_id = struct.unpack('<I', buf[pos+12:pos+16])[0]
    pos += 16
    
    if 0 <= x <= 30720 and 0 <= y <= 30720:
        cls_l = cls.lower()
        mod_l = model.lower()
        if any(k in cls_l or k in mod_l for k in [
            'house', 'shed', 'building', 'stone', 'shop', 'barn', 'garage', 
            'fuelstation', 'factory', 'church', 'hospital', 'barracks', 
            'hangar', 'terminal', 'pier', 'lighthouse', 'tower', 'slum', 'addon'
        ]):
            # Skip pure fences and lamps
            if any(k in cls_l for k in ['fence', 'lamp', 'column', 'wire', 'mirror', 'gate', 'pipe', 'wall']):
                continue
                
            btype, w, h = classify_building(cls_l, mod_l)
            buildings.append({
                "id": f"b_{b_idx}",
                "class": cls,
                "type": btype,
                "x": round(x, 1),
                "y": round(y, 1),
                "w": w,
                "h": h
            })
            b_idx += 1

t1 = time.time()
print(f"Parsed {len(buildings)} real island buildings in {t1 - t0:.2f}s!")

with open(out_json, 'w', encoding='utf-8') as f:
    json.dump(buildings, f, separators=(',', ':'))

print(f"Saved to {out_json} (size: {len(json.dumps(buildings))/1024:.1f} KB)")
