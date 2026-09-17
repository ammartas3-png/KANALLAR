const button = document.getElementById("produce");
if (button) {
  button.addEventListener("click", async () => {
    button.disabled = true;
    button.textContent = "Üretiliyor…";
    try {
      const response = await fetch("/api/produce", { method: "POST" });
      if (!response.ok) throw new Error(await response.text());
      window.location.reload();
    } catch (error) {
      button.disabled = false;
      button.textContent = "Video üret";
      alert(error);
    }
  });
}
