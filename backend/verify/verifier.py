import hashlib
import uuid
import hmac
import os

# --- Constants ---
# Secret for the internal PDF signature (Legacy/Backup check)
SERVER_SECRET = "eco_reset_super_secret_key_2026"

# Secret for the QR Code URL parameters (Must match generator.py & main.py)
SECRET_KEY = os.environ.get("ECORESET_SECRET", "dev-secret-change-in-production")

# --- In-memory store of issued certificates ---
cert_store = {}

# ==========================================
# 1. CORE CERTIFICATE GENERATION & STORAGE
# ==========================================

def generate_cert_id() -> str:
    """Generates a unique ID for the certificate."""
    return str(uuid.uuid4())

def generate_signature(cert_id: str, file_hash: str) -> str:
    """Creates a tamper-proof signature for the PDF using the server secret."""
    payload = f"{SERVER_SECRET}{cert_id}{file_hash}".encode('utf-8')
    return hashlib.sha256(payload).hexdigest()

def store_cert(cert_id: str, file_hash: str, signature: str):
    """Save issued cert so the verification endpoints can check it later."""
    cert_store[cert_id] = {
        "file_hash": file_hash,
        "signature": signature
    }

# ==========================================
# 2. PDF MANUAL VERIFICATION (Text-Based)
# ==========================================

def verify_signature(cert_id: str, file_hash: str, provided_signature: str) -> bool:
    """Re-hashes the data to verify it hasn't been tampered with."""
    expected_signature = generate_signature(cert_id, file_hash)
    return expected_signature == provided_signature

def verify_cert(cert_id: str, file_hash: str) -> str:
    """Returns 'VERIFIED' or 'TAMPERED'. Used if someone manually types the PDF data."""
    record = cert_store.get(cert_id)
    if not record:
        return "TAMPERED"
    is_valid = verify_signature(cert_id, file_hash, record["signature"])
    return "VERIFIED" if is_valid else "TAMPERED"

# ==========================================
# 3. QR CODE SCAN VERIFICATION (URL-Based)
# ==========================================

def check_qr_scan(cert_id: str, provided_sig: str, timestamp: str) -> dict:
    """Evaluates the QR scan URL parameters and returns the 3-point check for the UI."""
    
    # Check 1: TAMPER PROOF (Did a hacker alter the URL parameters?)
    expected_message = f"{cert_id}:{timestamp}".encode()
    expected_sig = hmac.new(SECRET_KEY.encode(), expected_message, hashlib.sha256).hexdigest()
    
    # We use hmac.compare_digest to prevent timing attacks
    if not hmac.compare_digest(expected_sig, provided_sig):
        return {
            "is_verified": False,
            "is_tamper_proof": False, # Failed!
            "ok_for_resale": False,
            "message": "🚨 Security Alert: URL Signature Tampered!"
        }

    # Check 2: VERIFICATION (Does this ID actually exist in our database/memory?)
    record = cert_store.get(cert_id)
    if not record:
        return {
            "is_verified": False, # Failed!
            "is_tamper_proof": True,  # URL is mathematically valid, but ID is fake
            "ok_for_resale": False,
            "message": "❌ Certificate Not Found in EcoReset Database."
        }

    # Check 3: DEVICE OK FOR RESALE (Passed both security checks)
    return {
        "is_verified": True,
        "is_tamper_proof": True,
        "ok_for_resale": True,
        "device_hash": record.get("file_hash"),
        "wiped_at": timestamp,
        "message": "✅ Authentic Certificate. Device is safe for resale or recycling."
    }

# ==========================================
# TEST BLOCK
# ==========================================
if __name__ == "__main__":
    print("🛡️ Testing Verification Engine...")
    test_cert_id = "12345-abcde"
    test_file_hash = "real_data_hash_123"

    valid_sig = generate_signature(test_cert_id, test_file_hash)
    print(f"\n[+] Generated Valid Signature:\n    {valid_sig}")

    print("\n[?] Simulating normal user verifying a valid certificate...")
    is_valid = verify_signature(test_cert_id, test_file_hash, valid_sig)
    print(f"    Result: {'✅ VERIFIED' if is_valid else '❌ FAILED'}")

    print("\n[?] Simulating hacker tampering...")
    tampered_hash = "fake_hacked_hash_999"
    is_tampered_valid = verify_signature(test_cert_id, tampered_hash, valid_sig)
    print(f"    Result: {'🚨 TAMPERING CAUGHT' if not is_tampered_valid else '❌ SECURITY FAILED'}")