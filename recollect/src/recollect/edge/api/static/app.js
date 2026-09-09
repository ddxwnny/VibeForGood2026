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
    const data = await json("/v1/enrolments", {
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
    document.getElementById("chat-senior").value = data.senior_id;
    document.getElementById("series-senior").value = data.senior_id;
    document.getElementById("window-senior").value = data.senior_id;
    document.getElementById("erase-senior").value = data.senior_id;
    show("enrol-out", data);
  } catch (e) { show("enrol-out", null, e); }
}

async function roster() {
  try { show("roster-out", await json("/v1/roster")); }
  catch (e) { show("roster-out", null, e); }
}

async function recordTask() {
  try {
    const data = await json("/v1/seniors/" + document.getElementById("task-senior").value + "/observations", {
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
    const data = await json("/v1/seniors/" + document.getElementById("series-senior").value + "/observations");
    show("series-out", data);
  } catch (e) { show("series-out", null, e); }
}

async function weekly() {
  try {
    const q = document.getElementById("window-baseline").checked ? "?baseline=true" : "";
    const data = await json("/v1/seniors/" + document.getElementById("window-senior").value + "/window" + q, {
      method: "POST",
    });
    show("window-out", data);
  } catch (e) { show("window-out", null, e); }
}

async function erase() {
  try {
    const data = await json("/v1/seniors/" + document.getElementById("erase-senior").value + "/erase", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reason: document.getElementById("erase-reason").value }),
    });
    show("erase-out", data);
  } catch (e) { show("erase-out", null, e); }
}

async function sweep() {
  try { show("sweep-out", await json("/v1/jobs/retention-sweep", { method: "POST" })); }
  catch (e) { show("sweep-out", null, e); }
}

// --- Aunty Chatbot & Voice Logic ---

function appendChatMessage(sender, text) {
  const box = document.getElementById("chat-box");
  const msg = document.createElement("div");
  const isSenior = sender === "Senior";
  msg.style.padding = "8px 12px";
  msg.style.borderRadius = "8px";
  msg.style.maxWidth = "80%";
  msg.style.fontSize = "15px";
  msg.style.alignSelf = isSenior ? "flex-end" : "flex-start";
  msg.style.background = isSenior ? "var(--primary)" : "var(--soft)";
  msg.style.color = isSenior ? "#FFF" : "inherit";
  msg.innerHTML = `<strong>${sender}:</strong> ${text}`;
  box.appendChild(msg);
  box.scrollTop = box.scrollHeight;
  return msg;
}

function playAudioBase64(base64Audio) {
  const audio = new Audio("data:audio/mp3;base64," + base64Audio);
  audio.play().catch((err) => {
    console.warn("Audio play error:", err);
  });
}

function speakOutLoud(text, audioBase64 = null) {
  if (!document.getElementById("chat-tts")?.checked) return;
  if (audioBase64) {
    playAudioBase64(audioBase64);
    return;
  }
  if (!("speechSynthesis" in window)) return;
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 0.95; // slightly unhurried for older adult usability (NFR-17)
  window.speechSynthesis.speak(utterance);
}

let recognition = null;
let isRecording = false;

function toggleVoiceInput() {
  const btn = document.getElementById("mic-btn");
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    alert("Speech recognition is not supported in this browser. You can type your message.");
    return;
  }

  if (isRecording && recognition) {
    recognition.stop();
    return;
  }

  recognition = new SpeechRecognition();
  recognition.lang = "en-SG";
  recognition.interimResults = false;

  recognition.onstart = () => {
    isRecording = true;
    btn.textContent = "🛑 Listening…";
    btn.style.borderColor = "#c0392b";
    btn.style.color = "#c0392b";
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    document.getElementById("chat-input").value = transcript;
    sendChat();
  };

  recognition.onerror = () => {
    isRecording = false;
    btn.textContent = "🎤 Speak";
    btn.style.borderColor = "";
    btn.style.color = "";
  };

  recognition.onend = () => {
    isRecording = false;
    btn.textContent = "🎤 Speak";
    btn.style.borderColor = "";
    btn.style.color = "";
  };

  recognition.start();
}

async function sendChat() {
  const input = document.getElementById("chat-input");
  const text = input.value.trim();
  const seniorId = document.getElementById("chat-senior").value.trim();
  if (!text) return;
  if (!seniorId) {
    alert("Please enrol a senior first or enter their Senior ID.");
    return;
  }

  appendChatMessage("Senior", text);
  input.value = "";

  const thinkingElem = appendChatMessage("Recollect", "<em>Thinking…</em>");

  try {
    const data = await json(`/v1/seniors/${seniorId}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });

    if (thinkingElem) {
      thinkingElem.innerHTML = `<strong>Recollect:</strong> ${data.reply}`;
    } else {
      appendChatMessage("Recollect", data.reply);
    }
    speakOutLoud(data.reply, data.audio_base64);
    show("chat-out", data);

    // If an observation was recorded, automatically reload the functional series view
    if (data.observations_recorded && data.observations_recorded.length > 0) {
      document.getElementById("series-senior").value = seniorId;
      series();
    }
  } catch (err) {
    if (thinkingElem) {
      thinkingElem.innerHTML = `<strong>System:</strong> Error: ${err.message}`;
    } else {
      appendChatMessage("System", "Error: " + err.message);
    }
    show("chat-out", null, err);
  }
}

checkHealth();

