from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uuid
import os
import hmac
import hashlib
from wipe.engine import secure_wipe_task

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

jobs = {}

# Load the secret key for HMAC (same as in cert/generator.py)
SECRET_KEY = os.environ.get("ECORESET_SECRET", "dev-secret-change-in-production")


@app.get("/")
def home():
    return {"status": "EcoReset API is Running"}


@app.post("/wipe")
async def start_wipe(data: dict, background_tasks: BackgroundTasks):
    # FIXED: Changed "path" to "device_path" to match what the UI sends
    target_path = data.get("path") 
    
    if not target_path or not os.path.exists(target_path):
        raise HTTPException(status_code=400, detail="Invalid path")
        
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "starting", "progress": 0}
    background_tasks.add_task(secure_wipe_task, job_id, target_path, jobs)
    return {"job_id": job_id}


@app.get("/status/{job_id}")
async def get_status(job_id: str):
    return jobs.get(job_id, {"status": "not_found"})


@app.post("/generate-cert")
async def api_generate_cert(data: dict):
    job_id = data.get("job_id")
    device_path = data.get("device_path", "Unknown Device")

    if not job_id or job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    if job.get("status") not in ("completed", "completed_with_errors"):
        raise HTTPException(status_code=400, detail="Wipe not complete yet")

    all_hashes = job.get("hashes", {})
    combined = "".join(sorted(all_hashes.values()))
    master_hash = hashlib.sha256(combined.encode()).hexdigest()

    from cert.generator import create_certificate
    result = create_certificate(file_hash=master_hash, device_path=device_path)
    return result


@app.post("/verify")
async def api_verify_cert(data: dict):
    cert_id = data.get("cert_id")
    file_hash = data.get("file_hash")

    if not cert_id or not file_hash:
        raise HTTPException(status_code=400, detail="cert_id and file_hash are required")

    from verify.verifier import verify_cert
    result = verify_cert(cert_id, file_hash)
    return {"status": result}


# ---------- NEW: QR & verification endpoints ----------

@app.get("/download/{cert_id}")
async def download_cert(cert_id: str):
    """Serves the PDF certificate."""
    path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "outputs", f"EcoReset_Cert_{cert_id}.pdf")
    )
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Certificate not found")
    return FileResponse(
        path,
        media_type="application/pdf",
        filename=f"EcoReset_Cert_{cert_id}.pdf"
    )


@app.get("/download-qr/{cert_id}")
async def download_qr(cert_id: str):
    """Serves the QR code image for the certificate."""
    path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "outputs", f"EcoReset_QR_{cert_id}.png")
    )
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="QR code not found")
    return FileResponse(
        path,
        media_type="image/png",
        filename=f"EcoReset_QR_{cert_id}.png"
    )


@app.get("/api/verify/{cert_id}")
async def verify_certificate(cert_id: str, sig: str, ts: str):
    """
    Verifies the HMAC signature AND checks the database.
    Called when someone scans the QR code.
    """
    # Check 1: TAMPER PROOF
    message = f"{cert_id}:{ts}".encode()
    expected_sig = hmac.new(SECRET_KEY.encode(), message, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(sig, expected_sig):
        return {
            "is_verified": False,
            "is_tamper_proof": False,
            "ok_for_resale": False,
            "message": "🚨 Security Alert: URL Signature Tampered!"
        }

    # Check 2: VERIFICATION (Exists in Memory/DB)
    from verify.verifier import cert_store
    record = cert_store.get(cert_id)
    
    if not record:
        return {
            "is_verified": False,
            "is_tamper_proof": True,
            "ok_for_resale": False,
            "message": "❌ Certificate Not Found in EcoReset Database."
        }

    # Check 3: DEVICE OK FOR RESALE
    return {
        "is_verified": True,
        "is_tamper_proof": True,
        "ok_for_resale": True,
        "device_hash": record.get("file_hash"),
        "timestamp": ts,
        "message": "✅ Authentic Certificate. Device is safe for resale or recycling."
    }

# --------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)