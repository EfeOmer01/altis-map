import struct

wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"

with open(wrp_path, 'rb') as f:
    f.seek(36694910)
    buf = f.read(2048)

# Let's inspect objects
pos = 0
for count in range(10):
    # Find next classname or p3d
    p3d_idx = buf.find(b'.p3d\x00', pos)
    if p3d_idx == -1: break
    
    # Backtrack to start of classname / string
    prev_zero = buf.rfind(b'\x00', 0, p3d_idx)
    # The string between prev_zero and p3d_idx is p3d path
    p3d_path = buf[prev_zero+1:p3d_idx+4].decode('ascii', errors='ignore')
    
    # What's before prev_zero?
    prev_prev_zero = buf.rfind(b'\x00', 0, prev_zero)
    classname = buf[prev_prev_zero+1:prev_zero].decode('ascii', errors='ignore')
    
    # After p3d_idx+5:
    data_after = buf[p3d_idx+5:p3d_idx+5+64]
    floats = struct.unpack('<16f', data_after)
    print(f"\nObject {count}:")
    print(f"  Class: {classname}")
    print(f"  Model: {p3d_path}")
    print(f"  Floats after: {[round(x, 2) for x in floats[:8]]}")
    
    pos = p3d_idx + 5 + 32 # jump forward
