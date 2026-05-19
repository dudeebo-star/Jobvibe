import re
from pathlib import Path

import fitz

SKILLS = [
    "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust", "kotlin", "swift",
    "react", "vue", "angular", "next.js", "node", "django", "flask", "fastapi", "spring", "dotnet",
    "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "aws", "azure", "gcp",
    "docker", "kubernetes", "terraform", "git", "ci/cd", "jenkins", "github actions",
    "machine learning", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch",
    "pandas", "numpy", "scikit-learn", "data analysis", "power bi", "tableau",
    "agile", "scrum", "rest", "graphql", "microservices", "linux", "bash",
    "html", "css", "tailwind", "figma", "excel", "communication", "leadership",
]

TITLE_RE = re.compile(
    r"(?i)(?:senior|junior|lead|principal|staff)?\s*"
    r"(?:software|full[- ]?stack|front[- ]?end|back[- ]?end|data|ml|devops|cloud|mobile|web)\s*"
    r"(?:engineer|developer|architect|analyst|scientist|intern)",
)


def pdf_to_text(path: Path) -> str:
    doc = fitz.open(path)
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    return text.strip()


def match_skills(text: str, pool: list[str] | None = None) -> list[str]:
    pool = pool or SKILLS
    lower = text.lower()
    return sorted({s for s in pool if s in lower})


def extract_titles(text: str) -> list[str]:
    seen: list[str] = []
    for m in TITLE_RE.finditer(text):
        t = m.group(0).strip()
        if t.lower() not in {x.lower() for x in seen}:
            seen.append(t)
    return seen[:6]


def years_experience(text: str) -> int | None:
    for pat in (
        r"(\d+)\+?\s*years?\s+(?:of\s+)?experience",
        r"experience[:\s]+(\d+)\+?\s*years?",
    ):
        m = re.search(pat, text, re.I)
        if m:
            return int(m.group(1))
    return None


def analyse_resume(pdf_path: Path, job_text: str) -> dict:
    raw = pdf_to_text(pdf_path)
    skills = match_skills(raw)
    job_skills = match_skills(job_text)
    return {
        "raw_excerpt": raw[:6000],
        "skills": skills,
        "job_skills": job_skills,
        "matched": sorted(set(skills) & set(job_skills)),
        "gaps": sorted(set(job_skills) - set(skills)),
        "titles": extract_titles(raw),
        "years": years_experience(raw),
    }
