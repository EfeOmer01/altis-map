import struct

wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"

# Earlier in Cluster 1: start 41867497
# Cluster 2: start 41875801 (diff = 8304 bytes!)
# Cluster 3: start 41884717 (diff = 8916 bytes!)
# Look at the difference: ~8KB!
# In Terrain Builder, cells are 480m x 480m (64 x 64 cells = 4096 cells).
# Let's inspect the header of these cells around 41867000!

with open(wrp_path, 'rb') as f:
    f.seek(41867000)
    buf = f.read(1000)

print("First 256 bytes before 41867497:")
idx = buf.find(b'bridge_01_f.p3d')
print("bridge found at:", idx)
pre = buf[:idx]
print("Preceding 64 bytes hex:", pre[-64:].hex())
ints = struct.unpack(f'<{len(pre[-64:])//4}I', pre[-64:])
print("Preceding ints:", ints)
