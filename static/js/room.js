import { bindSpeech } from "./speech.js";
import { VisionTracker } from "./vision.js";

const id = new URLSearchParams(location.search).get("id") || sessionStorage.getItem("jobvibe_id");
if (!id) location.href = "/";

const feed = document.getElementById("feed");
const question = document.getElementById("question");
const answer = document.getElementById("answer");
const status = document.getElementById("status");
const send = document.getElementById("send");
const finish = document.getElementById("finish");

const speech = bindSpeech(answer, status, document.getElementById("mic"));
let vision;

function esc(s) {
  const d = document.createElement("div");
  d.textContent = s;
  return d.innerHTML;
}

function addMsg(speaker, text) {
  const el = document.createElement("div");
  el.className = `msg ${speaker}`;
  el.innerHTML = `<div class="who">${speaker === "ai" ? "Interviewer" : "You"}</div><div>${esc(text)}</div>`;
  feed.appendChild(el);
  feed.scrollTop = feed.scrollHeight;
}

async function postVision(sample) {
  try {
    await fetch(`/api/sessions/${id}/vision`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(sample),
    });
  } catch (_) {}
}

(async () => {
  const opening = sessionStorage.getItem("jobvibe_opening");
  if (opening) {
    question.textContent = opening;
    addMsg("ai", opening);
  }

  vision = new VisionTracker(document.getElementById("cam"), postVision);
  await vision.start();
})();

send.addEventListener("click", async () => {
  const text = answer.value.trim();
  if (!text) {
    status.textContent = "Enter or speak an answer first.";
    return;
  }
  speech.stop();
  send.disabled = true;
  addMsg("candidate", text);

  try {
    const res = await fetch(`/api/sessions/${id}/answer`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Error");

    answer.value = "";
    question.textContent = data.next;
    addMsg("ai", data.next);
    status.textContent = data.source === "clarify" ? "Please add more detail." : "";
  } catch (e) {
    status.textContent = e.message;
  } finally {
    send.disabled = false;
  }
});

finish.addEventListener("click", async () => {
  speech.stop();
  finish.disabled = true;
  status.textContent = "Scoring and writing summary…";

  try {
    const res = await fetch(`/api/sessions/${id}/finish`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ vision: vision?.all() || [] }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Error");
    sessionStorage.setItem(`jobvibe_report_${id}`, JSON.stringify(data));
    location.href = `/static/report.html?id=${id}`;
  } catch (e) {
    status.textContent = e.message;
    finish.disabled = false;
  }
});
