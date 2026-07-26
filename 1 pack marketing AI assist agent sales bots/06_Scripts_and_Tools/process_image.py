from PIL import Image

def process_sticker(input_path, output_path):
    try:
        with Image.open(input_path) as img:
            # Resize to 512x512
            img = img.resize((512, 512), Image.Resampling.LANCZOS)
            
            # Save as PNG
            img.save(output_path, "PNG")
            print(f"Successfully processed {output_path}")
    except Exception as e:
        print(f"Error processing image: {e}")

if __name__ == "__main__":
    input_file = "/Users/higherpower/.gemini/antigravity/brain/da383cca-b77f-4885-b667-f5d1f3ba9fe0/ai_money_bot_1780748806995.png"
    output_file = "sticker_01.png"
    process_sticker(input_file, output_file)
