import struct

wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"

with open(wrp_path, 'rb') as f:
    f.seek(36694910)
    buf = f.read(2048)

# Let's inspect carefully
pos = 5 # start of Land_lighthouse_small_f
for i in range(10):
    # read classname (null-terminated)
    end_cls = buf.find(b'\x00', pos)
    cls = buf[pos:end_cls].decode('ascii', errors='ignore')
    
    # read model (null-terminated)
    pos = end_cls + 1
    end_model = buf.find(b'\x00', pos)
    model = buf[pos:end_model].decode('ascii', errors='ignore')
    
    pos = end_model + 1
    # Let's read next 32 bytes and see
    chunk = buf[pos:pos+32]
    # Unpack floats
    x, z, y = struct.unpack('<3f', chunk[:12])
    extra = chunk[12:16]
    extra_int = struct.unpack('<I', extra)[0]
    extra_float = struct.unpack('<f', extra)[0]
    
    print(f"[{i}] Pos: {pos-len(cls)-len(model)-2:06d}")
    print(f"  Class: {cls}")
    print(f"  Model: {model}")
    print(f"  X: {x:.2f}, Z: {z:.2f}, Y: {y:.2f}, Extra: {extra.hex()} (int: {extra_int}, float: {extra_float})")
    
    # Let's see what follows extra: does the next classname start at pos+16 or pos+?
    # Check if pos+16 is printable ASCII (start of next classname)
    next_byte = buf[pos+16]
    print(f"  Byte at +16: 0x{next_byte:02x} ('{chr(next_byte) if 32 <= next_byte < 127 else '?'}')")
    pos = pos + 16
