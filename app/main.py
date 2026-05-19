import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from app.config import ROOT, UPLOADS
from app.services.interviewer import next_question
from app.services.pdf_report import generate_pdf
from app.services.questions import build_bank, first_question
from app.services.resume import analyse_resume
from app.services.scoring import (
    ai_summary,
    communication_score,
    composite,
    confidence_score,
    relevance_score,
    technical_score,
)

app = FastAPI(title="JobVibe", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

STATIC = ROOT / "static"
sessions: dict[str, dict] = {}


@app.get("/")
def home():
    return FileResponse(STATIC / "index.html")


@app.post("/api/sessions")
async def create_session(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    candidate_name: str = Form("Candidate"),
    role_title: str = Form("Open Role"),
):
    if not resume.filename or not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Upload a PDF resume.")

    sid = str(uuid.uuid4())
    path = UPLOADS / f"{sid}.pdf"
    path.write_bytes(await resume.read())

    resume_data = analyse_resume(path, job_description)
    bank = await build_bank(resume_data, job_description)
    opening = first_question(bank)

    sessions[sid] = {
        "name": candidate_name,
        "role": role_title,
        "job": job_description,
        "resume": resume_data,
        "bank": bank,
        "history": [{"speaker": "ai", "text": opening, "category": "technical"}],
        "answers": [],
        "vision": [],
    }

    return {
        "id": sid,
        "resume": {
            "skills": resume_data["skills"][:15],
            "matched": resume_data["matched"],
            "gaps": resume_data["gaps"],
            "titles": resume_data["titles"],
            "years": resume_data["years"],
        },
        "bank_counts": {k: len(bank.get(k, [])) for k in ("technical", "behavioural", "cultural")},
        "opening": opening,
    }


@app.get("/api/sessions/{sid}")
def get_session(sid: str):
    s = sessions.get(sid)
    if not s:
        raise HTTPException(404, "Session not found")
    return {"name": s["name"], "history": s["history"]}


@app.post("/api/sessions/{sid}/answer")
async def post_answer(sid: str, body: dict):
    s = sessions.get(sid)
    if not s:
        raise HTTPException(404, "Session not found")

    text = (body.get("text") or "").strip()
    if not text:
        raise HTTPException(400, "Empty answer")

    cat = s["history"][-1].get("category", "technical") if s["history"] else "technical"
    s["history"].append({"speaker": "candidate", "text": text, "category": cat})
    s["answers"].append(text)

    nxt = await next_question(s["job"], s["bank"], s["history"], text)
    s["history"].append({
        "speaker": "ai",
        "text": nxt["question"],
        "category": nxt.get("category", "technical"),
        "source": nxt.get("source"),
    })

    return {
        "words": len(text.split()),
        "next": nxt["question"],
        "source": nxt.get("source"),
        "category": nxt.get("category"),
    }


@app.post("/api/sessions/{sid}/vision")
def post_vision(sid: str, body: dict):
    s = sessions.get(sid)
    if not s:
        raise HTTPException(404, "Session not found")
    s["vision"].append({
        "t": body.get("t", 0),
        "eye": body.get("eye", 0),
        "stable": body.get("stable", 0),
        "calm": body.get("calm", 0),
        "overall": body.get("overall", 0),
    })
    return {"ok": True}


@app.post("/api/sessions/{sid}/finish")
async def finish(sid: str, body: dict | None = None):
    s = sessions.get(sid)
    if not s:
        raise HTTPException(404, "Session not found")

    body = body or {}
    if body.get("vision"):
        s["vision"] = body["vision"]

    scores = {
        "relevance": round(relevance_score(s["answers"], s["job"]), 1),
        "communication": round(communication_score(s["answers"]), 1),
        "confidence": round(confidence_score(s["vision"]), 1),
        "technical": round(
            technical_score(s["answers"], s["resume"]["skills"], s["resume"]["job_skills"]), 1
        ),
    }
    scores["composite"] = composite(
        scores["relevance"], scores["communication"], scores["confidence"], scores["technical"]
    )

    summary = await ai_summary(s["job"], s["resume"], s["history"], scores)
    s["scores"] = scores
    s["summary"] = summary

    return {
        "scores": scores,
        "summary": summary,
        "vision": s["vision"],
        "history": s["history"],
    }


@app.get("/api/sessions/{sid}/report.pdf")
def download_pdf(sid: str):
    s = sessions.get(sid)
    if not s or "scores" not in s:
        raise HTTPException(404, "Finish the interview first.")
    pdf = generate_pdf(s["name"], s["role"], s["scores"], s["summary"], s["vision"])
    return Response(
        pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="jobvibe-{sid[:8]}.pdf"'},
    )


app.mount("/static", StaticFiles(directory=STATIC), name="static")
