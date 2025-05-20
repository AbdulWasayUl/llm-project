from backend.new_data_preprocessing.utils import is_question
from PyPDF2 import PdfReader

def extract_lines_from_txt(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.readlines()

def extract_lines_from_pdf(filepath):
    reader = PdfReader(filepath)
    lines = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            lines.extend(text.splitlines())
    return lines

def extract_qa_from_lines(lines, title="Text/PDF Content"):
    qas = []
    current_question = None
    current_answer = []

    for line in lines:
        stripped = line.strip()
        if is_question(stripped):
            if current_question and current_answer:
                qas.append({
                    "question": current_question,
                    "answer": current_answer
                })
            current_question = stripped
            current_answer = []
        elif current_question:
            if stripped:
                current_answer.append(stripped)

    if current_question and current_answer:
        qas.append({
            "question": current_question,
            "answer": " ".join(current_answer)
        })


    return {
        "questions": qas
    }

def extract_from_text_or_pdf(filepath):
    if filepath.lower().endswith(".txt"):
        lines = extract_lines_from_txt(filepath)
    elif filepath.lower().endswith(".pdf"):
        lines = extract_lines_from_pdf(filepath)
    else:
        raise ValueError("Unsupported file type for text/pdf extractor")
    return extract_qa_from_lines(lines)