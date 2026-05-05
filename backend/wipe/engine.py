import os
import secrets
import shutil
import traceback

def secure_wipe_task(job_id, target_path, jobs):
    job = jobs[job_id]
    job["status"] = "running"
    job["progress"] = 0

    try:
        if os.path.isfile(target_path):
            target_path = os.path.dirname(target_path)
        elif not os.path.isdir(target_path):
            job["status"] = "failed"
            job["error"] = "Invalid path"
            return

        file_list = []
        for root, dirs, files in os.walk(target_path, topdown=False):
            for name in files:
                file_list.append(os.path.join(root, name))

        total_files = len(file_list)
        passes = 3
        file_hashes = {}

        for idx, file_path in enumerate(file_list, 1):
            progress = int((idx / total_files) * 90) if total_files else 90
            job["progress"] = progress
            job["status"] = f"wiping {os.path.basename(file_path)}..."

            try:
                file_size = os.path.getsize(file_path)
                for _ in range(passes):
                    with open(file_path, "wb") as f:
                        written = 0
                        while written < file_size:
                            remaining = file_size - written
                            chunk = min(1024 * 1024, remaining)
                            f.write(secrets.token_bytes(chunk))
                            written += chunk
                os.remove(file_path)
                file_hashes[file_path] = "deleted_" + secrets.token_hex(8)
            except Exception as e:
                job["status"] = "completed_with_errors"
                job["error"] = f"Error wiping {file_path}: {e}"
                continue

        job["progress"] = 95
        job["status"] = "removing folder..."
        try:
            shutil.rmtree(target_path)
        except Exception as e:
            job["status"] = "completed_with_errors"
            job["error"] = f"Could not remove folder: {e}"

        job["progress"] = 100
        job["status"] = "completed"
        job["hashes"] = file_hashes

    except Exception as e:
        job["status"] = "failed"
        job["error"] = str(e)