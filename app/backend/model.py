import os
import argparse
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from huggingface_hub import login
import shutil

def download_model(model_name: str, model_path: str):
    if os.path.exists(model_path) and os.path.isdir(model_path):
        print(f"Model already exists at '{model_path}', skipping download.")
        return

    print(f"Downloading model '{model_name}' to '{model_path}'...")
    try:
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            torch_dtype=torch.float16
        )
        tokenizer = AutoTokenizer.from_pretrained(model_name)

        os.makedirs(model_path, exist_ok=True)
        tokenizer.save_pretrained(model_path)
        model.save_pretrained(model_path)

        print("Download complete.")
    except Exception as e:
        print(f"\nError downloading model: {e}")
        # Clean up partial download if any
        if os.path.exists(model_path):
            print(f"Cleaning up partially downloaded files in '{model_path}'...")
            shutil.rmtree(model_path)
        raise SystemExit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download a Hugging Face model if not already present.")
    parser.add_argument("--model_path", type=str, default=os.path.join("models", "Qwen", "Qwen1.5-1.8B-Chat"), help="Local directory to save the model.")
    args = parser.parse_args()
    hf_token = input("Enter your Hugging Face token: ").strip()
    login(hf_token)

    download_model("Qwen/Qwen1.5-1.8B-Chat", args.model_path)
