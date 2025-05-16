import json

# Load the existing QA pairs
with open("C:/Users/HP/Desktop/LLM Project/preprocessing/qa_pairs.json", "r", encoding="utf-8") as f:
    qa_pairs_data = json.load(f)

# Load the account-based QAs
with open("C:/Users/HP/Desktop/LLM Project/preprocessing/account_qas.json", "r", encoding="utf-8") as f:
    acc_qas_data = json.load(f)

# Append new QAs from acc_qas.json
for acc_key, acc_entry in acc_qas_data.items():
    title = acc_entry.get("title", "").strip()
    for qa in acc_entry.get("qas", []):
        question = qa.get("question", "").strip()
        answer_list = qa.get("answer", [])
        
        if question and isinstance(answer_list, list):
            joined_answer = " ".join(str(ans).strip() for ans in answer_list if ans)
            if joined_answer:  # Only append if answer is not empty
                full_question = f"{question} for {title}"
                qa_pairs_data["questions"].append({
                    "question": full_question,
                    "answer": joined_answer
                })

# Save the updated QA pairs
with open("C:/Users/HP/Desktop/LLM Project/preprocessing/qa_pairs.json", "w", encoding="utf-8") as f:
    json.dump(qa_pairs_data, f, indent=4, ensure_ascii=False)
