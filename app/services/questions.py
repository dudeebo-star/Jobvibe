from app.services.llm import LLMError, complete, parse_json
from app.services.resume import match_skills, SKILLS

PROMPT = """You are a senior interviewer. Build a question bank from the resume summary and job description.

Return ONLY JSON:
{
  "technical": [{"question": "...", "relevance": 1-10, "skills": ["..."]}],
  "behavioural": [{"question": "...", "relevance": 1-10, "star_tip": "..."}],
  "cultural": [{"question": "...", "relevance": 1-10}]
}

- 6 technical, 5 behavioural (STAR), 4 cultural
- Sort each list by relevance descending
- Tie questions to this candidate and role"""


async def build_bank(resume: dict, job: str) -> dict:
    payload = {
        "skills": resume["skills"][:20],
        "matched": resume["matched"],
        "gaps": resume["gaps"],
        "titles": resume["titles"],
        "years": resume["years"],
    }
    try:
        raw = await complete([
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": f"Resume:\n{payload}\n\nJob:\n{job[:5000]}"},
        ], temperature=0.6)
        bank = parse_json(raw)
    except (LLMError, Exception):
        bank = _offline_bank(resume, job)

    for key in ("technical", "behavioural", "cultural"):
        bank.setdefault(key, [])
        bank[key].sort(key=lambda x: x.get("relevance", 0), reverse=True)
    return bank


def _offline_bank(resume: dict, job: str) -> dict:
    focus = resume["matched"] or resume["skills"][:4]
    job_kw = match_skills(job, SKILLS)[:4]
    technical = [
        {"question": f"Walk me through a project where you used {s}. What was your role?", "relevance": 9 - i, "skills": [s]}
        for i, s in enumerate(focus[:5])
    ]
    for kw in job_kw:
        if len(technical) < 6:
            technical.append({"question": f"How would you use {kw} in this position?", "relevance": 7, "skills": [kw]})
    return {
        "technical": technical,
        "behavioural": [
            {"question": "Describe a time you missed a deadline. What happened and what did you learn?", "relevance": 9, "star_tip": "STAR"},
            {"question": "Tell me about resolving a disagreement on your team.", "relevance": 8, "star_tip": "STAR"},
            {"question": "Give an example of leading without formal authority.", "relevance": 7, "star_tip": "STAR"},
        ],
        "cultural": [
            {"question": "What kind of manager brings out your best work?", "relevance": 8},
            {"question": "How do you prefer to receive feedback?", "relevance": 7},
        ],
    }


def first_question(bank: dict) -> str:
    for cat in ("technical", "behavioural", "cultural"):
        items = bank.get(cat, [])
        if items:
            return items[0]["question"]
    return "Introduce yourself and why you are interested in this role."
