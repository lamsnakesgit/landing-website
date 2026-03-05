
import fitz

def investigate_pdf(path):
    doc = fitz.open(path)
    print(f"Investigating {path}...")
    
    for i, page in enumerate(doc):
        text = page.get_text("text")
        print(f"--- Page {i+1} ---")
        print(text[:500])  # Print first 500 chars to see if text exists
        
        # Check for images
        images = page.get_images(full=True)
        if images:
            print(f"  Found {len(images)} images on page {i+1}")

if __name__ == "__main__":
    investigate_pdf("ИИ-сотрудники_Измеримый_ROI_v2.pdf")
