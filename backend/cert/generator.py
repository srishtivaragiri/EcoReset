import os
import hmac
import hashlib
import qrcode
from datetime import datetime, timezone
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from verify.verifier import generate_cert_id, generate_signature, store_cert

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "outputs"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

SECRET_KEY = os.environ.get("ECORESET_SECRET", "dev-secret-change-in-production")

def create_certificate(file_hash: str, device_path: str) -> dict:
    cert_id = generate_cert_id()
    signature = generate_signature(cert_id, file_hash)
    store_cert(cert_id, file_hash, signature)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Signed verification URL
    message = f"{cert_id}:{timestamp}".encode()
    hmac_sig = hmac.new(SECRET_KEY.encode(), message, hashlib.sha256).hexdigest()

    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:5173")
    verification_url = f"{frontend_url}/verify/{cert_id}?sig={hmac_sig}&ts={timestamp}"

    # QR code
    qr_filename = f"EcoReset_QR_{cert_id}.png"
    qr_path = os.path.join(OUTPUT_DIR, qr_filename)
    qr = qrcode.make(verification_url)
    qr.save(qr_path)

    # PDF
    pdf_filename = f"EcoReset_Cert_{cert_id}.pdf"
    pdf_path = os.path.join(OUTPUT_DIR, pdf_filename)
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 24)
    c.drawString(100, height - 100, "EcoReset Verification Certificate")
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 150, f"Certificate ID: {cert_id}")
    c.drawString(100, height - 180, f"Timestamp: {timestamp}")
    c.drawString(100, height - 210, f"Device Wiped: {device_path}")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(100, height - 260, "SHA-256 Data Hash:")
    c.setFont("Courier", 10)
    c.drawString(100, height - 275, file_hash)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(100, height - 310, "Digital Signature:")
    c.setFont("Courier", 10)
    c.drawString(100, height - 325, signature)
    c.drawImage(qr_path, 400, height - 240, width=120, height=120)
    c.save()

    return {
        "status": "success",
        "cert_id": cert_id,
        "pdf_url": pdf_path,
        "signature": signature,
        "verification_url": verification_url,
        "qr_image_url": f"/download-qr/{cert_id}"
    }