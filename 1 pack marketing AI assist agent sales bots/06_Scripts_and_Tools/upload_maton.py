import os
import requests
import sys

# Disable buffering
sys.stdout.reconfigure(line_buffering=True)

TOKEN = "Tot5eHN_Tm2738fZjWPHQcMH9scggY7KXxztQJCjbpEEq5wP6PhXgweGRQHSUBKSQs4aAno7gRN9XgWtDCiogcaTOorsdcWxFuaMHFfo8A"
FILES = [
    "/Users/higherpower/Movies/web_ai_ddd_web_2026-02-01 19-42-34.mov",
    "/Users/higherpower/Movies/web_ai_ddd_web_2026-02-01 20-57-17.mov"
]

def upload_video(file_path):
    print(f"Uploading {file_path}...")
    size = os.path.getsize(file_path)
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "X-Upload-Content-Length": str(size),
        "X-Upload-Content-Type": "video/quicktime"
    }
    
    metadata = {
        "snippet": {
            "title": os.path.basename(file_path),
            "description": "Uploaded via maton.ai",
            "tags": ["maton", "ai", "web_ai_ddd_web"],
            "categoryId": "22"
        },
        "status": {
            "privacyStatus": "unlisted",
            "selfDeclaredMadeForKids": False
        }
    }
    
    init_url = "https://gateway.maton.ai/youtube/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"
    
    try:
        r = requests.post(init_url, headers=headers, json=metadata, timeout=30)
        if r.status_code != 200:
            print(f"Error init upload: {r.status_code} {r.text}")
            return None
            
        upload_url = r.headers.get("Location")
        if not upload_url:
            print("No Location header returned.")
            return None
            
        print(f"Got upload URL. Uploading data...")
        put_headers = {
            "Content-Type": "video/quicktime"
        }
        with open(file_path, "rb") as f:
            r2 = requests.put(upload_url, headers=put_headers, data=f)
            
        if r2.status_code in [200, 201]:
            video_id = r2.json().get("id")
            print(f"SUCCESS {file_path} -> https://youtu.be/{video_id}")
            return f"https://youtu.be/{video_id}"
        else:
            print(f"Error uploading data: {r2.status_code} {r2.text}")
            return None
    except Exception as e:
        print(f"Exception during upload: {e}")
        return None

results = []
for f in FILES:
    link = upload_video(f)
    if link:
        results.append((f, link))

print("\n--- RESULTS ---")
for path, link in results:
    print(f"PATH: {path}")
    print(f"LINK: {link}")
