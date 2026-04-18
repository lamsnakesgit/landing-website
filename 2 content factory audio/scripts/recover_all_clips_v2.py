import os
from pathlib import Path
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ.get("GOOGLE_API_KEY")

def recover_with_sdk_fix():
    client = genai.Client(api_key=API_KEY)
    output_dir = Path("outputs/clips")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Список ID операций
    operations = {
        "scene_1_hook": "models/veo-3.1-generate-preview/operations/s2a8kyx4kgcs",
        "scene_2_context": "models/veo-3.1-generate-preview/operations/bwnvkbmhfymb",
        "scene_3_value": "models/veo-3.1-generate-preview/operations/8ffz13npuf87",
        "scene_4_cta": "models/veo-3.1-generate-preview/operations/ts6q2jh9t5iy"
    }
    
    for scene_id, op_name in operations.items():
        print(f"🧐 Проверка {scene_id}...")
        try:
            # Важный фикс: создаем объект Operation вручную
            op_obj = types.Operation(name=op_name)
            op = client.operations.get(op_obj)
            
            if op.done:
                # В ответе лежат видео
                if hasattr(op.response, "generated_videos"):
                    vid = op.response.generated_videos[0].video
                    output_path = output_dir / f"{scene_id}.mp4"
                    print(f"✅ Готово. Скачивание {vid.uri}...")
                    
                    # Пытаемся скачать через SDK
                    video_data = client.files.download(file=vid)
                    output_path.write_bytes(video_data)
                    print(f"💾 СОХРАНЕНО: {scene_id}.mp4")
                else:
                    print(f"⚠️ Ошибка RAI или пустой ответ: {op.response}")
            else:
                print(f"⏳ Операция еще в процессе...")
        except Exception as e:
            print(f"🔥 Ошибка: {e}")

if __name__ == "__main__":
    recover_with_sdk_fix()
