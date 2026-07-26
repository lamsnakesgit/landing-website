import os
from PIL import Image, ImageDraw, ImageFont
import requests

def download_font(url, filename):
    if not os.path.exists(filename):
        r = requests.get(url)
        with open(filename, 'wb') as f:
            f.write(r.content)

# Download a nice bold font
download_font("https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat-Bold.ttf", "Montserrat-Bold.ttf")

input_dir = "/Users/higherpower/.gemini/antigravity/brain/da383cca-b77f-4885-b667-f5d1f3ba9fe0"
output_dir = "stickers_watermarked"
os.makedirs(output_dir, exist_ok=True)

# List of files we generated
files = [
    "01_cold_call",
    "02_deal_closed",
    "03_waiting_payment",
    "04_meeting_overload",
    "05_bot_works_24_7",
    "06_client_edits"
]

def add_watermark(image_path, output_path, text="@nnsvt"):
    try:
        with Image.open(image_path) as img:
            # Resize to 512x512
            img = img.resize((512, 512), Image.Resampling.LANCZOS)
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Prepare drawing
            draw = ImageDraw.Draw(img)
            # Try to load font
            try:
                font = ImageFont.truetype("Montserrat-Bold.ttf", 36)
            except:
                font = ImageFont.load_default()
            
            # Calculate text size and position (bottom center)
            # Use textbbox instead of textsize (deprecated in new Pillow)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            
            x = (512 - text_w) / 2
            y = 512 - text_h - 20 # 20px from bottom
            
            # Draw shadow/outline for readability
            shadow_color = (0, 0, 0, 180)
            outline_thickness = 2
            for dx in [-outline_thickness, 0, outline_thickness]:
                for dy in [-outline_thickness, 0, outline_thickness]:
                    draw.text((x + dx, y + dy), text, font=font, fill=shadow_color)
                    
            # Draw main text
            draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
            
            img.save(output_path, "PNG")
            print(f"Saved: {output_path}")
    except Exception as e:
        print(f"Error processing {image_path}: {e}")

# Process them
for f_name in files:
    # Find the exact filename since there is a timestamp suffix
    matching_files = [f for f in os.listdir(input_dir) if f.startswith(f_name) and f.endswith(".png")]
    if matching_files:
        input_file = os.path.join(input_dir, matching_files[0])
        output_file = os.path.join(output_dir, f"{f_name}.png")
        add_watermark(input_file, output_file)
    else:
        print(f"Could not find source image for {f_name}")
