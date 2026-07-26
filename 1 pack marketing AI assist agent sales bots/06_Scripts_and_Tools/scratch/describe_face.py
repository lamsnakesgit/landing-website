import os
from google import genai
from google.genai import types

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "vertex_sa.json"
client = genai.Client(vertexai=True, project="my-project-28666-8-5-26-0-crm", location="us-central1")

try:
    image_path = "studio_face.png"
    with open(image_path, "rb") as f:
        img_bytes = f.read()
        
    img = types.Image(image_bytes=img_bytes, mime_type="image/png")
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
            "Describe the appearance of the person in this image in detail, including gender, approximate age, hairstyle/hair color, facial features (eyes, nose, mouth), facial hair, skin tone, and expression. Keep the description focused on factual visual details that would help a text-to-image generator recreate a highly similar person.",
            img
        ]
    )
    print("DESCRIPTION_START")
    print(response.text)
    print("DESCRIPTION_END")
except Exception as e:
    import traceback
    traceback.print_exc()
