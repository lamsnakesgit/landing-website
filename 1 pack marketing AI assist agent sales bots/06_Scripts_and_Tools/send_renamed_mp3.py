import os, urllib.request, uuid, mimetypes
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("ANTIGRAVITY_BOT_TOKEN")
CHAT_ID = "888005446"

old_path = "sales_pitch.mp3"
new_path = "Секрет_бесплатных_лидов_СтикерМаркетинг.mp3"

if os.path.exists(old_path):
    import shutil
    shutil.copy(old_path, new_path)

def multipart_form(fields, files):
    boundary = "----ClineBoundary" + uuid.uuid4().hex
    body = bytearray()
    for name, value in fields.items():
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        body.extend(str(value).encode())
        body.extend(b"\r\n")
    for name, path in files.items():
        path = Path(path)
        mime = "audio/mpeg"
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="{name}"; filename="{path.name}"\r\n'.encode())
        body.extend(f"Content-Type: {mime}\r\n\r\n".encode())
        body.extend(path.read_bytes())
        body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode())
    return bytes(body), boundary

body, boundary = multipart_form({"chat_id": CHAT_ID, "caption": "🔥 Аудио-визитка с правильным названием для канала/профиля"}, {"audio": new_path})
req = urllib.request.Request(f"https://api.telegram.org/bot{BOT_TOKEN}/sendAudio", data=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}, method="POST")
with urllib.request.urlopen(req, timeout=90) as resp:
    print("Sent:", resp.status)
