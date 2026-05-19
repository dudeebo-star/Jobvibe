import re

from app.config import WEIGHTS
from app.services.llm import complete, parse_json
from app.services.resume import match_skills, SKILLS


def relevance_score(answers: list[str], job: str) -> float:
    if not answers:
        return 0.0
    job_kw = set(match_skills(job, SKILLS)) or set(re.findall(r"\b[a-z]{5,}\b", job.lower()))
    hits, total = 0, 0
    for a in answers:
        a_kw = set(match_skills(a, SKILLS)) | set(re.findall(r"\b[a-z]{5,}\b", a.lower()))
        hits += len(a_kw & job_kw)
        total += max(len(job_kw), 1)
    return min(100.0, hits / max(total, 1) * 120)


def communication_score(answers: list[str]) -> float:
    if not answers:
        return 0.0
    scores = []
    for a in answers:
        n = len(a.split())
        base = 35 if n < 15 else 58 if n < 35 else 82 if n < 70 else 94
        if re.search(r"\b(for example|specifically|resulted|achieved|implemented|led)\b", a, re.I):
            base = min(100, base + 8)
        scores.append(base)
    return sum(scores) / len(scores)


def technical_score(answers: list[str], resume_skills: list[str], job_skills: list[str]) -> float:
    target = set(job_skills) | set(resume_skills)
    if not target or not answers:
        return 50.0
    blob = " ".join(answers).lower()
    hit = sum(1 for s in target if s in blob)
    return min(100.0, hit / len(target) * 100)


def confidence_score(samples: list[dict]) -> float:
    if not samples:
        return 50.0
    return sum(s.get("overall", 50) for s in samples) / len(samples)


def composite(r: float, c: float, conf: float, t: float) -> float:
    return round(
        r * WEIGHTS["relevance"]
        + c * WEIGHTS["communication"]
        + conf * WEIGHTS["confidence"]
        + t * WEIGHTS["technical"],
        1,
    )


SUMMARY_PROMPT = """Summarise this interview for hiring managers. Return ONLY JSON:
{"summary": "2-3 paragraphs", "recommendation": "Strong Hire"|"Hire"|"Maybe"|"No Hire",
 "strengths": ["..."], "improvements": ["..."]}"""


async def ai_summary(job: str, resume: dict, history: list[dict], scores: dict) -> dict:
    transcript = "\n".join(
        f"{'Interviewer' if t['speaker'] == 'ai' else 'Candidate'}: {t['text']}"
        for t in history
    )
    try:
        raw = await complete([
            {"role": "system", "content": SUMMARY_PROMPT},
            {"role": "user", "content": (
                f"Scores: {scores}\nSkills: {resume.get('skills', [])}\n"
                f"Job:\n{job[:2500]}\n\nTranscript:\n{transcript[:7000]}"
            )},
        ], temperature=0.5, max_tokens=900)
        return parse_json(raw)
    except Exception:
        comp = scores.get("composite", 0)
        rec = "Hire" if comp >= 70 else "Maybe" if comp >= 55 else "No Hire"
        return {
            "summary": f"Overall score {comp}/100 across relevance, communication, confidence, and technical fit.",
            "recommendation": rec,
            "strengths": ["Completed the full interview"],
            "improvements": ["Add more metrics and specifics in answers"],
        }
