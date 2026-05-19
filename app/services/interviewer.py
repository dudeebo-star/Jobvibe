from app.config import SHORT_ANSWER_WORDS
from app.services.llm import complete, parse_json

SYSTEM = """You conduct a live job interview. Return ONLY JSON:
{"question": "...", "source": "bank"|"follow_up"|"clarify", "category": "technical"|"behavioural"|"cultural"}

Rules:
- Under 25 words in the last answer → clarify (source: clarify)
- Otherwise use unused bank questions or smart follow-ups
- Never repeat a question already asked
- One question, conversational tone, max 2 sentences
- Order: technical → behavioural → cultural"""


async def next_question(job: str, bank: dict, history: list[dict], answer: str) -> dict:
    words = len(answer.split())
    if words < SHORT_ANSWER_WORDS and answer.strip():
        cat = "technical"
        for turn in reversed(history):
            if turn.get("speaker") == "ai":
                cat = turn.get("category", cat)
                break
        return {
            "question": "Could you expand on that with a concrete example, tools you used, and the outcome?",
            "source": "clarify",
            "category": cat,
        }

    asked = [t["text"] for t in history if t.get("speaker") == "ai"]
    transcript = "\n".join(
        f"{'Interviewer' if t['speaker'] == 'ai' else 'Candidate'}: {t['text']}"
        for t in history[-14:]
    )

    try:
        raw = await complete([
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": (
                f"Job:\n{job[:3500]}\n\nBank:\n{bank}\n\nAsked:\n{asked}\n\n"
                f"Transcript:\n{transcript}\n\nLatest answer:\n{answer}"
            )},
        ], temperature=0.75, max_tokens=400)
        out = parse_json(raw)
        if out.get("question"):
            return out
    except Exception:
        pass

    return _pick_from_bank(bank, asked)


def _pick_from_bank(bank: dict, asked: list[str]) -> dict:
    for cat in ("technical", "behavioural", "cultural"):
        for item in bank.get(cat, []):
            q = item.get("question", "")
            if q and q not in asked:
                return {"question": q, "source": "bank", "category": cat}
    return {
        "question": "Anything else you would like us to know about your fit for this role?",
        "source": "follow_up",
        "category": "cultural",
    }
