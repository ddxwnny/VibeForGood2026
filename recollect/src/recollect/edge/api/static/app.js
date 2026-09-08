// Mock frontend — throwaway. Calls the FastAPI backend directly; owns no data or logic.

async function json(url, opts) {
  const res = await fetch(url, opts);
  const text = await res.text();
  let data;
  try { data = JSON.parse(text); } catch { data = text; }
  if (!res.ok) throw new Error(typeof data === "string" ? data : (data.detail || res.statusText));
  return data;
}

function show(id, value, err) {
  const el = document.getElementById(id);
  if (err) { el.textContent = "error: " + err.message; return; }
  el.textContent = typeof value === "string" ? value : JSON.stringify(value, null, 2);
}

async function checkHealth() {
  const el = document.getElementById("health");
  try {
    const data = await json("/api/health");
    el.textContent = data.status === "ok" ? "online" : "degraded";
    el.className = "badge ok";
  } catch (e) {
    el.textContent = "offline";
    el.className = "badge err";
  }
}

// base64 of a placeholder "voice" — the mock needs *some* own-voice audio bytes.
const DUMMY_AUDIO = btoa(unescape(encodeURIComponent("own-voice ulysses instruction (mock)")));

async function enrol() {
  try {
    const data = await json("/api/enrolments", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        display_name: document.getElementById("enrol-name").value,
        preferred_language: document.getElementById("enrol-lang").value,
        recipient_co_signature: document.getElementById("enrol-co-sign").checked,
        research_consent: document.getElementById("enrol-research").checked,
        processor_disclosure_acknowledged: document.getElementById("enrol-disclosure").checked,
        ulysses_audio_base64: DUMMY_AUDIO,
      }),
    });
    document.getElementById("task-senior").value = data.senior_id;
    document.getElementById("series-senior").value = data.senior_id;
    document.getElementById("window-senior").value = data.senior_id;
    document.getElementById("erase-senior").value = data.senior_id;
    show("enrol-out", data);
  } catch (e) { show("enrol-out", null, e); }
}

async function roster() {
  try { show("roster-out", await json("/api/roster")); }
  catch (e) { show("roster-out", null, e); }
}

async function recordTask() {
  try {
    const data = await json("/api/seniors/" + document.getElementById("task-senior").value + "/observations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        signal_type: document.getElementById("task-signal").value,
        outcome: document.getElementById("task-outcome").value,
        content: document.getElementById("task-content").value,
      }),
    });
    show("task-out", data);
  } catch (e) { show("task-out", null, e); }
}

async function series() {
  try {
    const data = await json("/api/seniors/" + document.getElementById("series-senior").value + "/observations");
    show("series-out", data);
  } catch (e) { show("series-out", null, e); }
}

async function weekly() {
  try {
    const q = document.getElementById("window-baseline").checked ? "?baseline=true" : "";
    const data = await json("/api/seniors/" + document.getElementById("window-senior").value + "/window" + q, {
      method: "POST",
    });
    show("window-out", data);
  } catch (e) { show("window-out", null, e); }
}

async function erase() {
  try {
    const data = await json("/api/seniors/" + document.getElementById("erase-senior").value + "/erase", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reason: document.getElementById("erase-reason").value }),
    });
    show("erase-out", data);
  } catch (e) { show("erase-out", null, e); }
}

async function sweep() {
  try { show("sweep-out", await json("/api/jobs/retention-sweep", { method: "POST" })); }
  catch (e) { show("sweep-out", null, e); }
}

checkHealth();
