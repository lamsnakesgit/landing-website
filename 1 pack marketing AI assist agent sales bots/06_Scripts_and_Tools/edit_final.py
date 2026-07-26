import os
from PIL import Image, ImageDraw, ImageFont

def edit_poster():
    img_path = "/Users/higherpower/.gemini/antigravity/brain/41d56b7c-5ba5-4daa-8819-2c57d8aca4f1/media__1784921529784.jpg"
    out_path = "/Users/higherpower/.gemini/antigravity/brain/41d56b7c-5ba5-4daa-8819-2c57d8aca4f1/final_poster_25_07.png"
    
    img = Image.open(img_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    cyan_pixels = []
    # Search the bottom area for cyan color
    for y in range(height - 400, height - 50):
        for x in range(width):
            r, g, b = img.getpixel((x, y))
            # Cyan detection: high green and blue, lower red
            if r < 140 and g > 180 and b > 180 and abs(g - b) < 50:
                cyan_pixels.append((x, y, r, g, b))
                
    if not cyan_pixels:
        print("Cyan banner not found! Trying broader colors or fixed box.")
        box = [90, 840, 930, 940]
        banner_color = (0, 255, 255)
    else:
        xs = [p[0] for p in cyan_pixels]
        ys = [p[1] for p in cyan_pixels]
        box = [min(xs), min(ys), max(xs), max(ys)]
        banner_color = (cyan_pixels[0][2], cyan_pixels[0][3], cyan_pixels[0][4])
        print(f"Found banner at {box}, color {banner_color}")
        
        # We want to cover the whole banner nicely, including rounded corners if any.
        # So we just use the bounding box.
        
    draw.rectangle([box[0]-2, box[1]-2, box[2]+2, box[3]+2], fill=banner_color)
    
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 36)
    except:
        font = ImageFont.load_default()
            
    text = "25.07 В 15:00 | ОФФЛАЙН + ОНЛАЙН"
    
    if hasattr(font, 'getbbox'):
        left, top, right, bottom = font.getbbox(text)
        tw = right - left
        th = bottom - top
    elif hasattr(draw, 'textsize'):
        tw, th = draw.textsize(text, font=font)
    else:
        tw, th = font.getlength(text), 36
        
    tx = box[0] + (box[2] - box[0] - tw) / 2
    ty = box[1] + (box[3] - box[1] - th) / 2 - 5
    
    draw.text((tx, ty), text, fill=(0, 0, 0), font=font)
    
    img.save(out_path)
    print(f"Saved to {out_path}")

if __name__ == "__main__":
    edit_poster()
