const labels = {
  queued: "Sırada",
  writing: "Senaryo yazılıyor",
  narrating: "Seslendiriliyor",
  designing: "Sahne kartları",
  rendering: "Video kuruluyor",
  ready: "Yayına hazır",
  uploading: "YouTube'a gidiyor",
  uploaded: "Yüklendi",
  failed: "Hata",
};

async function produce(channelId, button) {
  button.disabled = true;
  button.textContent = "Kuyruğa alındı…";
  const response = await fetch(`/api/channels/${channelId}/produce`, { method: "POST" });
  if (!response.ok) {
    button.disabled = false;
    button.textContent = "Video üret";
    alert(await response.text());
    return;
  }
  const job = await response.json();
  window.location.href = `/jobs/${job.id}`;
}

async function pollJob() {
  const page = document.querySelector("[data-job]");
  if (!page) return;
  const status = page.dataset.status;
  if (["ready", "uploaded", "failed"].includes(status)) return;
  const jobId = page.dataset.job;
  const tick = async () => {
    const response = await fetch(`/api/jobs/${jobId}`);
    if (!response.ok) return;
    const job = await response.json();
    const step = document.querySelector("[data-step]");
    if (step) {
      step.textContent = labels[job.step] || job.status;
      step.className = `status ${job.status}`;
    }
    if (["ready", "uploaded", "failed"].includes(job.status)) {
      window.location.reload();
      return;
    }
    window.setTimeout(tick, 2000);
  };
  tick();
}

document.querySelectorAll("[data-produce]").forEach((button) => {
  button.addEventListener("click", () => produce(button.dataset.produce, button));
});

pollJob();
