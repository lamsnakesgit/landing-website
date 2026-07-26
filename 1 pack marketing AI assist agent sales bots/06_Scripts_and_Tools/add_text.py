from PIL import Image, ImageDraw, ImageFont

def draw_text_on_image(img_path, headline, subtext, out_path):
    img = Image.open(img_path).convert("RGBA")
    txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)
    
    width, height = img.size
    
    # Fonts
    try:
        font_h1 = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", int(height * 0.06), index=1) # Bold
        font_p = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", int(height * 0.04))
    except IOError:
        font_h1 = ImageFont.load_default()
        font_p = ImageFont.load_default()
        
    # Draw dark gradient/box at the top for readability
    box_h = int(height * 0.35)
    draw.rectangle([0, 0, width, box_h], fill=(0, 0, 0, 180))
    
    # Text positioning
    margin_x = int(width * 0.05)
    y_pos = int(height * 0.05)
    
    # Draw headline
    draw.text((margin_x, y_pos), headline, font=font_h1, fill="white", spacing=10)
    
    # Calculate height of headline
    bbox = draw.multiline_textbbox((margin_x, y_pos), headline, font=font_h1, spacing=10)
    y_pos = bbox[3] + int(height * 0.02)
    
    # Draw subtext
    draw.text((margin_x, y_pos), subtext, font=font_p, fill=(200, 200, 200), spacing=10)
    
    out = Image.alpha_composite(img, txt_layer)
    out.convert("RGB").save(out_path)
    print(f"Saved {out_path}")

# Slide 1
s1_img = "/Users/higherpower/.gemini/antigravity/brain/c1edc89f-b82d-476c-8418-be8adaaf40a4/carousel_output/slide_1.png"
h1 = "Сверхинтеллект\nзабирают у масс."
p1 = "Claude уже забанили.\nКто следующий? GPT? Gemini?"
draw_text_on_image(s1_img, h1, p1, s1_img)

# Slide 5
s2_img = "/Users/higherpower/.gemini/antigravity/brain/c1edc89f-b82d-476c-8418-be8adaaf40a4/carousel_output/slide_2.png"
h2 = "Только свой Open-Source."
p2 = "Берем мощные модели из Китая.\nИ тренируем их на своих весах и мозгах."
draw_text_on_image(s2_img, h2, p2, s2_img)
