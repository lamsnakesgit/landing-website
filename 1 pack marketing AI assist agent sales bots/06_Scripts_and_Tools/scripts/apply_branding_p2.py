
import fitz

def apply_branding_project2(input_path, output_path):
    doc = fitz.open(input_path)
    print(f"Applying branding to {len(doc)} pages of {input_path}...")
    
    branding_text = "Aiconic agency | instagram.com/aiconicvibe"
    
    for i, page in enumerate(doc):
        w = page.rect.width
        h = page.rect.height
        
        # Branding coordinates (Bottom Right)
        # Assuming same layout as previous presentation
        rect_x0 = w - 180
        rect_y0 = h - 35
        rect_x1 = w
        rect_y1 = h
        
        rect = fitz.Rect(rect_x0, rect_y0, rect_x1, rect_y1)
        
        # Draw white mask
        shape = page.new_shape()
        shape.draw_rect(rect)
        shape.finish(color=(1, 1, 1), fill=(1, 1, 1))
        shape.commit()
        
        # Insert text
        page.insert_text((rect_x0 + 5, rect_y0 + 20), branding_text, fontsize=8, color=(0.2, 0.2, 0.2))
        
    doc.save(output_path)
    print(f"Saved branded PDF to {output_path}")

if __name__ == "__main__":
    apply_branding_project2(
        "Интеллектуальный_отдел_продаж_UPDATED.pdf", 
        "Интеллектуальный_отдел_продаж_Branded.pdf"
    )
