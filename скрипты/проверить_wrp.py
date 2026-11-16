import sys

wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"
with open(wrp_path, 'rb') as f:
    header = f.read(64)
    print("Header:", header[:16])
    print("Hex:", header[:16].hex())
