import struct

b1 = b'\x00eZE'
b2 = b'N\x06QF'
print("X:", struct.unpack('<f', b1)[0])
print("Y:", struct.unpack('<f', b2)[0])
