import re
import struct

wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"

print("Scanning AmazingMap.wrp for objects...")
models = set()
count = 0

with open(wrp_path, 'rb') as f:
    data = f.read()

print(f"Read {len(data)} bytes. Finding all .p3d...")
# Search for .p3d
p3d_pattern = re.compile(rb'([a-zA-Z0-9_\\]+\.p3d)\x00', re.IGNORECASE)

matches = []
for m in p3d_pattern.finditer(data):
    matches.append((m.start(), m.group(1).decode('ascii', errors='ignore')))

print(f"Total .p3d occurrences found: {len(matches)}")
unique_models = set(m[1].lower() for m in matches)
print(f"Unique models count: {len(unique_models)}")

# Print 20 sample models
sample_models = list(unique_models)[:30]
for sm in sample_models:
    print(" -", sm)
