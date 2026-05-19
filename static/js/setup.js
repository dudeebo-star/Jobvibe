const form = document.getElementById("form");
const msg = document.getElementById("msg");
const insights = document.getElementById("insights");
const body = document.getElementById("insight-body");
const go = document.getElementById("go");
let sessionId = null;

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  go.disabled = true;
  msg.textContent = "Parsing resume and generating questions with DeepSeek…";

  const fd = new FormData();
  fd.append("resume", document.getElementById("pdf").files[0]);
  fd.append("job_description", document.getElementById("job").value);
  fd.append("candidate_name", document.getElementById("name").value);
  fd.append("role_title", document.getElementById("role").value);

  try {
    const res = await fetch("/api/sessions", { method: "POST", body: fd });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed");

    sessionId = data.id;
    sessionStorage.setItem("jobvibe_id", sessionId);
    sessionStorage.setItem("jobvibe_opening", data.opening);

    const r = data.resume;
    const c = data.bank_counts;
    body.innerHTML = `
      <p class="hint">Matched skills</p>
      <div class="pills">${(r.matched || []).map((s) => `<span class="pill">${s}</span>`).join("") || "<span class='pill warn'>None detected</span>"}</div>
      <p class="hint">Gaps vs job</p>
      <div class="pills">${(r.gaps || []).map((s) => `<span class="pill warn">${s}</span>`).join("") || "<span class='pill'>None</span>"}</div>
      <p class="hint">Question bank: ${c.technical} technical · ${c.behavioural} behavioural · ${c.cultural} cultural</p>`;

    insights.hidden = false;
    msg.textContent = "Ready — enter the interview room when you are set.";
  } catch (err) {
    msg.textContent = err.message;
  } finally {
    go.disabled = false;
  }
});

document.getElementById("enter").addEventListener("click", () => {
  if (sessionId) location.href = `/static/room.html?id=${sessionId}`;
});
