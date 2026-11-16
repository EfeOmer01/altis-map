import struct
import os

shp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\data\roads\roads.shp"
dbf_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\data\roads\roads.dbf"

# Read first 5 polylines from roads.shp
with open(shp_path, "rb") as f:
    hdr = f.read(100)
    print("SHP Header len 100. ShapeType:", struct.unpack('<I', hdr[32:36])[0])
    # Bounding box of entire SHP:
    bbox = struct.unpack('<4d', hdr[36:68])
    print(f"SHP Bounding Box: Xmin={bbox[0]:.2f}, Ymin={bbox[1]:.2f}, Xmax={bbox[2]:.2f}, Ymax={bbox[3]:.2f}")
    
    # Let's inspect first 5 records:
    for i in range(5):
        rh = f.read(8)
        if not rh: break
        rnum, rlen = struct.unpack('>II', rh)
        rdata = f.read(rlen * 2)
        stype = struct.unpack('<I', rdata[0:4])[0]
        nparts, npts = struct.unpack('<II', rdata[36:44])
        print(f"Record {i}: stype={stype}, nparts={nparts}, npts={npts}")
        # print first 3 points:
        pts = []
        for p in range(min(5, npts)):
            px, py = struct.unpack('<2d', rdata[44 + nparts*4 + p*16 : 44 + nparts*4 + (p+1)*16])
            pts.append((round(px, 2), round(py, 2)))
        print(f"  Pts: {pts}")
