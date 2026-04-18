import os
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ.get("GOOGLE_API_KEY")

def recover_with_http():
    output_dir = Path("outputs/clips")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # ID операций из лога
    operations = {
        "scene_1_hook": "s2a8kyx4kgcs",
        "scene_2_context": "bwnvkbmhfymb",
        "scene_3_value": "8ffz13npuf87",
        "scene_4_cta": "ts6q2jh9t5iy"
    }
    
    headers = {"x-goog-api-key": API_KEY}
    
    for scene_id, i in operations.items():
        print(f"🧐 Проверка {scene_id} ({i})...")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/veo-3.1-generate-preview/operations/{i}"
        
        try:
            r = requests.get(url, headers=headers)
            data = r.json()
            
            if data.get("done"):
                # Вытаскиваем download_url (uri)
                response = data.get("response", {})
                gen_video_resp = response.get("generateVideoResponse", {})
                samples = gen_video_resp.get("generatedSamples", [])
                
                if samples:
                    video_uri = samples[0].get("video", {}).get("uri")
                    # Превращаем в download link если это files/...
                    if "files/" in video_uri:
                        # Ссылка обычно в формате: https://generativelanguage.googleapis.com/v1beta/files/ID:download?alt=media
                        file_id = video_uri.split("/")[-1]
                        download_url = f"https://generativelanguage.googleapis.com/v1beta/files/{file_id}:download?alt=media&key={API_KEY}"
                        
                        print(f"✅ Готово. Скачивание {file_id}...")
                        video_r = requests.get(download_url)
                        
                        if video_r.status_code == 200:
                            (output_dir / f"{scene_id}.mp4").write_bytes(video_r.content)
                            print(f"💾 СОХРАНЕНО: {scene_id}.mp4")
                        else:
                            print(f"❌ Ошибка скачивания: {video_r.status_code}")
                else:
                    # Вероятно RAI блок
                    print(f"🛑 RAI Filter или пустой ответ: {gen_video_resp.get('raiMediaFilteredReasons')}")
            else:
                print(f"⏳ Еще в процессе (ожидайте)...")
                
        except Exception as e:
            print(f"🔥 Ошибка: {e}")

if __name__ == "__main__":
    recover_with_http()
