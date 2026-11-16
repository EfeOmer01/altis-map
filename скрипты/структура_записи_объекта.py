wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"

with open(wrp_path, 'rb') as f:
    f.seek(36694910)
    buf = f.read(500)

# Let's inspect object 0 and object 1
idx0 = buf.find(b'Land_lighthouse_small_f')
idx1 = buf.find(b'Land_slum_house01_f')

print(f"Object 0 starts at {idx0}, Object 1 starts at {idx1}, diff = {idx1 - idx0}")
rec0 = buf[idx0:idx1]
print("Rec 0 len:", len(rec0))
print("Rec 0 hex:", rec0.hex())
