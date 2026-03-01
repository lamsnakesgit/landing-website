
import fitz

def apply_global_branding(input_path, output_path):
    doc = fitz.open(input_path)
    print(f"Applying branding to {len(doc)} pages...")
    
    # Text to add
    branding_text = "Aiconic agency | instagram.com/aiconicvibe"
    
    for i, page in enumerate(doc):
        # Get dimensions
        w = page.rect.width
        h = page.rect.height
        
        # Coordinates for Bottom Right "notebooklm"
        # Assuming it's small, in the corner.
        # Let's cover a box and write text.
        # Approx box: from w-150, h-40 to w-10, h-10?
        # User can verify position with grid, but for now I'll make a best guess 
        # based on standard "branding footer" location.
        
        # Define Cover Rect (White Box)
        # Assuming bottom right corner. 
        # X: Width - 180 to Width
        # Y: Height - 30 to Height
        rect_x0 = w - 180
        rect_y0 = h - 35
        rect_x1 = w
        rect_y1 = h
        
        rect = fitz.Rect(rect_x0, rect_y0, rect_x1, rect_y1)
        
        # Draw white rectangle to hide "notebooklm"
        shape = page.new_shape()
        shape.draw_rect(rect)
        shape.finish(color=(1, 1, 1), fill=(1, 1, 1)) # White fill, white border
        shape.commit()
        
        # Insert new text
        # color is RGB. Black = (0,0,0) or Dark Grey
        page.insert_text((rect_x0 + 5, rect_y0 + 20), branding_text, fontsize=8, color=(0.2, 0.2, 0.2))
        
        if i == 0:
            print(f"Page 1 dims: {w}x{h}. Placed text at {rect_x0},{rect_y0}")

    doc.save(output_path)
    print(f"Saved modified PDF to {output_path}")

if __name__ == "__main__":
    apply_global_branding("ИИ-сотрудники_Измеримый_ROI_v2.pdf", "ИИ-сотрудники_Измеримый_ROI_v3_draft.pdf")
