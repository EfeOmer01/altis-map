import struct

wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"

with open(wrp_path, 'rb') as f:
    f.seek(36694910 + 5)
    buf = f.read(4096)

# Look at Object 0
pos = 0
for i in range(5):
    end_cls = buf.find(b'\x00', pos)
    cls = buf[pos:end_cls].decode('ascii')
    pos = end_cls + 1
    end_model = buf.find(b'\x00', pos)
    model = buf[pos:end_model].decode('ascii')
    pos = end_model + 1
    
    # Let's inspect 64 bytes following the model path
    data = buf[pos:pos+64]
    floats = struct.unpack('<16f', data)
    ints = struct.unpack('<16I', data)
    
    print(f"\nObject {i}: {cls} ({model})")
    print("Floats:", [f"{x:.4f}" for x in floats[:8]])
    print("Ints:", [f"{x} (0x{x:08x})" for x in ints[:8]])
    
    pos += 16
