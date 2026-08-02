import os
import json
import subprocess
import time
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ.get("MATON_API_KEY")

if not API_KEY:
    print("MATON_API_KEY is missing from .env!", flush=True)
    exit(1)

# Example files list (Users can replace this or pass via args)
youtube_files = [
    # Add absolute paths here
]

google_drive_files = [
    # Add absolute paths here
]

yt_url = "https://gateway.maton.ai/youtube/upload/youtube/v3/videos?uploadType=multipart&part=snippet,status"
gd_url = "https://gateway.maton.ai/google-drive/upload/drive/v3/files?uploadType=multipart"

print(f"Starting upload job. Google Drive: {len(google_drive_files)} files, YouTube: {len(youtube_files)} files.", flush=True)

# Google Drive Uploads
for idx, file_path in enumerate(google_drive_files):
    if not os.path.exists(file_path):
        print(f"[Google Drive] File not found: {file_path}", flush=True)
        continue
    
    filename = os.path.basename(file_path)
    print(f"[Google Drive {idx+1}/{len(google_drive_files)}] Uploading {filename}...", flush=True)
    
    metadata = {"name": filename}
    cmd = [
        "curl", "-s", "-X", "POST", gd_url,
        "-H", f"Authorization: Bearer {API_KEY}",
        "-F", f"metadata={json.dumps(metadata)};type=application/json",
        "-F", f"file=@{file_path};type=application/octet-stream"
    ]
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    duration = time.time() - start_time
    
    print(f"✅ [Google Drive] Uploaded in {duration:.1f}s. Result: {result.stdout.strip()}", flush=True)

# YouTube Uploads
total_yt = len(youtube_files)
for idx, file_path in enumerate(youtube_files):
    if not os.path.exists(file_path):
        print(f"[YouTube] File not found: {file_path}", flush=True)
        continue
        
    filename = os.path.basename(file_path)
    print(f"\n[YouTube {idx+1}/{total_yt}] Uploading {filename}...", flush=True)
    
    metadata = {
        "snippet": {
            "title": filename,
            "description": "Uploaded via Maton AI Gateway"
        },
        "status": {
            "privacyStatus": "unlisted"
        }
    }
    cmd = [
        "curl", "-s", "-X", "POST", yt_url,
        "-H", f"Authorization: Bearer {API_KEY}",
        "-F", f"metadata={json.dumps(metadata)};type=application/json",
        "-F", f"file=@{file_path};type=video/mp4"
    ]
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    duration = time.time() - start_time
    resp = result.stdout
    
    try:
        data = json.loads(resp)
        if "id" in data:
            yt_link = f"https://youtu.be/{data['id']}"
            print(f"✅ [YouTube] Uploaded in {duration:.1f}s! Link: {yt_link}", flush=True)
            print(f"🔗 Оригинал: file://{file_path}", flush=True)
        else:
            print(f"❌ [YouTube] Failed. Response: {resp}", flush=True)
    except json.JSONDecodeError:
        print(f"❌ [YouTube] JSON Error. Raw response: {resp}", flush=True)
        
    if idx + 1 < total_yt:
        print(f"⏳ Waiting 2 seconds before next upload...", flush=True)
        time.sleep(2)

print("\n🎉 All uploads finished!", flush=True)
