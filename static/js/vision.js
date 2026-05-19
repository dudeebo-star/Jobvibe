export class VisionTracker {
  constructor(video, onTick) {
    this.video = video;
    this.onTick = onTick;
    this.samples = [];
    this.t0 = Date.now();
    this.lastNose = null;
    this.latest = null;
    this.els = {
      eye: document.getElementById("m-eye"),
      stable: document.getElementById("m-stable"),
      calm: document.getElementById("m-calm"),
      overall: document.getElementById("m-overall"),
    };
  }

  async start() {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: "user", width: 640, height: 480 },
      audio: false,
    });
    this.video.srcObject = stream;

    if (typeof FaceMesh === "undefined") return;

    const mesh = new FaceMesh({
      locateFile: (f) => `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${f}`,
    });
    mesh.setOptions({ maxNumFaces: 1, refineLandmarks: true, minDetectionConfidence: 0.5, minTrackingConfidence: 0.5 });
    mesh.onResults((r) => this._frame(r));

    const cam = new Camera(this.video, {
      onFrame: async () => mesh.send({ image: this.video }),
      width: 640,
      height: 480,
    });
    cam.start();
    setInterval(() => this._record(), 2000);
  }

  _frame(results) {
    const lm = results.multiFaceLandmarks?.[0];
    if (!lm) return;

    const nose = lm[1];
    const le = lm[33];
    const re = lm[263];
    const eyeMid = (le.x + re.x) / 2;
    const eye = Math.max(0, Math.min(100, (1 - Math.abs(nose.x - eyeMid) * 8) * 100));

    let stable = 85;
    if (this.lastNose) {
      const dx = nose.x - this.lastNose.x;
      const dy = nose.y - this.lastNose.y;
      stable = Math.max(0, Math.min(100, (1 - Math.hypot(dx, dy) * 15) * 100));
    }
    this.lastNose = { x: nose.x, y: nose.y };

    const mouth = Math.abs(lm[13].y - lm[14].y);
    const brow = Math.abs(lm[10].y - lm[151].y);
    const calm = Math.max(0, Math.min(100, (1 - (mouth * 4 + brow * 2)) * 100));
    const overall = eye * 0.4 + stable * 0.35 + calm * 0.25;

    this.latest = { eye, stable, calm, overall };
    if (this.els.eye) this.els.eye.style.width = `${eye}%`;
    if (this.els.stable) this.els.stable.style.width = `${stable}%`;
    if (this.els.calm) this.els.calm.style.width = `${calm}%`;
    if (this.els.overall) this.els.overall.textContent = `${Math.round(overall)}%`;
  }

  _record() {
    if (!this.latest) return;
    const s = {
      t: Math.round((Date.now() - this.t0) / 1000),
      eye: this.latest.eye,
      stable: this.latest.stable,
      calm: this.latest.calm,
      overall: this.latest.overall,
    };
    this.samples.push(s);
    if (this.onTick) this.onTick(s);
  }

  all() {
    return this.samples;
  }
}
