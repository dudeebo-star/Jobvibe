JobVibe — AI Interview Platform
================================

Quick start
-----------
1. Install Python 3.10+ from https://python.org
2. Open a terminal in this folder
3. Run:
     python -m venv .venv
     .venv\Scripts\activate
     pip install -r requirements.txt
     copy .env.example .env
4. Edit .env and set DEEPSEEK_API_KEY (from https://platform.deepseek.com)
5. Run:
     python run.py
6. Open http://127.0.0.1:8000 in your browser

Modules
-------
- Resume analyser + question bank (PyMuPDF + DeepSeek)
- Live AI interview (Web Speech API + DeepSeek)
- Confidence tracking (MediaPipe Face Mesh)
- Scoring + PDF report (FPDF2)

Need camera and microphone for the full experience.
