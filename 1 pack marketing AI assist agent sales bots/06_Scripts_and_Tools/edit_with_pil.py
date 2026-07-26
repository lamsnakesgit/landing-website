import os
from PIL import Image, ImageDraw, ImageFont

def edit_poster():
    img_path = "/Users/higherpower/Desktop/afisha_19_07.png"
    out_path = "/Users/higherpower/.gemini/antigravity/brain/41d56b7c-5ba5-4daa-8819-2c57d8aca4f1/afisha_25_07.png"
    
    img = Image.open(img_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    # We assume the cyan banner is near the bottom.
    # Let's find the cyan banner bounding box approximately by searching for cyan pixels
    # Cyan is roughly R < 100, G > 200, B > 200
    cyan_pixels = []
    for y in range(height - 300, height):
        for x in range(width):
            r, g, b = img.getpixel((x, y))
            if r < 120 and g > 180 and b > 180:
                cyan_pixels.append((x, y, r, g, b))
                
    if not cyan_pixels:
        print("Cyan banner not found!")
        # Fallback coordinates
        box = [50, 950, width-50, 1050]
        banner_color = (0, 255, 255)
    else:
        xs = [p[0] for p in cyan_pixels]
        ys = [p[1] for p in cyan_pixels]
        box = [min(xs), min(ys), max(xs), max(ys)]
        banner_color = (cyan_pixels[0][2], cyan_pixels[0][3], cyan_pixels[0][4])
        print(f"Found banner at {box}, color {banner_color}")
    
    # Draw over the banner with the exact banner color
    # Add a little padding to make sure we cover the old text
    draw.rectangle([box[0]-5, box[1]-5, box[2]+5, box[3]+5], fill=banner_color)
    
    # Load a font
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 46)
    except:
        try:
            font = ImageFont.truetype("/Library/Fonts/Arial Bold.ttf", 46)
        except:
            font = ImageFont.load_default()
            
    text = "25.07 В 15:00 | ОФФЛАЙН + ОНЛАЙН"
    
    # Draw the text in black, centered in the banner
    # In newer Pillow, textsize is deprecated, use textbbox
    if hasattr(font, 'getbbox'):
        left, top, right, bottom = font.getbbox(text)
        tw = right - left
        th = bottom - top
    elif hasattr(draw, 'textsize'):
        tw, th = draw.textsize(text, font=font)
    else:
        tw, th = font.getlength(text), 46
        
    tx = box[0] + (box[2] - box[0] - tw) / 2
    ty = box[1] + (box[3] - box[1] - th) / 2 - 5 # slight adjustment
    
    draw.text((tx, ty), text, fill=(0, 0, 0), font=font)
    
    img.save(out_path)
    print(f"Saved to {out_path}")

if __name__ == "__main__":
    edit_poster()
