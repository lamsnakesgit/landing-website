import os
from google import genai
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
API_KEY = os.environ.get("GOOGLE_API_KEY")

# Список всех ID операций, которые я нашел в истории нашего чата
OPERATIONS = [
    "c6zoovip38vr", # Scene 1 Hook (v2 Lite)
    "knpg1dep35pq", # Scene 3 Value (v2 Lite)
    "3f4qrdnptafw", # Scene 1 Hook (v2 Normal - killed but might be ready)
    "p7hy9p8nzwsm", # Scene 1 Hook (Attempt before quota hit)
    "27xlzqyqjh96"  # Scene 1 Hook (v1 wrong photo - if you want it back too)
]

RECOVERY_DIR = Path("outputs/RECOVERED_STUFF")
RECOVERY_DIR.mkdir(parents=True, exist_ok=True)

def recover():
    client = genai.Client(api_key=API_KEY)
    print(f"🎬 Начинаю попытку восстановления {len(OPERATIONS)} видео из облака...")
    
    for op_id in OPERATIONS:
        full_name = f"models/veo-3.1-lite-generate-preview/operations/{op_id}"
        # Пробуем как лайт, так и нормальную модель (на случай если ID от другой)
        found = False
        for model_prefix in ["veo-3.1-lite-generate-preview", "veo-3.1-generate-preview"]:
            try:
                name = f"models/{model_prefix}/operations/{op_id}"
                print(f"🔍 Проверка {name}...")
                op = client.operations.get(name=name)
                
                if op.done:
                    if hasattr(op.response, "generated_videos"):
                        vid = op.response.generated_videos[0].video
                        output_path = RECOVERY_DIR / f"recovered_{op_id}.mp4"
                        print(f"✅ НАЙДЕНО! Скачиваю {vid.uri}...")
                        video_data = client.files.download(file=vid)
                        output_path.write_bytes(video_data)
                        print(f"💾 Восстановлено в {output_path}")
                        found = True
                        break
                else:
                    print(f"⏳ Сцена {op_id} еще в процессе или была отменена.")
            except Exception:
                continue
        
        if not found:
            print(f"❌ Не удалось восстановить {op_id} (возможно, удалено из облака или неверный ID).")

if __name__ == "__main__":
    recover()
