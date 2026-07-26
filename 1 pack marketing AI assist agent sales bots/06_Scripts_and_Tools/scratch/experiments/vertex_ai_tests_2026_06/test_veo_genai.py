import os
from google import genai
from google.genai import types

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "vertex_sa.json"
client = genai.Client(vertexai=True, project="my-project-28666-8-5-26-0-crm", location="us-central1")

try:
    print("Testing Image-to-Video setup...")
    
    image_path = "studio_face.png"
    
    # Read image bytes
    with open(image_path, "rb") as f:
        img_bytes = f.read()
        
    img = types.Image(image_bytes=img_bytes, mime_type="image/png")
    
    ref_image = types.VideoGenerationReferenceImage(
        image=img,
        reference_type="ASSET"
    )
    
    import time
    
    print("Testing generate_videos again...")
    response = client.models.generate_videos(
        model='veo-3.1-generate-001',
        prompt='A realistic video of this man talking',
        config=types.GenerateVideosConfig(
            referenceImages=[ref_image]
        )
    )
    print("Response dir:", dir(response))
    print("Response:", response)
    
    # Try just calling result
    print("Polling operation...")
    operation = response
    while not operation.done:
        print("Still generating...")
        time.sleep(10)
        operation = client.operations.get(operation)
        
    if operation.error:
        print("Error:", operation.error)
    else:
        print("Success! Saving videos...")
        for i, video in enumerate(operation.result.generated_videos):
            with open(f"veo_final_clip.mp4", "wb") as f:
                f.write(video.video_bytes)
            print(f"Saved veo_final_clip.mp4!")

    
except Exception as e:
    import traceback
    traceback.print_exc()

