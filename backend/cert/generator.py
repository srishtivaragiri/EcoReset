import os
import qrcode
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from backend.verify.verifier import generate_cert_id, generate_signature

# Ensure the outputs directory exists
OUTPUT_DIR = "backend/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_certificate(file_hash: str, device_path: str) -> dict:
    """Generates the PDF and returns the metadata for the API."""
    
    cert_id = generate_cert_id()
    signature = generate_signature(cert_id, file_hash)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 1. Generate the QR Code payload
    qr_data = f'{{"cert_id": "{cert_id}", "signature": "{signature}", "file_hash": "{file_hash}"}}'
    qr = qrcode.make(qr_data)
    qr_filename = f"{OUTPUT_DIR}/temp_qr_{cert_id}.png"
    qr.save(qr_filename)

    # 2. Setup PDF Canvas
    pdf_filename = f"{OUTPUT_DIR}/EcoReset_Cert_{cert_id}.pdf"
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    width, height = letter
    
    # 3. Draw Header
    c.setFont("Helvetica-Bold", 24)
    c.drawString(100, height - 100, "EcoReset Verification Certificate")
    
    # 4. Draw Metadata
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 150, f"Certificate ID: {cert_id}")
    c.drawString(100, height - 180, f"Timestamp: {timestamp}")
    c.drawString(100, height - 210, f"Device Wiped: {device_path}")
    
    # 5. Draw Security Hashes
    c.setFont("Helvetica-Bold", 10)
    c.drawString(100, height - 260, "SHA-256 Data Hash:")
    c.setFont("Courier", 10)
    c.drawString(100, height - 275, file_hash)
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(100, height - 310, "Digital Signature:")
    c.setFont("Courier", 10)
    c.drawString(100, height - 325, signature)

    # 6. Embed QR Code & Save
    c.drawImage(qr_filename, 400, height - 240, width=120, height=120)
    c.save()
    
    # 7. Cleanup the temporary QR image
    if os.path.exists(qr_filename):
        os.remove(qr_filename)
        
    return {
        "status": "success",
        "cert_id": cert_id,
        "pdf_url": pdf_filename,
        "signature": signature
    }

# --- TEST BLOCK ---
if __name__ == "__main__":
    print("Testing Certificate Generation...")
    test_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    result = create_certificate(file_hash=test_hash, device_path="D:/USB_Drive")
    print(f"Success! Certificate saved to: {result['pdf_url']}")