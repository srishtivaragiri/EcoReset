import hashlib
import uuid

SERVER_SECRET = "eco_reset_super_secret_key_2026"

def generate_cert_id() -> str:
    """Generates a unique ID for the certificate."""
    return str(uuid.uuid4())

def generate_signature(cert_id: str, file_hash: str) -> str:
    """Creates a tamper-proof signature using the server secret."""
    payload = f"{SERVER_SECRET}{cert_id}{file_hash}".encode('utf-8')
    return hashlib.sha256(payload).hexdigest()

def verify_signature(cert_id: str, file_hash: str, provided_signature: str) -> bool:
    """Re-hashes the data to verify it hasn't been tampered with."""
    expected_signature = generate_signature(cert_id, file_hash)
    return expected_signature == provided_signature
# --- TEST BLOCK ---
# This allows you to test the cryptography without running the web server.
if __name__ == "__main__":
    print("🛡️ Testing Verification Engine...")
    
    # Fake data from a "wiped" device
    test_cert_id = "12345-abcde"
    test_file_hash = "real_data_hash_123"
    
    # 1. Generate a valid signature
    valid_sig = generate_signature(test_cert_id, test_file_hash)
    print(f"\n[+] Generated Valid Signature:\n    {valid_sig}")
    
    # 2. Test the Valid Case (Normal User)
    print("\n[?] Simulating normal user verifying a valid certificate...")
    is_valid = verify_signature(test_cert_id, test_file_hash, valid_sig)
    print(f"    Result: {'✅ VERIFIED' if is_valid else '❌ FAILED'}")
    
    # 3. Test the Tampered Case (Hacker)
    print("\n[?] Simulating hacker changing the PDF to say they wiped a different drive...")
    tampered_hash = "fake_hacked_hash_999"
    is_tampered_valid = verify_signature(test_cert_id, tampered_hash, valid_sig)
    print(f"    Result: {'🚨 TAMPERING CAUGHT' if not is_tampered_valid else '❌ SECURITY FAILED'}")