import os

wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"

# Read in 10MB chunks and search for strings
import re

with open(wrp_path, 'rb') as f:
    chunk_idx = 0
    while True:
        pos = f.tell()
        chunk = f.read(10 * 1024 * 1024)
        if not chunk:
            break
        # Find any sequence of 8+ printable ascii chars
        matches = re.findall(rb'[a-zA-Z0-9_\\/.]{8,}', chunk)
        if len(matches) > 10:
            print(f"Chunk at {pos} (size {len(chunk)}): found {len(matches)} strings")
            print("  Samples:", [m.decode('ascii', errors='ignore') for m in matches[:5]])
        chunk_idx += 1
