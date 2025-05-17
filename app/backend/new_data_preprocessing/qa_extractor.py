import os
import json
from extract_excel import extract_from_excel
from extract_text_pdf import extract_from_text_or_pdf

def process_any_file(filepath, output_path="output_qas.json", skip_pages=2):
    ext = os.path.splitext(filepath)[1].lower()
    
    if ext == ".xlsx":
        qas_data = extract_from_excel(filepath, skip_sheets=skip_pages)
    elif ext in [".txt", ".pdf"]:
        qas_data = {"General": extract_from_text_or_pdf(filepath)}
    else:
        raise ValueError("Unsupported file type.")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(qas_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Q&A data extracted to {output_path}")

if __name__ == "__main__":
    process_any_file("C:/Users/HP/Desktop/LLM Project/dataset/NUST Bank-Product-Knowledge.xlsx", output_path="C:/Users/HP/Desktop/output_qas.json", skip_pages=2)