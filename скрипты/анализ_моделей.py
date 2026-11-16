import struct

wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"

with open(wrp_path, 'rb') as f:
    f.seek(40000000)
    data = f.read(5000000)
    # Find the first .p3d
    idx = data.find(b'.p3d')
    print("Found .p3d at rel offset:", idx, "absolute:", 40000000 + idx)
    
    # Let's inspect 500 bytes before that first .p3d
    start = max(0, idx - 500)
    snippet = data[start:idx+100]
    print("Snippet around first p3d:")
    print(snippet)
