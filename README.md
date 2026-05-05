# ♻️ EcoReset - Secure Device Sanitization & Verification Engine

**EcoReset** is a robust, forensic-grade backend system designed to manage secure hardware data wiping, generate verifiable certificates of destruction, and provide a cryptographically secure verification portal for device resale.

Built for the 2026 Hackathon, this backend utilizes a "Thin QR" architecture to bridge physical hardware wiping with instant, tamper-proof digital verification.

## ✨ Key Features

* **Secure Wipe Management:** Initiates and tracks background wiping processes for target drives.
* **Dynamic PDF Generation:** On-the-fly generation of professional Certificate of Destruction PDFs using `reportlab`.
* **"Thin QR" Cryptography:** Generates QR codes embedded with HMAC-SHA256 signed verification URLs, preventing tampering and "Fat QR" data limitations.
* **3-Point Verification Protocol:** A dedicated API endpoint that confirms:
  1. Cryptographic integrity of the URL parameters (Tamper-Proof Check).
  2. Existence of the Certificate ID in the secure database.
  3. Safety status for device resale or recycling.
* **Interactive API Documentation:** Auto-generated Swagger UI for easy endpoint testing.

## 🛠️ Technology Stack

* **Framework:** Python 3 + FastAPI
* **Server:** Uvicorn
* **Cryptography:** `hashlib` (SHA-256), `hmac`, `uuid`
* **Document Generation:** `reportlab`, `qrcode`, `Pillow`
* **Architecture:** Modular REST API

## 📂 Project Structure

```text
backend/
├── main.py                 # FastAPI application hub & routing
├── cert/
│   └── generator.py        # PDF canvas and Signed QR Code generation
├── verify/
│   └── verifier.py         # HMAC signatures and 3-Point verification logic
├── wipe/
│   └── engine.py           # Secure wiping task simulation
├── outputs/                # Directory for generated .pdf and .png files
└── requirements.txt        # Project dependencies
