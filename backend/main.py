from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid
import os
from wipe.engine import secure_wipe_task 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

jobs = {}

@app.get("/")
def home():
    return {"status": "EcoReset API is Running"}

@app.post("/wipe")
async def start_wipe(data: dict, background_tasks: BackgroundTasks):
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

# --- Role B Endpoints (Awaiting logic from Role B) ---
@app.post("/generate-cert")
def api_generate_cert(data: dict):
    return {"message": "Endpoint ready, awaiting Role B generator logic"}

@app.post("/verify")
def api_verify_cert(data: dict):
    return {"message": "Endpoint ready, awaiting Role B verifier logic"}