wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"

with open(wrp_path, 'rb') as f:
    f.seek(41867000)
    buf = f.read(200000)

offsets = []
pos = 0
while len(offsets) < 20:
    idx = buf.find(b'.p3d', pos)
    if idx == -1:
        break
    offsets.append(idx)
    pos = idx + 4

print("Found offsets:", offsets)
for i in range(len(offsets) - 1):
    print(f"Diff {i}->{i+1}: {offsets[i+1] - offsets[i]}")
