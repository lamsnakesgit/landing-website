import os
from google import genai
from google.genai import types

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "vertex_sa.json"
client = genai.Client(vertexai=True, project="my-project-28666-8-5-26-0-crm", location="us-central1")

try:
    # Let's describe face.png
    image_path = "face.png"
    with open(image_path, "rb") as f:
        img_bytes = f.read()
        
    part = types.Part.from_bytes(data=img_bytes, mime_type="image/png")
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
            "Describe the appearance of the person in this image in detail, including gender, approximate age, hairstyle/hair color, facial features, and skin tone. Factual visual details only.",
            part
        ]
    )
    print("FACE_PNG_DESCRIPTION:")
    print(response.text)
    print("---------------------------------")
    
    # Let's also describe face.webp if it exists
    if os.path.exists("face.webp"):
        with open("face.webp", "rb") as f:
            webp_bytes = f.read()
        part_webp = types.Part.from_bytes(data=webp_bytes, mime_type="image/webp")
        response_webp = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                "Describe the appearance of the person in this image. Factual visual details only.",
                part_webp
            ]
        )
        print("FACE_WEBP_DESCRIPTION:")
        print(response_webp.text)
        print("---------------------------------")

except Exception as e:
    import traceback
    traceback.print_exc()
