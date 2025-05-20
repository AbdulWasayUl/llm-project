from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
import docx
from PyPDF2 import PdfReader
from typing import List, Tuple
import torch
import faiss
import json
import os
import tempfile
import shutil
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM
from backend.new_data_preprocessing.extract_excel import extract_from_excel
from backend.new_data_preprocessing.extract_text_pdf import extract_from_text_or_pdf
import re
import logging


app = FastAPI()

# ==== Load RAG components ====
MODEL_NAME = "models/Qwen/Qwen1.5-1.8B-Chat"
INDEX_PATH = "bank-data_index.faiss"
DOCS_PATH = "bank-data.json"
EMBEDDING_DIR = "embedding"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# Load model and tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, device_map="auto", torch_dtype=torch.float16)

# Load FAISS index
index = faiss.read_index(INDEX_PATH)

# Load documents
with open(DOCS_PATH, "r", encoding="utf-8") as f:
    documents = json.load(f)

# Load encoder for query embedding
embedding_model = SentenceTransformer(os.path.join(EMBEDDING_DIR, EMBEDDING_MODEL_NAME))

# ==== Helper Functions ====
def retrieve(query: str, top_k: int = 3) -> List[str]:
    query_embedding = embedding_model.encode([query])
    _, indices = index.search(np.array(query_embedding).astype("float32"), top_k)
    return [documents[str(i)] for i in indices[0] if str(i) in documents]

def build_prompt(query: str, context_docs: List[str]) -> str:
    context = "\n---\n".join(context_docs)
    return (
         f"<|system|>>\nYou are a helpful banking assistant. You are provided with NUST Bank FAQ relevant to the query of the user. Your job is to give direct answers according to the provided context. NOT from your own knowledge. Give the answer in a user friendly manner. Keep answers short. No explanation\n"
        f"Context:\n\n{context}\n"
        f"---\n</s>"
        f"<|user|>\n {query}\n</s>"
        f"<|assistant|>"
    )

def generate_answer(query: str) -> str:
    context_docs = retrieve(query)
    prompt = build_prompt(query, context_docs)
    input_ids = tokenizer(prompt, return_tensors="pt", truncation=True).input_ids.to(model.device)
    output_ids = model.generate(input_ids, max_new_tokens=200, temperature=0.7)
    answer = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return answer.split("<|assistant|>")[-1].strip()

def build_documents(qa_list):
    return [f"Q: {item['question']}\nA: {item['answer']}" for item in qa_list if item.get("question") and item.get("answer")]

DISALLOWED_KEYWORDS = [
    "bomb", "hack", "bypass", "cheat", "illegal", "violence", "kill", 
    "porn", "dark web", "jailbreak", "prompt injection"
]

def filter_prompt(prompt: str) -> Tuple[bool, str]:
    lowered = prompt.lower()
    for word in DISALLOWED_KEYWORDS:
        if word in lowered:
            return False, f"❌ This request violates our usage policy: contains disallowed term '{word}'."
    
    if re.search(r"(ignore previous|pretend|act as|you are no longer bound)", prompt, re.IGNORECASE):
        return False, "⚠️ Prompt injection attempt detected. Request denied."

    return True, prompt

def sanitize_output(text: str, query:str) -> str:
    if any(bad in text.lower() for bad in DISALLOWED_KEYWORDS):
        log_violation(query, "Response contains disallowed content: " + text)
        return "⚠️ Response filtered due to policy violation."
    return text

logging.basicConfig(filename="security.log", level=logging.WARNING)

def log_violation(prompt: str, reason: str):
    logging.warning(f"Blocked prompt: '{prompt}' | Reason: {reason}")

# ==== API Interface ====
class QueryRequest(BaseModel):
    query: str

@app.post("/ask")
async def ask_question(req: QueryRequest):
    allowed, result = filter_prompt(req.query)
    if not allowed:
        log_violation(req.query, result)
        raise HTTPException(status_code=403, detail=result)
    
    response = generate_answer(req.query)
    return {"response": sanitize_output(response, req.query)}


@app.post("/add_data")
async def add_data(
    file: UploadFile = File(...),
    is_qa: bool = Form(...)
):
    # Save uploaded file temporarily
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in [".xlsx", ".pdf", ".txt"]:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use .xlsx, .pdf, or .txt")
    
    temp_dir = tempfile.mkdtemp()
    temp_file_path = os.path.join(temp_dir, file.filename)
    
    try:
        # Save file
        with open(temp_file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # Process file based on type
        if is_qa:
            # Process as QA pairs
            if file_ext == ".xlsx":
                qa_data = extract_from_excel(temp_file_path, skip_sheets=2)
            
            elif file_ext in [".txt", ".pdf"]:
                qa_data = extract_from_text_or_pdf(temp_file_path)
            else:
                raise ValueError("Unsupported file type")
            
            qa_pairs = qa_data.get("questions", [])
            new_docs = build_documents(qa_pairs)

        else:
            # Process as raw context
            if file_ext == ".txt":
                with open(temp_file_path, "r", encoding="utf-8") as f:
                    text = f.read()
            elif file_ext == ".pdf":
                reader = PdfReader(temp_file_path)
                text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
            elif file_ext == ".docx":
                doc = docx.Document(temp_file_path)
                text = "\n".join(para.text for para in doc.paragraphs if para.text.strip())
            else:
                raise ValueError("Unsupported file type for context-only mode")

            # Clean and split into paragraphs
            new_docs = [p.strip() for p in text.split("\n") if len(p.strip()) > 0]

        
        start_index = len(documents)

        # Append new docs
        for i, doc in enumerate(new_docs):
            documents[str(start_index + i)] = doc

        with open(DOCS_PATH, "w", encoding="utf-8") as f:
            json.dump(documents, f, indent=2, ensure_ascii=False)
        embeddings = embedding_model.encode(new_docs, convert_to_numpy=True)
        index.add(embeddings)
        faiss.write_index(index, INDEX_PATH)
            
        
        return {
            "success": True,
            "message": f"Successfully processed file '{file.filename}'"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)