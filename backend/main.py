from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
import uuid
import os
import hmac
import hashlib
import platform
import string
from pathlib import Path
from wipe.engine import secure_wipe_task

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

jobs = {}

SECRET_KEY = os.environ.get("ECORESET_SECRET", "dev-secret-change-in-production")


# ---------- Request models ----------
class WipeRequest(BaseModel):
    path: str

class BatchWipeRequest(BaseModel):
    paths: List[str]

class CertRequest(BaseModel):
    job_id: str
    device_path: str = "Unknown Device"

class VerifyRequest(BaseModel):
    cert_id: str
    file_hash: str

class BatchCertRequest(BaseModel):
    job_ids: List[str]
    device_paths: List[str]


# ---------- Endpoints ----------
@app.get("/")
def home():
    return {"status": "EcoReset API is Running"}


@app.get("/drives")
async def get_drives():
    """Returns list of available drives (Windows) or root folders (Linux/Mac)"""
    drives = []
    if platform.system() == "Windows":
        for letter in string.ascii_uppercase:
            drive_path = f"{letter}:\\"
            if os.path.exists(drive_path):
                drives.append({"drive": drive_path, "label": f"{drive_path} (Local Disk)"})
    else:
        # Linux/Mac: check common mount points
        for path in ["/", "/media", "/mnt"]:
            if os.path.exists(path):
                for item in os.listdir(path):
                    full = os.path.join(path, item)
                    if os.path.ismount(full) or (path == "/" and os.path.isdir(full)):
                        drives.append({"drive": full, "label": full})
        # Also include user's home directory
        home = str(Path.home())
        drives.append({"drive": home, "label": f"Home: {home}"})
    return drives


@app.post("/wipe")
async def start_wipe(data: WipeRequest, background_tasks: BackgroundTasks):
    target_path = data.path
    if not target_path or not os.path.exists(target_path):
        raise HTTPException(status_code=400, detail="Invalid path")
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "starting", "progress": 0}
    background_tasks.add_task(secure_wipe_task, job_id, target_path, jobs)
    return {"job_id": job_id}


@app.post("/wipe-batch")
async def start_batch_wipe(request: BatchWipeRequest, background_tasks: BackgroundTasks):
    job_ids = []
    for path in request.paths:
        if not path or not os.path.exists(path):
            continue
        job_id = str(uuid.uuid4())
        jobs[job_id] = {"status": "starting", "progress": 0}
        background_tasks.add_task(secure_wipe_task, job_id, path, jobs)
        job_ids.append(job_id)
    if not job_ids:
        raise HTTPException(status_code=400, detail="No valid paths provided")
    return {"job_ids": job_ids}


@app.get("/status/{job_id}")
async def get_status(job_id: str):
    return jobs.get(job_id, {"status": "not_found"})


@app.post("/generate-cert")
async def api_generate_cert(data: CertRequest):
    job_id = data.job_id
    device_path = data.device_path

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


@app.post("/generate-batch-cert")
async def api_generate_batch_cert(data: BatchCertRequest):
    """
    Generate a single certificate for multiple wiped devices (batch).
    Expects {"job_ids": [...], "device_paths": [...]}
    """
    job_ids = data.job_ids
    device_paths = data.device_paths

    if not job_ids or not device_paths:
        raise HTTPException(status_code=400, detail="Missing job_ids or device_paths")
    if len(job_ids) != len(device_paths):
        raise HTTPException(status_code=400, detail="job_ids and device_paths length mismatch")

    # Collect all hashes from each job
    all_hashes = []
    for job_id in job_ids:
        job = jobs.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        job_hashes = job.get("hashes", {})
        all_hashes.extend(job_hashes.values())

    combined = "".join(sorted(all_hashes))
    master_hash = hashlib.sha256(combined.encode()).hexdigest()

    # Create a comma-separated list of all device paths
    combined_device_paths = ", ".join(device_paths)

    from cert.generator import create_certificate
    result = create_certificate(file_hash=master_hash, device_path=combined_device_paths)
    return result


@app.post("/verify")
async def api_verify_cert(data: VerifyRequest):
    cert_id = data.cert_id
    file_hash = data.file_hash

    if not cert_id or not file_hash:
        raise HTTPException(status_code=400, detail="cert_id and file_hash are required")

    from verify.verifier import verify_cert
    result = verify_cert(cert_id, file_hash)
    return {"status": result}


# ---------- QR & verification endpoints ----------
@app.get("/download/{cert_id}")
async def download_cert(cert_id: str):
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
    message = f"{cert_id}:{ts}".encode()
    expected_sig = hmac.new(SECRET_KEY.encode(), message, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(sig, expected_sig):
        return {
            "is_verified": False,
            "is_tamper_proof": False,
            "ok_for_resale": False,
            "message": "🚨 Security Alert: URL Signature Tampered!"
        }

    from verify.verifier import cert_store
    record = cert_store.get(cert_id)
    
    if not record:
        return {
            "is_verified": False,
            "is_tamper_proof": True,
            "ok_for_resale": False,
            "message": "❌ Certificate Not Found in EcoReset Database."
        }

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