
import fitz

def swap_last_slide(target_path, source_path, output_path):
    print(f"Target: {target_path}")
    print(f"Source: {source_path}")
    
    doc_target = fitz.open(target_path)
    doc_source = fitz.open(source_path)
    
    print(f"Original Target Pages: {len(doc_target)}")
    
    # 1. Remove last page from target
    # Pages are 0-indexed. Last page is len-1.
    last_page_idx = len(doc_target) - 1
    doc_target.delete_page(last_page_idx)
    print(f"Removed page {last_page_idx + 1} from target.")
    
    # 2. Get first page from source
    # We will insert the first page of source into target.
    # formatting: doc.insert_pdf(doc_source, from_page=0, to_page=0)
    doc_target.insert_pdf(doc_source, from_page=0, to_page=0)
    print("Appended first page of source to target.")
    
    print(f"New Page Count: {len(doc_target)}")
    
    doc_target.save(output_path)
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    target = "Интеллектуальный_отдел_продаж_24_7.pdf"
    source = "ИИ_Агенты_Продажи.pdf"
    output = "Интеллектуальный_отдел_продаж_UPDATED.pdf"
    
    swap_last_slide(target, source, output)
