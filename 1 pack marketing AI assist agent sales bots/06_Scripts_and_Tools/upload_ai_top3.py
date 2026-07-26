import os
import requests
import sys

sys.stdout.reconfigure(line_buffering=True)

TOKEN = "Tot5eHN_Tm2738fZjWPHQcMH9scggY7KXxztQJCjbpEEq5wP6PhXgweGRQHSUBKSQs4aAno7gRN9XgWtDCiogcaTOorsdcWxFuaMHFfo8A"
FILES = [
    "/Users/higherpower/Movies/Content_Plan_Fact/ai club pro video1048586586 8 11 25 _ a b 18 coaching.mp4",
    "/Users/higherpower/Movies/kai - most intensive course ai/ai_kai_intensitve_2025-09-25 18-50-17.mov",
    "/Users/higherpower/Movies/kai - most intensive course ai/ai_kai_intensitve_2025-09-25 21-07-47.mov"
]

def upload_video(file_path):
    print(f"Uploading {file_path}...")
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None
        
    size = os.path.getsize(file_path)
    
    # Determine content type based on extension
    ext = os.path.splitext(file_path)[1].lower()
    content_type = "video/quicktime" if ext == ".mov" else "video/mp4"
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "X-Upload-Content-Length": str(size),
        "X-Upload-Content-Type": content_type
    }
    
    metadata = {
        "snippet": {
            "title": os.path.basename(file_path),
            "description": "Uploaded via maton.ai\nАвтор: https://t.me/nnsvt",
            "tags": ["maton", "ai", "nnsvt"],
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
            "Content-Type": content_type
        }
        with open(file_path, "rb") as f:
            r2 = requests.put(upload_url, headers=put_headers, data=f)
            
        if r2.status_code in [200, 201]:
            video_id = r2.json().get("id")
            link = f"https://youtu.be/{video_id}"
            print(f"SUCCESS {file_path} -> {link}")
            return link
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

# Telegram Notification (optional, based on previous pattern)
import urllib.request
import urllib.parse
TG_TOKEN = "7969376669:AAGxI8X0h_9kH338nE9296q05r8K9n98wI0"
CHAT_ID = "619074092"
msg = "✅ Топ-3 AI-видео успешно загружены:\n\n"
for path, link in results:
    msg += f"🎬 {os.path.basename(path)}\n🔗 {link}\n\n"

try:
    urllib.request.urlopen(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
        data=urllib.parse.urlencode({"chat_id": CHAT_ID, "text": msg}).encode())
except Exception as e:
    print("TG Note failed:", e)
