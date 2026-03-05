
import fitz

def extract_page_as_png(pdf_path, page_num, output_path):
    doc = fitz.open(pdf_path)
    if page_num < len(doc):
        # High DPI for quality
        pix = doc[page_num].get_pixmap(dpi=300) 
        pix.save(output_path)
        print(f"Saved Page {page_num+1} to {output_path}")
    else:
        print("Page not found")

if __name__ == "__main__":
    # Page 10 is index 9. Using v2 because it's clean (no white box).
    extract_page_as_png("ИИ-сотрудники_Измеримый_ROI_v2.pdf", 9, "slide_10_clean.png")
