
import fitz

def inject_image_and_fix_footer(pdf_path, image_path, output_path):
    doc = fitz.open(pdf_path)
    print(f"Opening {pdf_path}...")
    
    page_idx = 9 # Page 10
    
    # Reload the image as a PDF page or insert it?
    # Easiest: Insert a new page with the image, delete the old one.
    # Or draw the image over the ENTIRE existing page.
    
    page = doc[page_idx]
    rect = page.rect
    
    # Draw image over the whole page
    # This effectively replaces visual content
    page.insert_image(rect, filename=image_path)
    print(f"Inserted {image_path} over Page {page_idx+1}.")
    
    # Now re-apply the footer because the image might have covered it 
    # OR the image came from v2 (clean) so it has the OLD footer.
    
    # Footer Logic (copied from confirmed script)
    w = page.rect.width
    h = page.rect.height
    
    branding_text = "Aiconic agency | instagram.com/aiconicvibe"
    rect_x0 = w - 180
    rect_y0 = h - 35
    
    # White box to hide whatever footer is in the image
    footer_rect = fitz.Rect(rect_x0, rect_y0, w, h)
    
    shape = page.new_shape()
    shape.draw_rect(footer_rect)
    shape.finish(color=(1, 1, 1), fill=(1, 1, 1))
    shape.commit()
    
    page.insert_text((rect_x0 + 5, rect_y0 + 20), branding_text, fontsize=8, color=(0.2, 0.2, 0.2))
    print("Re-applied Aiconic footer to Page 10.")
    
    doc.save(output_path)
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    # The generated image path from the tool output
    # Note: user won't see this path, but I have it from the tool output.
    # I need to be careful with the filename.
    # The tool said: /Users/higherpower/.gemini/antigravity/brain/20b5aa81-6ead-4f98-bced-da906ef71b22/n8n_slide_retry_1770286889154.png
    # I will copy it to CWD or refer to it directly.
    
    img_path = "/Users/higherpower/.gemini/antigravity/brain/20b5aa81-6ead-4f98-bced-da906ef71b22/n8n_slide_retry_1770286889154.png"
    
    inject_image_and_fix_footer(
        "ИИ-сотрудники_Измеримый_ROI_final.pdf", 
        img_path, 
        "ИИ-сотрудники_Измеримый_ROI_final_v2.pdf"
    )
