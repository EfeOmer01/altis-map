import struct

shp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\data\roads\roads.shp"
prj_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\data\roads\roads.prj"

with open(prj_path, "r", encoding="latin1") as f:
    print("PRJ:", f.read())

with open(shp_path, "rb") as f:
    hdr = f.read(100)
    file_len, = struct.unpack('>I', hdr[24:28])
    file_bytes = file_len * 2
    xmin, ymin, xmax, ymax = struct.unpack('<4d', hdr[36:68])
    print(f"SHP Bounding Box: X=[{xmin}, {xmax}], Y=[{ymin}, {ymax}]")
    print(f"X span = {xmax - xmin}, Y span = {ymax - ymin}")

    # Let's read first 10 polylines
    for i in range(10):
        if f.tell() >= file_bytes: break
        rec_hdr = f.read(8)
        rec_num, rec_len = struct.unpack('>II', rec_hdr)
        rec_data = f.read(rec_len * 2)
        stype, = struct.unpack('<I', rec_data[0:4])
        if stype == 3:
            box = struct.unpack('<4d', rec_data[4:36])
            num_parts, num_pts = struct.unpack('<II', rec_data[36:44])
            px1, py1 = struct.unpack('<2d', rec_data[44+num_parts*4 : 44+num_parts*4+16])
            print(f"Rec {rec_num}: box X=[{box[0]:.1f}, {box[2]:.1f}], Y=[{box[1]:.1f}, {box[3]:.1f}], first pt=({px1:.1f}, {py1:.1f})")
