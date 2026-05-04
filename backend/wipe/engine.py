import os
import secrets
import hashlib

def secure_wipe_task(job_id, path, jobs_dict):
    try:
        files = []
        # Gather all files in the directory
        for root, dirs, filenames in os.walk(path):
            for f in filenames:
                files.append(os.path.join(root, f))
        
        total = len(files)
        if total == 0:
            jobs_dict[job_id] = {"status": "completed", "progress": 100, "hashes": {}}
            return

        failed_files = []
        file_hashes = {}

        for index, file_path in enumerate(files):
            try:
                # 1. Generate SHA-256 Hash BEFORE wiping (Requirement for Role B)
                sha256_hash = hashlib.sha256()
                with open(file_path, "rb") as f:
                    for byte_block in iter(lambda: f.read(4096), b""):
                        sha256_hash.update(byte_block)
                file_hashes[file_path] = sha256_hash.hexdigest()

                # 2. Secure Overwrite
                size = os.path.getsize(file_path)
                with open(file_path, "ba+", buffering=0) as f:
                    f.write(secrets.token_bytes(size))
                
                # 3. Delete File
                os.remove(file_path)

            except Exception as e:
                # Catch permission errors (like the Notepad test)
                failed_files.append(f"{file_path}: {str(e)}")
            
            # Update progress for the UI (Role C)
            jobs_dict[job_id]["progress"] = int(((index + 1) / total) * 100)
            jobs_dict[job_id]["status"] = "wiping"

        # Final Status Update
        if failed_files:
            jobs_dict[job_id]["status"] = "completed_with_errors"
            jobs_dict[job_id]["errors"] = failed_files
        else:
            jobs_dict[job_id]["status"] = "completed"
        
        # Store hashes for Role B to pick up
        jobs_dict[job_id]["hashes"] = file_hashes

    except Exception as e:
        jobs_dict[job_id]["status"] = f"system_error: {str(e)}"