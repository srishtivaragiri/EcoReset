from PIL import Image
from pyzbar.pyzbar import decode

# Install pyzbar if needed: pip install pyzbar
import sys, os

if len(sys.argv) < 2:
    print("Usage: python test_qr.py <path_to_qr_image>")
    sys.exit(1)

qr_path = sys.argv[1]
if not os.path.exists(qr_path):
    print("File not found:", qr_path)
    sys.exit(1)

img = Image.open(qr_path)
decoded = decode(img)
if decoded:
    data = decoded[0].data.decode('utf-8')
    print("QR Content:", data)
    if data.startswith("http"):
        print("SUCCESS: QR contains a URL.")
    elif data.startswith("{"):
        print("ERROR: QR contains JSON – old code is still being used.")
    else:
        print("UNEXPECTED content.")
else:
    print("No QR code found in image.")