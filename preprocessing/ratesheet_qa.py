import json

def build_answer(obj_list):
    parts = []
    for item in obj_list:
        if isinstance(item, dict):
            fields = []
            for key, value in item.items():
                val = value if value is not None else "None"
                fields.append(f"{key} is {val}")
            parts.append(", ".join(fields))
    return ". ".join(parts) + "."

def generate_qa_pairs(ratelist_path):
    with open(ratelist_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    qa_pairs = []

    # Savings Accounts
    for account, details in data.get("Savings Accounts", {}).items():
        question = f"What are the profit payment and profit rate for {account} Savings Account?"
        answer = build_answer(details)
        qa_pairs.append({"question": question, "answer": answer})

    # Term Deposits
    for deposit, details in data.get("Term Deposits", {}).items():
        question = f"What are the tenor, payout and profit rate for {deposit} Term Deposit?"
        answer = build_answer(details)
        qa_pairs.append({"question": question, "answer": answer})

    return {"questions": qa_pairs}

# Write to JSON
qa_data = generate_qa_pairs("C:/Users/HP/Desktop/LLM Project/preprocessing/ratelist.json")
with open("C:/Users/HP/Desktop/LLM Project/preprocessing/qa_pairs.json", "w", encoding="utf-8") as f:
    json.dump(qa_data, f, indent=4)
