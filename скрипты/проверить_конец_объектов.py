wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"

with open(wrp_path, 'rb') as f:
    f.seek(36694910 + 5)
    buf = f.read(15000000)

pos = 0
for i in range(21322):
    end_cls = buf.find(b'\x00', pos)
    pos = end_cls + 1
    end_model = buf.find(b'\x00', pos)
    pos = end_model + 1 + 16

print("Ended at offset in buf:", pos)
print("Bytes after break:")
after = buf[pos:pos+64]
print("Hex:", after.hex())
print("ASCII:", "".join(chr(b) if 32 <= b < 127 else "." for b in after))
