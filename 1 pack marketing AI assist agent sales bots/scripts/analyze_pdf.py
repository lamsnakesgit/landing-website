
import fitz

def analyze_pdf(path):
    doc = fitz.open(path)
    print(f"Analyzing {path} with {len(doc)} pages.")
    
    keywords = ["notebooklm", "Nextbot", "nextbot"]
    
    for page_num, page in enumerate(doc):
        # Search for text
        for keyword in keywords:
            text_instances = page.search_for(keyword)
            if text_instances:
                print(f"Found '{keyword}' on page {page_num + 1}:")
                for rect in text_instances:
                    print(f"  - Rect: {rect}")
        
        # Also print all text on the page to see if it's case-sensitive or hidden in blocks
        # text = page.get_text("text")
        # if "notebook" in text.lower() or "nextbot" in text.lower():
            # print(f"DEBUG Page {page_num+1} content snippet: {text[:200]}")

if __name__ == "__main__":
    analyze_pdf("ИИ-сотрудники_Измеримый_ROI_v2.pdf")
