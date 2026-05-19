from datetime import datetime

from fpdf import FPDF

from app.config import WEIGHTS


def generate_pdf(name: str, role: str, scores: dict, summary: dict, vision: list[dict]) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=14)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "JobVibe — Performance Report", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(4)

    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Candidate: {name}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Role: {role}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Date: {datetime.now():%Y-%m-%d %H:%M}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, f"Composite: {scores.get('composite', 0)}/100", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    for key, label in (
        ("relevance", "Answer relevance"),
        ("communication", "Communication"),
        ("confidence", "Confidence (vision)"),
        ("technical", "Technical accuracy"),
    ):
        w = int(WEIGHTS[key] * 100)
        pdf.cell(0, 6, f"  {label} ({w}%): {scores.get(key, 0):.1f}", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, f"Recommendation: {summary.get('recommendation', 'N/A')}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5, summary.get("summary", ""))
    pdf.ln(2)

    for title, key in (("Strengths", "strengths"), ("Improvements", "improvements")):
        items = summary.get(key, [])
        if items:
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 10)
            for item in items:
                pdf.cell(0, 5, f"  - {item}", new_x="LMARGIN", new_y="NEXT")

    if vision:
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 7, "Confidence samples (last 15)", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)
        for s in vision[-15:]:
            pdf.cell(
                0, 5,
                f"  t={s.get('t', 0)}s  eye={s.get('eye', 0):.0f}  "
                f"stable={s.get('stable', 0):.0f}  calm={s.get('calm', 0):.0f}  "
                f"overall={s.get('overall', 0):.0f}",
                new_x="LMARGIN", new_y="NEXT",
            )

    return bytes(pdf.output())
