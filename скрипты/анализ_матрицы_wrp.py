import struct
import math

wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"

# Let's inspect around 41867532
with open(wrp_path, 'rb') as f:
    f.seek(41867497)
    # Read 500 bytes
    buf = f.read(500)

print("First 200 bytes around 41867497:")
idx = buf.find(b'.p3d\x00')
print("Model found at:", idx)
model = buf[:idx+4].decode('ascii', errors='ignore')
print("Model:", model)

after = buf[idx+5:idx+5+64]
# Unpack 12 floats (3x3 rotation matrix + 3 position coordinates)
m = struct.unpack('<12f', after[:48])
print("\nTransform matrix (12 floats):")
print(f"  R0: {m[0]:.4f}, {m[1]:.4f}, {m[2]:.4f}")
print(f"  R1: {m[3]:.4f}, {m[4]:.4f}, {m[5]:.4f}")
print(f"  R2: {m[6]:.4f}, {m[7]:.4f}, {m[8]:.4f}")
print(f"  Pos: X={m[9]:.2f}, Z={m[10]:.2f}, Y={m[11]:.2f}")

yaw_rad = math.atan2(m[6], m[0])
yaw_deg = math.degrees(yaw_rad)
print(f"Calculated Yaw: {yaw_deg:.1f} degrees!")
