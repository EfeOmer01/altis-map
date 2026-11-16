import struct

wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"

with open(wrp_path, 'rb') as f:
    f.seek(41867000 + 532)
    s = f.read(150)
    print("At 532:", s)
    f.seek(41867000 + 8836 - 50)
    s2 = f.read(150)
    print("At 8836:", s2)
