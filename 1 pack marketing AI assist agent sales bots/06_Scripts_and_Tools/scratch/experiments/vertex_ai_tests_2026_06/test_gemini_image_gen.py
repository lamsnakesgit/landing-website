import os
from google import genai
from google.genai import types

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/2 accounts sub security/amocrm_wazzup_analytics/google_service_account.json"

client = genai.Client(vertexai=True, project="gen-lang-client-0675220826", location="us-central1")

print("Testing generate_content with IMAGE modality on gemini-3.1-flash-image...")
try:
    response = client.models.generate_content(
        model='gemini-3.1-flash-image',
        contents='A sharp close-up mugshot of a sleek humanoid robot in an orange prison uniform, looking directly at the viewer with glowing red eyes. The robot holds a sign with text "CLAUDE ЗАБАНИЛИ. КТО ДАЛЬШЕ?" in bold typography.',
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
        )
    )
    print("SUCCESS!")
    # Let's inspect the response to see where the image bytes are
    for part in response.candidates[0].content.parts:
        if part.inline_data:
            print("Found inline data!")
            print(f"Mime type: {part.inline_data.mime_type}")
            print(f"Data length: {len(part.inline_data.data)}")
        elif part.text:
            print(f"Text part: {part.text}")
except Exception as e:
    print(f"Error: {e}")

print("\nTesting gemini-3.1-pro-image (Nano Banana Pro)...")
try:
    response = client.models.generate_content(
        model='gemini-3.1-pro-image',
        contents='A sharp close-up mugshot of a sleek humanoid robot in an orange prison uniform, looking directly at the viewer with glowing red eyes. The robot holds a sign with text "CLAUDE ЗАБАНИЛИ. КТО ДАЛЬШЕ?" in bold typography.',
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
        )
    )
    print("SUCCESS!")
    for part in response.candidates[0].content.parts:
        if part.inline_data:
            print("Found inline data!")
            print(f"Mime type: {part.inline_data.mime_type}")
            print(f"Data length: {len(part.inline_data.data)}")
except Exception as e:
    print(f"Error: {e}")
