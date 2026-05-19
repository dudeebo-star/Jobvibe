# JobVibe — AI Interview Platform

Resume analysis, live AI interviews, confidence tracking, and PDF reports.

## Run on GitHub (Codespaces)

Best for development and demos — runs entirely in your browser via GitHub.

1. **Push this repo to GitHub** (see [First-time setup](#first-time-setup) below).
2. On GitHub, open the repo → **Code** → **Codespaces** → **Create codespace on main**.
3. Add your API key (either way):
   - **Repo secret (recommended):** Settings → Secrets and variables → Codespaces → **New secret** → name `DEEPSEEK_API_KEY`, paste your key from [platform.deepseek.com](https://platform.deepseek.com).
   - Or edit `.env` in the Codespace and set `DEEPSEEK_API_KEY=...`.
4. In the Codespace terminal:
   ```bash
   python run.py
   ```
5. When port **8000** is forwarded, open the URL GitHub shows (or the **Ports** tab → globe icon).

Camera and microphone work in the forwarded HTTPS URL for the full interview flow.

## Deploy from GitHub (public URL)

Use [Render](https://render.com) with this repo:

1. **New** → **Blueprint** → connect your GitHub repo (uses `render.yaml`).
2. Set **DEEPSEEK_API_KEY** in the Render dashboard when prompted.
3. Deploy; open the `.onrender.com` URL.

> Sessions are stored in memory — they reset when the service restarts. Fine for demos; not for production persistence.

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
copy .env.example .env          # then set DEEPSEEK_API_KEY
python run.py
```

Open http://127.0.0.1:8000

## First-time setup (push to GitHub)

```bash
git init
git add .
git commit -m "Initial commit: JobVibe"
git branch -M main
git remote add origin https://github.com/dudeebo-star/jobvibe.git
git push -u origin main
```

Create the empty repo on GitHub first (**New repository**), then use your repo URL in `git remote add`.

## Modules

- Resume analyser + question bank (PyMuPDF + DeepSeek)
- Live AI interview (Web Speech API + DeepSeek)
- Confidence tracking (MediaPipe Face Mesh)
- Scoring + PDF report (FPDF2)
