import struct

# Sample extras from Factory02:
extras = [
    0xc3ecfaad, 0xc4ccfedb, 0xc3cd0342, 0xc46d020b, 0xc48d01ad, 
    0xc42d0a18, 0xc48d09ae, 0xc50d0f0a, 0xc42d12d5, 0xc46d122a
]

for val in extras:
    b0 = val & 0xff
    b1 = (val >> 8) & 0xff
    b2 = (val >> 16) & 0xff
    b3 = (val >> 24) & 0xff
    low16 = val & 0xffff
    high16 = val >> 16
    print(f"0x{val:08x}: high16={high16} (0x{high16:04x}), low16={low16} (0x{low16:04x}), bytes=({b3:02x}, {b2:02x}, {b1:02x}, {b0:02x})")
