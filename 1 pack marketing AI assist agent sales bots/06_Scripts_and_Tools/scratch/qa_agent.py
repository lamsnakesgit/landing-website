import os
import sys
from google import genai
from google.genai import types

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/2 accounts sub security/amocrm_wazzup_analytics/google_service_account.json"

try:
    client = genai.Client(vertexai=True, project="gen-lang-client-0675220826", location="us-central1")
    video_path = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch/series/pacany_i_ii/04_renders/clip2_v2_final_8s.mp4"
    
    print("Загружаем видео в Gemini 2.5 Flash для QA-оценки...")
    
    # Gemini Vertex SDK требует Part.from_uri для больших видео, но попробуем from_bytes для 8-сек.
    with open(video_path, "rb") as f:
        video_bytes = f.read()
        
    part = types.Part.from_bytes(data=video_bytes, mime_type="video/mp4")
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
            part,
            "Выступи в роли строгого QA-агента видеопродакшена. Проанализируй это видео. Особое внимание удели аудиодорожке и речи. Опиши, насколько естественно или УЖАСНО звучит голос, интонации, дикция. Выдай жесткий, но справедливый вердикт по звуку."
        ]
    )
    print("\n=== ОТЧЕТ QA-АГЕНТА (Gemini) ===")
    print(response.text)
    print("==================================")
except Exception as e:
    print(f"Ошибка: {e}")
