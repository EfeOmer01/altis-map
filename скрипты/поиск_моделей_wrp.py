import re

wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"

with open(wrp_path, 'rb') as f:
    # Read the last 20MB of the file first to see if models table or objects are at the end
    f.seek(0, 2)
    filesize = f.tell()
    print("Filesize:", filesize)
    
    # Check end of file
    f.seek(max(0, filesize - 5000000))
    tail = f.read()
    
    # Find all .p3d occurrences in tail
    p3ds = re.findall(rb'[a-zA-Z0-9_\\/]+(?:\.p3d)', tail, re.IGNORECASE)
    print("Found .p3d in tail:", len(p3ds))
    if p3ds:
        print("Sample p3d in tail:", [p.decode('ascii', errors='ignore') for p in p3ds[:10]])
    else:
        # Check start or scan chunk by chunk
        f.seek(0)
        chunk = f.read(5000000)
        p3ds_start = re.findall(rb'[a-zA-Z0-9_\\/]+(?:\.p3d)', chunk, re.IGNORECASE)
        print("Found .p3d in start:", len(p3ds_start))
        if p3ds_start:
            print("Sample p3d in start:", [p.decode('ascii', errors='ignore') for p in p3ds_start[:10]])
