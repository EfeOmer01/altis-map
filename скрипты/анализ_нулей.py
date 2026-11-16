wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"

with open(wrp_path, 'rb') as f:
    f.seek(41867000 + 532)
    chunk = f.read(8836 - 532)

print("Chunk length:", len(chunk))
nonzero = [(i, chunk[i]) for i in range(len(chunk)) if chunk[i] != 0]
print("Non-zero byte count:", len(nonzero))
print("First 20 non-zero positions and values:")
for pos, val in nonzero[:20]:
    print(f"offset {pos}: {val} (0x{val:02x})")
if len(nonzero) > 20:
    print("Last 20 non-zero positions:")
    for pos, val in nonzero[-20:]:
        print(f"offset {pos}: {val} (0x{val:02x})")
