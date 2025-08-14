import re

AFTER_BEFORE_PAT = re.compile(
    r'\b(\d+)\s*(?:st|nd|rd|th)?\s*(?:number|digit)\s*(after|before)\s*(\d+)\b',
    re.IGNORECASE
)

def classify_question(question: str) -> str:
    q = question.lower().strip()

    #Math by operators or spelled operations
    if re.search(r'\d+\s*[\+\-\*/]\s*\d+', q) or \
       re.search(r'\d+\s*(plus|minus|times|multiplied by|divided by|over)\s*\d+', q):
        return "math"

    #Math by word patterns (nth number/digit after/before N)
    if AFTER_BEFORE_PAT.search(q):
        return "math"

    #Math cue words + numbers (e.g., "evaluate 2x+3", "sum of 3 and 5")
    if re.search(r'\b(sum|difference|product|quotient|evaluate|compute|solve|square|cube)\b', q) and re.search(r'\d', q):
        return "math"

    #Opinion cues
    if any(w in q for w in ["think", "opinion", "believe", "feel", "should", "better", "recommend"]):
        return "opinion"

    return "factual"


def respond(question: str) -> str:
    category = classify_question(question)

    if category == "math":
        # Handle the 'nth number/digit after/before N' pattern
        m = AFTER_BEFORE_PAT.search(question)
        if m:
            n = int(m.group(1))
            direction = m.group(2).lower()
            base = int(m.group(3))
            result = base + n if direction == "after" else base - n
            return f"The {n}{ordinal_suffix(n)} number after/before {base} is {result}."
        # Fallback: try safe eval on simple expressions
        expr = re.sub(r'[^0-9\+\-\*/\.\(\) ]', '', question)
        try:
            if any(op in expr for op in "+-*/"):
                return f"The answer is: {eval(expr)}"
        except Exception:
            pass
        return "I detected a math question, but I couldn't compute it from the wording."

    if category == "opinion":
        return "This looks opinion-based; the answer can vary by preference and context."

    return "This appears to be a factual question; you may need a reliable source or database for a precise answer."


def ordinal_suffix(n: int) -> str:
    if 10 <= n % 100 <= 20: return "th"
    return {1:"st",2:"nd",3:"rd"}.get(n % 10, "th")


if __name__ == "__main__":
    q = input("Enter your question: ")
    print(respond(q))
