import os
import requests
import sys

TOKEN = "Tot5eHN_Tm2738fZjWPHQcMH9scggY7KXxztQJCjbpEEq5wP6PhXgweGRQHSUBKSQs4aAno7gRN9XgWtDCiogcaTOorsdcWxFuaMHFfo8A"
VIDEO_ID = "X9lHrgPwttk"

print(f"Reading transcript for {VIDEO_ID} from transcript.txt...")
try:
    with open("transcript.txt", "r", encoding="utf-8") as f:
        text = f.read()
    # Replace single newlines with spaces to make it a paragraph, but leave double newlines if any
    text = " ".join(text.split())
    print(f"Transcript fetched! Length: {len(text)} chars.")
except Exception as e:
    print(f"Error reading transcript: {e}")
    sys.exit(1)

# Now fetch the current snippet
print("Fetching current video snippet...")
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}
url_get = f"https://gateway.maton.ai/youtube/youtube/v3/videos?part=snippet&id={VIDEO_ID}"

r = requests.get(url_get, headers=headers)
if r.status_code != 200:
    print(f"Failed to get video: {r.status_code} {r.text}")
    sys.exit(1)

data = r.json()
if not data.get("items"):
    print("Video not found.")
    sys.exit(1)

snippet = data["items"][0]["snippet"]

# Clean up text to avoid invalid description characters (like angle brackets)
text = text.replace('<', '').replace('>', '')

# Add transcript to description
current_desc = snippet.get("description", "")
if "Транскрипция:" not in current_desc:
    new_desc = current_desc + "\n\nТранскрипция:\n" + text
else:
    print("Transcript already added?")
    new_desc = current_desc

# Truncate if it exceeds YouTube limits (max 5000 chars for description)
if len(new_desc) > 4800:
    new_desc = new_desc[:4800] + "... (Текст обрезан)"

snippet["description"] = new_desc

print("Updating video on YouTube...")
url_put = f"https://gateway.maton.ai/youtube/youtube/v3/videos?part=snippet"

payload = {
    "id": VIDEO_ID,
    "snippet": snippet
}

r_put = requests.put(url_put, headers=headers, json=payload)
if r_put.status_code in [200, 204]:
    print("Success! Description updated.")
else:
    print(f"Failed to update description: {r_put.status_code} {r_put.text}")
