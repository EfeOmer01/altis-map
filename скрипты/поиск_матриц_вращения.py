import struct
import numpy as np

wrp_path = r"C:\Users\efeom\OneDrive\Рабочий стол\1\arma 3 map\am_map\AmazingMap.wrp"

# Search for contiguous sequences of 3x3 rotation matrices
# In a 3x3 rotation matrix around Y:
# [ r00, 0, r02, 0, 1, 0, -r02, 0, r00 ]
# or similar, where r00^2 + r02^2 == 1.0

print("Scanning for rotation matrices in AmazingMap.wrp...")
with open(wrp_path, 'rb') as f:
    # Read in 10MB chunks
    offset = 0
    while True:
        chunk = f.read(10 * 1024 * 1024)
        if not chunk or len(chunk) < 64: break
        
        # Check every 4 bytes
        # Let's search for float 1.0 surrounded by floats between -1.0 and 1.0
        # Fast scan using numpy
        arr = np.frombuffer(chunk, dtype=np.float32)
        # Find places where arr[i] == 1.0 and -1 <= arr[i-1] <= 1 and -1 <= arr[i+1] <= 1
        # and arr[i-1]^2 + arr[i+1]^2 ~ 1.0
        # Specifically: row 1 is [0, 1, 0] in Yaw-only matrix
        # So arr[i-4..i+4] could be a 3x3 matrix
        # Let's check where arr == 1.0
        ones = np.where(arr == 1.0)[0]
        # Filter for valid rotation matrices
        valid_count = 0
        first_valid = None
        for idx in ones:
            if idx >= 4 and idx + 7 < len(arr):
                # Check if arr[idx-4..idx+8] looks like transform
                r00 = arr[idx-4]
                r02 = arr[idx-2]
                r20 = arr[idx+2]
                r22 = arr[idx+4]
                if abs(r00**2 + r02**2 - 1.0) < 0.01 and abs(r20**2 + r22**2 - 1.0) < 0.01:
                    valid_count += 1
                    if first_valid is None:
                        first_valid = idx
                        
        if valid_count > 50:
            abs_pos = offset + first_valid * 4
            print(f"Found {valid_count} rotation matrices in chunk at {offset} (first at {abs_pos}, 0x{abs_pos:x})")
            
        offset += len(chunk)
