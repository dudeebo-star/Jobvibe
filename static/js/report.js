const id = new URLSearchParams(location.search).get("id");
const raw = id && sessionStorage.getItem(`jobvibe_report_${id}`);
if (!raw) {
  document.querySelector("h1").textContent = "No report — finish an interview first.";
} else {
  const data = JSON.parse(raw);
  const scores = data.scores || {};
  const summary = data.summary || {};
  const vision = data.vision || [];

  const rec = summary.recommendation || "N/A";
  const badge = document.getElementById("rec-badge");
  badge.textContent = rec;
  badge.className = "badge-rec " + (
    /no hire/i.test(rec) ? "no" : /maybe/i.test(rec) ? "maybe" : "hire"
  );

  const tiles = [
    { label: "Composite score", value: scores.composite, hero: true },
    { label: "Relevance (40%)", value: scores.relevance },
    { label: "Communication (25%)", value: scores.communication },
    { label: "Confidence (20%)", value: scores.confidence },
    { label: "Technical (15%)", value: scores.technical },
  ];

  document.getElementById("scores").innerHTML = tiles.map((t) => `
    <div class="score-tile${t.hero ? " hero" : ""}">
      <div class="num">${t.value ?? "—"}</div>
      <div>${t.label}</div>
    </div>`).join("");

  document.getElementById("summary").textContent = summary.summary || "";
  document.getElementById("strengths").innerHTML = (summary.strengths || []).map((s) => `<li>${s}</li>`).join("");
  document.getElementById("improve").innerHTML = (summary.improvements || []).map((s) => `<li>${s}</li>`).join("");
  document.getElementById("pdf").href = `/api/sessions/${id}/report.pdf`;

  drawChart(vision);
}

function drawChart(samples) {
  const canvas = document.getElementById("chart");
  if (!canvas || !samples.length) return;

  const ctx = canvas.getContext("2d");
  const w = canvas.parentElement.clientWidth;
  const h = 130;
  const dpr = devicePixelRatio || 1;
  canvas.width = w * dpr;
  canvas.height = h * dpr;
  canvas.style.width = w + "px";
  canvas.style.height = h + "px";
  ctx.scale(dpr, dpr);

  const pad = 20;
  const maxT = Math.max(...samples.map((s) => s.t), 1);
  const pts = samples.map((s) => ({
    x: pad + (s.t / maxT) * (w - pad * 2),
    y: h - pad - (s.overall / 100) * (h - pad * 2),
  }));

  ctx.strokeStyle = "#0d9488";
  ctx.lineWidth = 2;
  ctx.beginPath();
  pts.forEach((p, i) => (i ? ctx.lineTo(p.x, p.y) : ctx.moveTo(p.x, p.y)));
  ctx.stroke();
}
