
import fitz

def apply_final_fixes(input_path, output_path):
    doc = fitz.open(input_path)
    print(f"Opening {input_path}...")
    
    # Page 10 (index 9)
    page_idx = 9 
    if len(doc) > page_idx:
        page = doc[page_idx]
        w = page.rect.width
        h = page.rect.height
        
        print(f"Modifying Page {page_idx+1} (Size: {w}x{h})...")
        
        # Assume Center for Nextbot
        # Let's clean a box in the middle.
        # Box size: 300x100?
        cw = 400
        ch = 150
        cx = (w - cw) / 2
        cy = (h - ch) / 2
        
        rect = fitz.Rect(cx, cy, cx + cw, cy + ch)
        
        # Draw white rect (Mask)
        shape = page.new_shape()
        shape.draw_rect(rect)
        shape.finish(color=(1, 1, 1), fill=(1, 1, 1))
        shape.commit()
        
        # Insert "N8N" text
        # Centered text is tricky with simple insert_text, so we estimate position
        text = "N8N"
        fontsize = 72
        # Approx width of text?
        # A rough guess for centering text
        text_x = cx + (cw / 2) - 60 # rough offset
        text_y = cy + (ch / 2) + 20
        
        page.insert_text((text_x, text_y), text, fontsize=fontsize, color=(0, 0, 0))
        print("Applied N8N patch.")
        
    else:
        print(f"Error: Page {page_idx+1} not found.")

    doc.save(output_path)
    print(f"Saved final PDF to {output_path}")

if __name__ == "__main__":
    apply_final_fixes("ИИ-сотрудники_Измеримый_ROI_v3_draft.pdf", "ИИ-сотрудники_Измеримый_ROI_final.pdf")
