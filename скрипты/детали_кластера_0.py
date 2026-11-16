import struct
import re

wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"

with open(wrp_path, 'rb') as f:
    f.seek(36652600)
    data = f.read(5000)

print("First 1000 bytes of cluster 0:")
pos = 0
for i in range(10):
    idx = data.find(b'.p3d', pos)
    if idx == -1: break
    start = data.rfind(b'\x00', 0, idx) + 1
    model = data[start:idx+4].decode('ascii', errors='ignore')
    # Let's see what is before and after
    print(f"[{i}] offset {start}: {model}")
    pos = idx + 4
