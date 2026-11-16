import struct
import math

# Let's inspect all 58 objects in Factory02
from поиск_объектов_фабрики import found_objects

print("Analyzing extras of Factory02 objects:")
for obj in found_objects[:20]:
    extra = obj[5]
    # Unpack 4 bytes
    b0 = extra & 0xff
    b1 = (extra >> 8) & 0xff
    b2 = (extra >> 16) & 0xff
    b3 = (extra >> 24) & 0xff
    
    # Try signed int16
    s_low = struct.unpack('<h', struct.pack('<H', extra & 0xffff))[0]
    s_high = struct.unpack('<h', struct.pack('<H', extra >> 16))[0]
    
    # Angle possibilities
    deg_from_b0 = (b0 / 256.0) * 360.0
    deg_from_b1 = (b1 / 256.0) * 360.0
    deg_from_b2 = (b2 / 256.0) * 360.0
    deg_from_b3 = (b3 / 256.0) * 360.0
    deg_from_low16 = ((extra & 0xffff) / 65536.0) * 360.0
    
    print(f"{obj[0][:20]:<20} extra=0x{extra:08x} -> bytes=({b0:02x}, {b1:02x}, {b2:02x}, {b3:02x}) deg_low16={deg_from_low16:.1f}°")
