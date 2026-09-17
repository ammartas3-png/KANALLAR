const button = document.getElementById("produce");
const statusLine = document.getElementById("status");

async function waitForNewVideo(beforeCount) {
  for (let i = 0; i < 90; i += 1) {
    const response = await fetch("/api/stats");
    if (response.ok) {
      const stats = await response.json();
      if ((stats.videos || []).length > beforeCount) {
        window.location.reload();
        return;
      }
    }
    await new Promise((resolve) => setTimeout(resolve, 2000));
  }
  throw new Error("Üretim zaman aşımı");
}

if (button) {
  button.addEventListener("click", async () => {
    button.disabled = true;
    button.textContent = "Kuyrukta…";
    if (statusLine) statusLine.textContent = "Research → voice → render çalışıyor";
    try {
      const before = await fetch("/api/stats").then((r) => r.json());
      const response = await fetch("/api/produce", { method: "POST" });
      if (!response.ok) throw new Error(await response.text());
      await waitForNewVideo((before.videos || []).length);
    } catch (error) {
      button.disabled = false;
      button.textContent = "Video üret";
      alert(error);
    }
  });
}
