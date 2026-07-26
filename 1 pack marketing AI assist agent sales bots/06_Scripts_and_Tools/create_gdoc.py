import os
import json
import requests
import sys

TOKEN = "Tot5eHN_Tm2738fZjWPHQcMH9scggY7KXxztQJCjbpEEq5wP6PhXgweGRQHSUBKSQs4aAno7gRN9XgWtDCiogcaTOorsdcWxFuaMHFfo8A"
VIDEO_LINK = "https://youtu.be/X9lHrgPwttk"
DOC_TITLE = "Транскрипция видео Ледовских"

print("Reading transcript...")
try:
    with open("transcript.txt", "r", encoding="utf-8") as f:
        text = f.read()
    # clean up text
    text = " ".join(text.split())
except Exception as e:
    print(f"Error reading transcript: {e}")
    sys.exit(1)

content = f"Ссылка на видео: {VIDEO_LINK}\n\nТранскрипция:\n{text}"

# write to a temporary file
temp_file = "transcript_full_for_doc.txt"
with open(temp_file, "w", encoding="utf-8") as f:
    f.write(content)

print("Uploading to Google Drive as Google Doc...")
url = "https://gateway.maton.ai/google-drive/upload/drive/v3/files?uploadType=multipart"

# Google Doc mimetype
metadata = {
    "name": DOC_TITLE,
    "mimeType": "application/vnd.google-apps.document"
}

with open(temp_file, "rb") as f:
    files = {
        "metadata": (None, json.dumps(metadata), "application/json"),
        "file": (os.path.basename(temp_file), f, "text/plain")
    }
    response = requests.post(
        url,
        headers={"Authorization": f"Bearer {TOKEN}"},
        files=files
    )

if response.status_code == 200:
    res_json = response.json()
    doc_id = res_json.get("id")
    print(f"Success! Document ID: {doc_id}")
    print(f"Link: https://docs.google.com/document/d/{doc_id}/edit")
    
    # Optional: share file globally so user can read it, or just return link
    # But maton defaults to private. Let's make it anyone with link can read
    print("Making the document accessible via link...")
    share_url = f"https://gateway.maton.ai/google-drive/drive/v3/files/{doc_id}/permissions"
    share_data = {
        "role": "reader",
        "type": "anyone"
    }
    r_share = requests.post(
        share_url,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json"
        },
        json=share_data
    )
    if r_share.status_code == 200:
        print("Document is now accessible via link!")
    else:
        print(f"Failed to share: {r_share.status_code} {r_share.text}")
else:
    print(f"Failed to upload: {response.status_code} {response.text}")

