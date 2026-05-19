export function bindSpeech(textarea, statusEl, micBtn) {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) {
    statusEl.textContent = "Speech not supported — type your answers.";
    micBtn.disabled = true;
    return { stop() {} };
  }

  const rec = new SR();
  rec.continuous = true;
  rec.interimResults = true;
  rec.lang = "en-US";
  let on = false;

  rec.onresult = (e) => {
    let fin = "";
    let interim = "";
    for (let i = e.resultIndex; i < e.results.length; i++) {
      const t = e.results[i][0].transcript;
      if (e.results[i].isFinal) fin += t;
      else interim += t;
    }
    if (fin) {
      const cur = textarea.value;
      textarea.value = (cur ? cur + " " : "") + fin.trim();
    }
    statusEl.textContent = interim ? `Listening: ${interim}` : on ? "Listening…" : "";
  };

  rec.onerror = () => stop();
  rec.onend = () => { if (on) rec.start(); };

  function start() {
    on = true;
    micBtn.classList.add("recording");
    micBtn.textContent = "Stop mic";
    rec.start();
  }

  function stop() {
    on = false;
    micBtn.classList.remove("recording");
    micBtn.textContent = "Mic";
    try { rec.stop(); } catch (_) {}
  }

  micBtn.addEventListener("click", () => (on ? stop() : start()));
  return { stop };
}
