import struct
import re

wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"

with open(wrp_path, 'rb') as f:
    data = f.read()

p3d_pattern = re.compile(rb'([a-zA-Z0-9_\\]+\.p3d)\x00', re.IGNORECASE)
matches = list(p3d_pattern.finditer(data))

# Group matches by gaps
clusters = []
current_cluster = [matches[0]]

for m in matches[1:]:
    gap = m.start() - current_cluster[-1].end()
    if gap > 200: # gap larger than 200 bytes
        clusters.append(current_cluster)
        current_cluster = [m]
    else:
        current_cluster.append(m)
clusters.append(current_cluster)

print(f"Total clusters: {len(clusters)}")
for idx, cl in enumerate(clusters[:10]):
    print(f"Cluster {idx}: start {cl[0].start()}, count {len(cl)}, sample: {cl[0].group(1).decode('ascii', errors='ignore')}")
