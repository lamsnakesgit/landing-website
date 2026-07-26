import os
import google.auth
from google.auth.transport.requests import Request
import requests
import json
import base64
from PIL import Image, ImageDraw, ImageFont
import time

LOCATION = "us-central1"
WORKSPACE_ROOT = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots"
SA_PATH = os.path.join(WORKSPACE_ROOT, "vertex_sa.json")

prompts = [
    "Cyberpunk cinematic shot. A glowing, hyper-intelligent brain in a glass jar being taken away by men in dark, expensive mafia suits. Rain, neon reflections, dark and gritty atmosphere.",
    "A neon-lit cyberpunk street in Asia. A sleek, powerful android mafia member standing confidently, holding a glowing data core. Red and blue neon lighting, cinematic realism."
]

def add_watermark(image_path: str):
    """
    Добавляет водяной знак @lamanopro_ и синюю галочку на изображение.
    """
    img = Image.open(image_path).convert("RGBA")
    txt = Image.new("RGBA", img.size, (255,255,255,0))
    
    font_size = int(img.height * 0.04)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except IOError:
        font = ImageFont.load_default()
    
    draw = ImageDraw.Draw(txt)
    text = "@lamanopro_"
    
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    # Dimensions for the badge
    badge_size = int(text_h * 1.2)
    margin = int(font_size * 0.5)
    
    total_w = text_w + badge_size + margin
    
    # Position (bottom center)
    x = (img.width - total_w) // 2
    y = img.height - text_h - int(img.height * 0.05)
    
    # Draw dark overlay for text readability
    padding = 10
    draw.rectangle(
        [x - padding, y - padding, x + total_w + padding, y + max(text_h, badge_size) + padding],
        fill=(0, 0, 0, 160)
    )
    
    # Draw text
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
    
    # Draw verification badge (blue circle + white checkmark)
    badge_x = x + text_w + margin
    badge_y = y + (text_h - badge_size) // 2
    draw.ellipse([badge_x, badge_y, badge_x + badge_size, badge_y + badge_size], fill=(29, 155, 240, 255))
    
    # Draw checkmark inside badge
    cx, cy = badge_x + badge_size * 0.5, badge_y + badge_size * 0.5
    sz = badge_size
    pts = [
        (cx - sz*0.2, cy),
        (cx - sz*0.05, cy + sz*0.15),
        (cx + sz*0.25, cy - sz*0.2)
    ]
    draw.line(pts, fill="white", width=max(2, int(sz/8)), joint="curve")
    
    out = Image.alpha_composite(img, txt)
    out.convert("RGB").save(image_path)
    print(f"Водяной знак добавлен на {image_path}")

def generate_carousel(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SA_PATH
    
    if not os.path.exists(SA_PATH):
        print(f"Error: Service account file not found at {SA_PATH}")
        return
        
    with open(SA_PATH, 'r') as f:
        sa_data = json.load(f)
        project_id = sa_data.get("project_id")
        
    credentials, _ = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
    credentials.refresh(Request())
    
    url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{LOCATION}/publishers/google/models/imagen-3.0-generate-001:predict"
    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json; charset=utf-8"
    }

    for i, prompt in enumerate(prompts):
        print(f"Generating slide {i+1}...")
        data = {
            "instances": [{"prompt": prompt}],
            "parameters": {"sampleCount": 1, "aspectRatio": "1:1"}
        }
        
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            resp_json = response.json()
            if "predictions" in resp_json and len(resp_json["predictions"]) > 0:
                encoded_image = resp_json["predictions"][0]["bytesBase64Encoded"]
                image_data = base64.b64decode(encoded_image)
                
                output_path = os.path.join(output_dir, f"slide_{i+1}.png")
                with open(output_path, "wb") as f:
                    f.write(image_data)
                    
                # Add watermark
                add_watermark(output_path)
                print(f"✅ Slide {i+1} saved to {output_path}")
            else:
                print(f"Error on slide {i+1}: No predictions.")
        else:
            print(f"Error {response.status_code} on slide {i+1}: {response.text}")
            
        time.sleep(2) # To avoid rate limits

if __name__ == "__main__":
    artifact_dir = "/Users/higherpower/.gemini/antigravity/brain/c1edc89f-b82d-476c-8418-be8adaaf40a4/carousel_output"
    generate_carousel(artifact_dir)
