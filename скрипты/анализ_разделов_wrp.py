import struct

wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"

with open(wrp_path, 'rb') as f:
    f.seek(36694910 + 5 + 1997876) # ~38.69 MB
    while True:
        pos = f.tell()
        head = f.read(64)
        if not head: break
        # Check if there is magic or header
        magic = head[:4]
        # Check if there are readable strings or ints
        print(f"At {pos} (0x{pos:x}):")
        print("  Hex:", head[:32].hex())
        print("  ASCII:", "".join(chr(b) if 32 <= b < 127 else "." for b in head[:32]))
        
        # Let's skip forward by 10MB or search for next string
        f.seek(pos + 10 * 1024 * 1024)
        if pos > 155000000: break
