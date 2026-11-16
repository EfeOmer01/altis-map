import struct

wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"

with open(wrp_path, 'rb') as f:
    data = f.read()

import re
p3d_pattern = re.compile(rb'([a-zA-Z0-9_\\]+\.p3d)\x00', re.IGNORECASE)

matches = list(p3d_pattern.finditer(data))

for i in [0, 1, 2, 5, 10, 50, 100]:
    if i >= len(matches): break
    m = matches[i]
    model_name = m.group(1).decode('ascii', errors='ignore')
    after_pos = m.end()
    # Read next 64 bytes
    after_bytes = data[after_pos:after_pos+64]
    # Unpack floats
    floats = struct.unpack('<16f', after_bytes)
    print(f"\n--- Match {i} at {m.start()}: {model_name} ---")
    print("Floats:", [round(x, 2) for x in floats])
