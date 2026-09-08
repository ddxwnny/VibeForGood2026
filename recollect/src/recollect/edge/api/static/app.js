// Mock frontend — throwaway. Calls the FastAPI backend directly; owns no data or logic.
async function checkHealth() {
  const el = document.getElementById("health");
  try {
    const res = await fetch("/api/health");
    const data = await res.json();
    el.textContent = data.status === "ok" ? "online" : "degraded";
    el.className = "badge ok";
  } catch (e) {
    el.textContent = "offline";
    el.className = "badge err";
  }
}

checkHealth();
