wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"

with open(wrp_path, 'rb') as f:
    f.seek(36652646)
    # Read until we hit non-string data
    pos = 36652646
    models = []
    while True:
        line = b""
        ch = f.read(1)
        if not ch: break
        while ch != b'\x00':
            line += ch
            ch = f.read(1)
            if len(line) > 500: break
        if not line or not line.endswith(b'.p3d'):
            print(f"End of model string table at {f.tell()}, last read: {line[:50]}")
            break
        models.append(line.decode('ascii', errors='ignore'))

print(f"Total models in table: {len(models)}")
print("First 5:", models[:5])
print("Last 5:", models[-5:])
