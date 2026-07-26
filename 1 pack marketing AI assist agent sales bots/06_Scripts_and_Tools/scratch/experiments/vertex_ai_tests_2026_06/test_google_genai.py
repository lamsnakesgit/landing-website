import os
from google import genai
from google.genai import types

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/2 accounts sub security/amocrm_wazzup_analytics/google_service_account.json"
client = genai.Client(vertexai=True, project="gen-lang-client-0675220826", location="global")

print("Generating with gemini-3.1-flash-image in global...")
try:
    result = client.models.generate_images(
        model='gemini-3.1-flash-image',
        prompt="A robot holding a sign saying HELLO",
        config=types.GenerateImagesConfig(
            number_of_images=1,
            output_mime_type="image/png",
            aspect_ratio="3:4"
        )
    )
    print("SUCCESS!")
except Exception as e:
    print(f"Error: {e}")
