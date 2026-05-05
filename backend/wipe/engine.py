import os
import secrets
import shutil
import traceback

def secure_wipe_task(job_id, target_path, jobs):
    job = jobs[job_id]
    job["status"] = "running"
    job["progress"] = 0
    job["device_path"] = target_path   # for frontend display

    try:
        # If a single file was given, treat its parent folder as target
        if os.path.isfile(target_path):
            target_path = os.path.dirname(target_path)
        elif not os.path.isdir(target_path):
            job["status"] = "failed"
            job["error"] = "Invalid path"
            return

        # Count total files and directories BEFORE wiping
        total_files = 0
        total_folders = 0
        for root, dirs, files in os.walk(target_path):
            total_files += len(files)
            total_folders += 1   # count current directory (including target_path)
        # total_folders includes the top-most folder (target_path) and all subfolders

        passes = 3
        file_hashes = {}
        files_deleted = 0

        # Wipe files one by one
        processed = 0
        for root, dirs, files in os.walk(target_path, topdown=False):
            for name in files:
                file_path = os.path.join(root, name)
                processed += 1
                progress = int((processed / total_files) * 90) if total_files else 90
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
                    files_deleted += 1
                    file_hashes[file_path] = "deleted_" + secrets.token_hex(8)
                except Exception as e:
                    job["status"] = "completed_with_errors"
                    job["error"] = f"Error wiping {file_path}: {e}"
                    # Continue with other files

        job["progress"] = 95
        job["status"] = "removing folders..."
        try:
            shutil.rmtree(target_path)
        except Exception as e:
            job["status"] = "completed_with_errors"
            job["error"] = f"Could not remove folders: {e}"

        # Final stats
        job["progress"] = 100
        job["status"] = "completed"
        job["hashes"] = file_hashes
        job["files_deleted"] = files_deleted
        job["folders_deleted"] = total_folders   # all directories that were removed

    except Exception as e:
        job["status"] = "failed"
        job["error"] = str(e)