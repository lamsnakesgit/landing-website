
import fitz


def create_grid_pdf(input_path, output_path):
    doc = fitz.open(input_path)
    print(f"Processing {len(doc)} pages...")

    for i in range(len(doc)):
        page = doc[i]
        shape = page.new_shape()
        
        # Page dimensions
        width = page.rect.width
        height = page.rect.height
        
        step_x = 50
        step_y = 50
        
        # Draw vertical lines
        for x in range(0, int(width), step_x):
            shape.draw_line((x, 0), (x, height))
            shape.insert_text((x + 2, 10), f"X{x}", fontsize=8, color=(1, 0, 0))

        # Draw horizontal lines
        for y in range(0, int(height), step_y):
            shape.draw_line((0, y), (width, y))
            shape.insert_text((2, y + 10), f"Y{y}", fontsize=8, color=(1, 0, 0))
        
        # Draw nice grid labels in cells
        for y in range(0, int(height), step_y):
            for x in range(0, int(width), step_x):
                shape.insert_text((x + 5, y + 25), f"{x},{y}", fontsize=6, color=(0, 0, 1))

        shape.finish(color=(1, 0, 0), width=0.5)
        shape.commit()
    
    doc.save(output_path)
    print(f"Saved full grid to {output_path}")

if __name__ == "__main__":
    create_grid_pdf("ИИ-сотрудники_Измеримый_ROI_v2.pdf", "debug_grid_full.pdf")


