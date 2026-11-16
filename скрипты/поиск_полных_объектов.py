import struct
import re
import math

wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"

# Search for the pattern:
# .p3d\x00 followed by 12 floats where:
# - r00^2 + r02^2 ~ 1.0 (rotation matrix)
# - 0 <= X <= 30720 and 0 <= Y <= 30720
# And 24 bytes before .p3d\x00 contains bounding box: 6 floats!

print("Scanning for full-transform objects across entire AmazingMap.wrp...")
with open(wrp_path, 'rb') as f:
    data = f.read()

p3d_pattern = re.compile(rb'([a-zA-Z0-9_\\]+\.p3d)\x00', re.IGNORECASE)

records = []
for m in p3d_pattern.finditer(data):
    p3d_end = m.end()
    p3d_start = m.start()
    model = m.group(1).decode('ascii', errors='ignore')
    
    # Check 12 floats after .p3d\x00
    if p3d_end + 48 > len(data): continue
    floats_after = struct.unpack('<12f', data[p3d_end : p3d_end + 48])
    r00, r01, r02 = floats_after[0:3]
    r10, r11, r12 = floats_after[3:6]
    r20, r21, r22 = floats_after[6:9]
    x, z, y = floats_after[9:12]
    
    # Check if this is a valid transform
    if 0 <= x <= 30720 and 0 <= y <= 30720:
        norm1 = r00**2 + r01**2 + r02**2
        norm2 = r20**2 + r21**2 + r22**2
        if 0.95 <= norm1 <= 1.05 and 0.95 <= norm2 <= 1.05:
            # We found a full transform object!
            # Check bounding box before p3d_start
            bbox = None
            if p3d_start >= 28:
                try:
                    b_floats = struct.unpack('<6f', data[p3d_start - 24 : p3d_start])
                    # Check if b_floats are reasonable bounding box coords
                    min_x, min_z, min_y, max_x, max_z, max_y = b_floats
                    if min_x <= max_x and min_y <= max_y:
                        bbox = (min_x, min_y, max_x, max_y)
                except: pass
                
            yaw = math.degrees(math.atan2(r20, r00))
            records.append({
                "model": model,
                "x": round(x, 1),
                "y": round(y, 1),
                "z": round(z, 1),
                "yaw": round(yaw, 1),
                "bbox": bbox,
                "offset": p3d_start
            })

print(f"Total full-transform objects found: {len(records)}!")
print("Sample full-transform objects:")
for r in records[:15]:
    print(f"  {r['model']} at ({r['x']}, {r['y']}), yaw={r['yaw']}°, bbox={r['bbox']}")
