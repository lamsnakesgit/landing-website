import os
from google import genai
from google.genai import types

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "vertex_sa.json"
client = genai.Client(vertexai=True, project="my-project-28666-8-5-26-0-crm", location="us-central1")

try:
    # Load original face.png
    with open("face.png", "rb") as f:
        orig_bytes = f.read()
    orig_part = types.Part.from_bytes(data=orig_bytes, mime_type="image/png")
    
    # Load generated 15.png
    generated_path = "04_Design_and_Media/photo_shoot/15.png"
    with open(generated_path, "rb") as f:
        gen_bytes = f.read()
    gen_part = types.Part.from_bytes(data=gen_bytes, mime_type="image/png")
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
            "Compare the original face in the first image with the generated face in the second image. "
            "Describe the key visual differences (e.g., ethnicity, face shape, eyes, nose, lips, eyebrows, skin tone, hair) "
            "and write a highly detailed description of the first image's face. "
            "Then, write a detailed english prompt for a text-to-image generator (Imagen 3) that will generate a face "
            "that looks much closer to the first image, while keeping the setting (wearing a white bathrobe with a white towel wrapped around her hair in a bathroom/spa).",
            orig_part,
            gen_part
        ]
    )
    print("COMPARISON_START")
    print(response.text)
    print("COMPARISON_END")

except Exception as e:
    import traceback
    traceback.print_exc()
