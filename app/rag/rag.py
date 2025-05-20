import os
import json
import argparse
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from huggingface_hub import login

EMBEDDING_DIR = "embedding"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
INDEX_PATH = "bank-data_index.faiss"
DOCS_PATH = "bank-data.json"

def load_or_download_model():
    model_path = os.path.join(EMBEDDING_DIR, EMBEDDING_MODEL_NAME)
    if not os.path.exists(model_path):
        print(f"Downloading model to '{model_path}'...")
        model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        model.save(model_path)
    else:
        print(f"Using cached model from '{model_path}'")
        model = SentenceTransformer(model_path)
    return model

def load_qa_data(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f).get("questions", [])

def build_documents(qa_list):
    return [f"Q: {item['question']}\nA: {item['answer']}" for item in qa_list if item.get("question") and item.get("answer")]

def load_or_create_index(dim):
    if os.path.exists(INDEX_PATH):
        print(f"Loading existing FAISS index from {INDEX_PATH}")
        return faiss.read_index(INDEX_PATH)
    print("Creating new FAISS index")
    return faiss.IndexFlatL2(dim)

def save_documents(documents):
    doc_map = {str(i): doc for i, doc in enumerate(documents)}
    with open(DOCS_PATH, "w", encoding="utf-8") as f:
        json.dump(doc_map, f, indent=2, ensure_ascii=False)
    print(f"Documents saved to '{DOCS_PATH}'")

def main(qa_path):
    print(f"Loading QA data from '{qa_path}'")
    qa_data = load_qa_data(qa_path)
    if not qa_data:
        print("No valid QA data found.")
        return

    documents = build_documents(qa_data)
    save_documents(documents)

    model = load_or_download_model()
    print("Generating embeddings...")
    embeddings = model.encode(documents, convert_to_numpy=True)

    dim = embeddings.shape[1]
    index = load_or_create_index(dim)
    index.add(embeddings)

    faiss.write_index(index, INDEX_PATH)
    print(f"FAISS index saved at '{INDEX_PATH}' with total entries: {index.ntotal}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build or append a FAISS index from QA pairs.")
    parser.add_argument("--qa_path", type=str, default=os.path.join(os.path.dirname(__file__), "qa_pairs.json"), help="Path to QA JSON file.")
    hf_token = input("Enter your Hugging Face token: ").strip()
    args = parser.parse_args()

    login(hf_token)

    main(args.qa_path)