import struct
import json
import math
import time

wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"
out_json = r"C:\Users\efeom\.gemini\antigravity\scratch\карта-алтис\данные\дома_острова.json"

# Размеры реальных P3D моделей Arma 3 (Длина x Ширина в метрах)
MODEL_DIMS = {
    # Заводы и большие ангары
    'shed_big': (36, 18),
    'u_shed_ind': (26, 15),
    'i_shed_ind': (24, 14),
    'metal_shed': (14, 8),
    'shed_small': (9, 6),
    'stone_shed': (8, 6),
    'dp_smallfactory': (20, 14),
    'factory_conv': (35, 16),
    
    # Жилые дома
    'house_big_01': (15, 12),
    'house_big_02': (16, 13),
    'house_small_01': (10, 8),
    'house_small_02': (11, 8),
    'stone_housebig': (15, 11),
    'stone_housesmall': (10, 8),
    'slum_house': (10, 8),
    'slum': (9, 7),
    'addon': (8, 6),
    'shop': (14, 10),
    
    # Военные и спецобъекты
    'miloffices': (22, 12),
    'barracks': (18, 10),
    'cargo_tower': (9, 9),
    'cargo_house': (13, 7),
    'cargo_hq': (15, 13),
    'cargo_patrol': (8, 8),
    'garage_v1': (14, 10),
    'garage_v2': (14, 10),
    'fuelstation': (18, 14),
    'hospital': (25, 18),
    'church': (22, 14),
    'lighthouse': (8, 8),
    'reservoirtank': (12, 12),
    'spp_transformer': (8, 6),
    'ttowersmall': (6, 6),
    'helipadsquare': (15, 15),
}

def get_dims(cls_lower, model_lower):
    for key, (length, width) in MODEL_DIMS.items():
        if key in cls_lower or key in model_lower:
            return length, width
    if 'big' in cls_lower or 'big' in model_lower:
        return 15, 11
    if 'small' in cls_lower or 'small' in model_lower:
        return 9, 7
    if 'shed' in cls_lower or 'shed' in model_lower:
        return 8, 6
    return 11, 8

t0 = time.time()
with open(wrp_path, 'rb') as f:
    f.seek(36694910 + 5)
    buf = f.read(3000000)

pos = 0
buildings = []
b_idx = 1

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
    extra = struct.unpack('<I', buf[pos+12:pos+16])[0]
    pos += 16
    
    if 0 <= x <= 30720 and 0 <= y <= 30720:
        cls_l = cls.lower()
        mod_l = model.lower()
        
        # Фильтруем только здания, ангары, склады, жилые дома
        if any(k in cls_l or k in mod_l for k in [
            'house', 'shed', 'building', 'stone', 'shop', 'barn', 'garage', 
            'fuelstation', 'factory', 'church', 'hospital', 'barracks', 
            'hangar', 'terminal', 'pier', 'lighthouse', 'tower', 'slum', 'addon',
            'cargo', 'miloffices', 'reservoirtank'
        ]):
            # Пропускаем заборы, столбы, фонари
            if any(k in cls_l for k in ['fence', 'lamp', 'column', 'wire', 'mirror', 'gate', 'pipe', 'wall']):
                continue
                
            # Извлекаем ТОЧНЫЙ угол поворота из low 16 bits!
            # В Arma 3 getDir идет по часовой стрелке от 0 до 360
            raw_angle = extra & 0xffff
            yaw_deg = round((raw_angle / 65536.0) * 360.0, 1)
            
            length, width = get_dims(cls_l, mod_l)
            
            buildings.append({
                "id": f"b_{b_idx}",
                "class": cls,
                "x": round(x, 1),
                "y": round(y, 1),
                "yaw": yaw_deg,
                "w": width,
                "l": length
            })
            b_idx += 1

t1 = time.time()
print(f"Экспортировано {len(buildings)} точных построек с реальными углами поворота за {t1 - t0:.2f} сек!")

with open(out_json, 'w', encoding='utf-8') as f:
    json.dump(buildings, f, separators=(',', ':'))

print(f"Сохранено в {out_json} (размер: {len(json.dumps(buildings))/1024:.1f} KB)")
