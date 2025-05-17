import re

QUESTION_WORD_REGEX = re.compile(
    r"(?i)^\s*(is|please|what|how|when|where|why|are|can|do|does|shall|should|could|would|will|who|which)\b.*\.$"
)

def is_question(text):
    if not isinstance(text, str):
        return False
    stripped = text.strip()
    if stripped.endswith("?"):
        return True
    return bool(QUESTION_WORD_REGEX.match(stripped))

def clean_answer_list(answer_list):
    cleaned = []
    i = 0
    while i < len(answer_list):
        item = answer_list[i]
        if (
            isinstance(item, str) and item.strip() == "Profit Payment"
            and i + 1 < len(answer_list)
            and isinstance(answer_list[i + 1], str)
            and answer_list[i + 1].strip() == "Profit Rate"
        ):
            i += 5
            continue
        if item is not None:
            cleaned.append(str(item).strip())
        i += 1
    return cleaned