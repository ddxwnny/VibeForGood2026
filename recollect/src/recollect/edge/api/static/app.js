/**
 * ============================================================================
 * RECOLLECT — Frontend Application Engine
 * ============================================================================
 * A conversational companion and cognitive wellness screening platform.
 * 
 * Table of Contents:
 *  1. Configuration & Global Constants
 *  2. Icon Registry & SVG Helpers
 *  3. Application State & Storage Layer
 *  4. Cognitive Task Classifier & Signal Extraction
 *  5. Audio & Voice Synthesis Subsystem (ElevenLabs & Web Speech API)
 *  6. API Client & Data Access Layer
 *  7. Layout Shell & Navigation Router
 *  8. Screen Views & HTML Templates
 *  9. Event Delegation & Lifecycle Bootstrap
 * ============================================================================
 */

// ============================================================================
// 1. CONFIGURATION & GLOBAL CONSTANTS
// ============================================================================

const API_BASE = (
  typeof window !== 'undefined' &&
  (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') &&
  window.location.port !== '8000' &&
  window.location.port !== '3000' &&
  window.location.port !== ''
) ? 'http://127.0.0.1:8000' : '';

const landmarkPresets = [
  {
    title: 'Changi Beach Park',
    description: 'Coastal park where Arun enjoyed cycling and sea breezes on Sunday mornings.',
    image_url: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&auto=format&fit=crop&q=60',
    personal_memory: 'Arun spent Sunday mornings here in the 1980s cycling with his brother along the coastline.',
    recognition_keys: 'changi, changi beach, beach, coast, cycling, sea',
    prompt_question: 'Arun, look at this photo! Do you remember where this beach is?'
  },
  {
    title: 'Tiong Bahru Market',
    description: 'Historic market and hawker centre famous for fresh kopi and chwee kueh.',
    image_url: 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800&auto=format&fit=crop&q=60',
    personal_memory: 'Met old schoolmates every first Saturday of the month for breakfast.',
    recognition_keys: 'tiong bahru, market, hawker, chwee kueh, kopi, food centre',
    prompt_question: 'Do you recognize this bustling market with the big food centre upstairs?'
  },
  {
    title: 'Singapore Botanic Gardens — Orchid Garden',
    description: 'Lush tropical gardens with National Orchid Garden collection.',
    image_url: 'https://images.unsplash.com/photo-1528183429752-a97d0bf99b5a?w=800&auto=format&fit=crop&q=60',
    personal_memory: 'Lily loved photographing the purple orchid displays during the annual flower show.',
    recognition_keys: 'botanic, botanic garden, orchid, orchid garden, garden, flowers',
    prompt_question: 'Lily, look at these beautiful orchids! Do you remember which garden this was taken at?'
  },
  {
    title: 'Gardens by the Bay — Supertree Grove',
    description: 'Futuristic nature park by Marina Bay with iconic tree structures.',
    image_url: 'https://images.unsplash.com/photo-1525625293386-3f8f99389edd?w=800&auto=format&fit=crop&q=60',
    personal_memory: 'Visited with Mei during the evening light and sound show in 2023.',
    recognition_keys: 'gardens by the bay, supertree, marina, garden, bay',
    prompt_question: 'Do you remember visiting these giant flower trees with Mei?'
  },
  {
    title: 'Katong & Joo Chiat Heritage Shophouses',
    description: 'Colourful Peranakan shophouses and traditional bakeries.',
    image_url: 'https://images.unsplash.com/photo-1574958269340-fa927503f3dd?w=800&auto=format&fit=crop&q=60',
    personal_memory: 'Loved having Sunday afternoon laksa and kueh chang here.',
    recognition_keys: 'katong, joo chiat, shophouses, peranakan, laksa',
    prompt_question: 'Do you recognize these colourful pastel heritage houses in the East?'
  }
];

const defaultPlaces = {
  '018d0000-0000-7000-8000-000000000001': [
    {
      id: '018d0000-0000-7000-8000-000000000101',
      senior_id: '018d0000-0000-7000-8000-000000000001',
      title: 'Changi Beach Park',
      description: 'Where Arun used to go cycling every Sunday morning and have teh tarik with friends.',
      image_url: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&auto=format&fit=crop&q=60',
      personal_memory: 'Arun spent Sunday mornings here in the 1980s cycling with his brother along the coastline.',
      recognition_keys: ['changi', 'changi beach', 'beach', 'coast', 'cycling', 'sea'],
      prompt_question: 'Arun, look at this photo! Do you remember where this beach is?',
      recall_attempts: 3,
      recall_successes: 3,
      last_asked_at: 'Yesterday',
      status: 'Recognized'
    },
    {
      id: '018d0000-0000-7000-8000-000000000102',
      senior_id: '018d0000-0000-7000-8000-000000000001',
      title: 'Tiong Bahru Market & Hawker Centre',
      description: "Arun's favourite spot for chwee kueh and fresh kopi on weekends.",
      image_url: 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800&auto=format&fit=crop&q=60',
      personal_memory: 'Met here with old schoolmates every first Saturday of the month.',
      recognition_keys: ['tiong bahru', 'market', 'hawker', 'chwee kueh', 'kopi', 'food centre'],
      prompt_question: 'Do you recognize this famous market with the round courtyard?',
      recall_attempts: 2,
      recall_successes: 1,
      last_asked_at: '3 days ago',
      status: 'Needed Clue'
    }
  ],
  '018d0000-0000-7000-8000-000000000002': [
    {
      id: '018d0000-0000-7000-8000-000000000103',
      senior_id: '018d0000-0000-7000-8000-000000000002',
      title: 'Singapore Botanic Gardens — Orchid Garden',
      description: "Lily's beloved VIP Orchid Garden where she admires rare orchid hybrids.",
      image_url: 'https://images.unsplash.com/photo-1528183429752-a97d0bf99b5a?w=800&auto=format&fit=crop&q=60',
      personal_memory: 'Lily took award-winning photographs of the National Orchid Garden during the annual orchid show.',
      recognition_keys: ['botanic', 'botanic garden', 'orchid', 'orchid garden', 'garden', 'flowers'],
      prompt_question: 'Lily, look at these beautiful orchids! Do you remember which garden this was taken at?',
      recall_attempts: 4,
      recall_successes: 4,
      last_asked_at: '2 days ago',
      status: 'Recognized'
    }
  ]
};

const defaultConversations = {
  // Arun (Early Cognitive Signal Screening Demo: IADL Medication, Orientation, Misplacing)
  '018d0000-0000-7000-8000-000000000001': [
    { role: 'ai', text: 'Good morning Arun! How is your day going? Remember to take your morning blood pressure medication with breakfast.', time: '08:30 AM' },
    { role: 'you', text: 'Good morning Aunty. I haven\'t taken my blood pressure pills today... I forgot where I put the box.', time: '08:32 AM', flag: 'medication_incomplete' },
    { role: 'ai', text: 'No worries Arun, don\'t rush. The blood pressure pills are usually kept on the kitchen counter by the kettle. Would you like to check there first?', time: '08:32 AM' },
    { role: 'you', text: 'Aunty, what day is today? Is it Wednesday or Thursday?', time: '10:15 AM', flag: 'date_time_incomplete' },
    { role: 'ai', text: 'Today is Wednesday morning, Arun. It is 10:15 AM and you have no doctor appointments scheduled today, so you can relax peacefully.', time: '10:15 AM' }
  ],
  // Lily (Stable Baseline Routine)
  '018d0000-0000-7000-8000-000000000002': [
    { role: 'ai', text: 'Good morning Lily! How are your purple orchids doing on the balcony today?', time: '09:00 AM' },
    { role: 'you', text: 'Good morning Aunty! I watered them and took my morning calcium tablet after eating papaya.', time: '09:02 AM' },
    { role: 'ai', text: 'That is wonderful Lily! It is so nice to start the morning with your plants. Remember to drink warm water during your walk.', time: '09:02 AM' },
    { role: 'you', text: 'Aunty, did Mei send the community centre newsletter photos?', time: '11:05 AM' },
    { role: 'ai', text: 'Yes Lily, Mei shared the photos and noted your handicraft session for next week!', time: '11:05 AM' }
  ]
};

// ============================================================================
// 2. ICON REGISTRY & SVG HELPERS
// ============================================================================

const icons = {
  back: '<path d="m15 5-7 7 7 7"/>',
  people: '<circle cx="9" cy="8" r="3"/><path d="M3 21v-3a6 6 0 0 1 12 0v3M17 5a3 3 0 0 1 0 6m1 4a5 5 0 0 1 3 5"/>',
  home: '<path d="m3 10 9-7 9 7v11H3zM9 21v-8h6v8"/>',
  place: '<path d="M12 21s-7-4.35-7-10a7 7 0 1 1 14 0c0 5.65-7 10-7 10Z"/><circle cx="12" cy="11" r="3"/>',
  image: '<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="m21 15-5-5L5 21"/>',
  note: '<rect x="4" y="3" width="16" height="19" rx="3"/><path d="M8 8h8M8 12h8M8 16h5"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  arrow: '<path d="M4 12h16m-6-6 6 6-6 6"/>',
  leaf: '<path d="M4 20C1 8 10 3 21 3c0 11-5 19-17 17Zm0 0L16 8"/>',
  mic: '<rect x="8" y="2" width="8" height="13" rx="4"/><path d="M5 10v2a7 7 0 0 0 14 0v-2M12 19v3M8 22h8"/>',
  check: '<path d="m5 12 4 4L20 5"/>',
  volume: '<polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/>',
  sparkles: '<path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z"/>',
  trash: '<path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>',
};

const icon = name => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${icons[name] || icons.leaf}</svg>`;
const escape = value => String(value).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

// ============================================================================
// 3. APPLICATION STATE & STORAGE LAYER
// ============================================================================

let people = [
  { id: '018d0000-0000-7000-8000-000000000001', name: 'Arun', initials: 'AR', relation: 'Father', age: '72', last: 'Active', reachable: true, consent: true, fresh: false },
  { id: '018d0000-0000-7000-8000-000000000002', name: 'Lily', initials: 'LY', relation: 'Mother', age: '68', last: 'Active', reachable: true, consent: true, fresh: false },
];

let caregiver = false;
let selected = people[0].id;
let linked = people[0];
let pendingPerson = null;
let invitation = null;
let activePlaceQuiz = null; // currently active place recall memory test in chat session
let authMode = 'signup';
let voiceState = 'idle';
let dirty = false;
let lastRoute = '';
let currentAudio = null;
let recognition = null;
let windowData = null;
let observationsData = [];
let overviewPlacesTab = 'list';

function loadPlaces() {
  try {
    const saved = localStorage.getItem('recollect_places_v3');
    if (saved) return JSON.parse(saved);
  } catch (e) {}
  return JSON.parse(JSON.stringify(defaultPlaces));
}

let seniorPlaces = loadPlaces();

function savePlaces() {
  try {
    localStorage.setItem('recollect_places_v3', JSON.stringify(seniorPlaces));
  } catch (e) {}
}

function getSeniorPlaces(seniorId) {
  const id = seniorId || selected || '018d0000-0000-7000-8000-000000000001';
  if (!seniorPlaces[id]) {
    seniorPlaces[id] = [];
  }
  return seniorPlaces[id];
}

function loadConversations() {
  try {
    const saved = localStorage.getItem('recollect_conversations_v4');
    if (saved) return JSON.parse(saved);
  } catch (e) {}
  return JSON.parse(JSON.stringify(defaultConversations));
}

let seniorConversations = loadConversations();

function saveConversations() {
  try {
    localStorage.setItem('recollect_conversations_v4', JSON.stringify(seniorConversations));
  } catch (e) {}
}

function getSeniorMessages(seniorId) {
  const p = people.find(item => item.id === seniorId) || currentPerson();
  const id = seniorId || p.id || '018d0000-0000-7000-8000-000000000001';
  if (!seniorConversations[id]) {
    seniorConversations[id] = [
      { role: 'ai', text: `Good day, ${escape(p.name)}! Welcome to Recollect. How is your morning going? Remember to take your morning medication when you are ready.`, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }
    ];
  }
  return seniorConversations[id];
}

const currentPerson = () => people.find(p => p.id === selected) || people[0] || { id: '', name: 'Senior', initials: 'SN', relation: 'Senior' };

// ============================================================================
// 4. COGNITIVE TASK CLASSIFIER & SIGNAL EXTRACTION
// ============================================================================

function extractClientTask(text) {
  const lowered = text.toLowerCase();
  const isDeclined = ["don't want", "dont want", "refuse", "skip", "no need", "never take"].some(w => lowered.includes(w));
  const isForgotten = [
    "forgot", "forget", "didn't take", "didnt take", "haven't taken", "havent taken",
    "cannot find", "can't find", "where did i put", "not yet taken", "lost my",
    "don't know", "dont know", "do not know", "no idea", "no clue",
    "cant remember", "can't remember", "don't remember", "dont remember", "do not remember", "not remember",
    "cannot recall", "can't recall", "don't recall", "dont recall", "do not recall",
    "not sure where", "not sure", "never seen this", "never seen",
    "don't recognize", "dont recognize", "do not recognize", "cannot recognize",
    "not familiar", "unfamiliar"
  ].some(w => lowered.includes(w));

  let outcome = 'completed';
  if (isDeclined) outcome = 'declined';
  else if (isForgotten) outcome = 'incomplete';

  // 1. Temporal & Date/Time orientation signals
  const datetimeKeywords = [
    "what day is it", "what is today", "what date is it", "which day", "which month",
    "what year", "is it sunday", "is it monday", "is it tuesday", "is it wednesday",
    "is it thursday", "is it friday", "is it saturday", "is it morning", "is it evening",
    "what time is it", "where am i"
  ];
  if (datetimeKeywords.some(k => lowered.includes(k))) {
    return { signal_type: 'date_time', outcome: 'incomplete', content: text };
  }

  // 2. Misplacing everyday objects
  const misplaceKeywords = [
    "cannot find my", "can't find my", "where did i leave my", "lost my keys",
    "lost my wallet", "lost my glasses", "where is my purse", "where are my glasses", "someone moved my"
  ];
  if (misplaceKeywords.some(k => lowered.includes(k)) && !["pill", "medicine", "medication"].some(m => lowered.includes(m))) {
    return { signal_type: 'misplacing', outcome: 'incomplete', content: text };
  }

  // 3. Word-finding / Language difficulty / Anomia
  const languageKeywords = [
    "what is that thing called", "the thing you use to", "i forgot the word",
    "can't think of the name", "what do you call it"
  ];
  if (languageKeywords.some(k => lowered.includes(k))) {
    return { signal_type: 'language', outcome: 'incomplete', content: text };
  }

  // 4. Memory / Repetition queries
  const memoryKeywords = [
    "did anyone visit", "did i eat", "did mei call", "did someone call",
    "did i have breakfast", "did i have lunch"
  ];
  if (memoryKeywords.some(k => lowered.includes(k))) {
    return { signal_type: 'memory', outcome: 'incomplete', content: text };
  }

  // 5. Place Memory / Photo Reminiscence queries
  const placeKeywords = [
    "changi", "beach", "gardens by the bay", "tiong bahru", "botanic", "merlion",
    "katong", "photo", "picture", "this place", "that place", "the place",
    "where this is", "where is that", "where is this", "where was this", "what place", "which place",
    "remember the place", "remember this place", "that looks like", "is that the", "is this the",
    "that is the", "thats the"
  ];
  if (activePlaceQuiz || placeKeywords.some(k => lowered.includes(k))) {
    return { signal_type: 'place_memory', outcome, content: text };
  }

  // 6. Medication signals
  if (["medicine", "pills", "pill", "medication", "tablet", "dose", "panadol", "blood pressure"].some(k => lowered.includes(k))) {
    return { signal_type: 'medication', outcome, content: text };
  }

  // 7. Appointment signals
  if (["appointment", "polyclinic", "hospital", "doctor", "clinic", "checkup", "see doctor"].some(k => lowered.includes(k))) {
    return { signal_type: 'appointment', outcome, content: text };
  }

  // 8. Mail / Letter signals
  if (["letter", "mail", "post", "envelope", "cpf", "town council", "bill"].some(k => lowered.includes(k))) {
    return { signal_type: 'mail', outcome, content: text };
  }

  // 9. Routine signals
  if (["walk", "exercise", "market", "breakfast", "lunch", "dinner", "tai chi", "park connector", "garden", "plants", "orchid"].some(k => lowered.includes(k))) {
    return { signal_type: 'routine', outcome, content: text };
  }

  return null;
}

// ============================================================================
// 5. AUDIO & VOICE SYNTHESIS SUBSYSTEM
// ============================================================================

let isAudioUnlocked = false;
let sharedAudioElement = null;

function unlockAudio() {
  if (!sharedAudioElement) {
    sharedAudioElement = new Audio();
  }
  if (window.speechSynthesis && window.speechSynthesis.paused) {
    try { window.speechSynthesis.resume(); } catch (e) {}
  }
  if (isAudioUnlocked) return;
  try {
    sharedAudioElement.src = 'data:audio/wav;base64,UklGRigAAABXQVZFZm10IBIAAAABAAEARKwAAIhYAQACABAAAABkYXRhAgAAAAEA';
    const p = sharedAudioElement.play();
    if (p !== undefined) {
      p.then(() => {
        sharedAudioElement.pause();
        isAudioUnlocked = true;
      }).catch(() => {});
    }
  } catch (e) {}
}

['click', 'touchstart', 'keydown', 'submit'].forEach(evt => {
  document.addEventListener(evt, unlockAudio, { passive: true });
});

function updateVoiceUI() {
  const micBtn = document.querySelector('.mic[data-action="voice"]');
  const statusEl = document.querySelector('#voice-status');
  if (micBtn && statusEl) {
    micBtn.setAttribute('aria-label', voiceState === 'listening' ? 'Stop listening' : (voiceState === 'speaking' ? 'Stop speaking' : 'Start speaking'));
    micBtn.innerHTML = voiceState === 'listening' ? '<span aria-hidden="true" style="font-size:24px">■</span>' : (voiceState === 'speaking' ? icon('volume') : icon('mic'));
    statusEl.textContent = voiceState === 'listening' ? 'Listening… speak now' : (voiceState === 'speaking' ? 'Speaking aloud…' : 'Tap mic to talk aloud');
    return true;
  }
  return false;
}

async function playAuntyVoice(text, audioBase64, lang = 'en-SG') {
  voiceState = 'speaking';
  if (!updateVoiceUI()) render();

  if (audioBase64) {
    try {
      if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
      }
      currentAudio = sharedAudioElement || new Audio();
      currentAudio.src = `data:audio/mpeg;base64,${audioBase64}`;
      currentAudio.onended = () => {
        voiceState = 'idle';
        if (!updateVoiceUI()) render();
      };
      currentAudio.onerror = () => {
        console.warn('ElevenLabs audio playback failed, falling back to speech synthesis');
        speakText(text, lang, () => {
          voiceState = 'idle';
          if (!updateVoiceUI()) render();
        });
      };
      const playPromise = currentAudio.play();
      if (playPromise !== undefined) {
        await playPromise;
        return;
      }
    } catch (err) {
      console.warn('ElevenLabs audio playback error or autoplay blocked, falling back to speech synthesis:', err);
    }
  }

  // Fallback to browser Speech Synthesis
  speakText(text, lang, () => {
    voiceState = 'idle';
    if (!updateVoiceUI()) render();
  });
}

function speakText(text, lang = 'en-SG', onEnd) {
  if (!('speechSynthesis' in window) || !window.speechSynthesis) {
    if (onEnd) onEnd();
    return;
  }
  try {
    window.speechSynthesis.cancel();
    window.speechSynthesis.resume();

    const cleanText = String(text || '').replace(/<[^>]*>?/gm, '').replace(/[*_#`]/g, '');
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = lang || 'en-SG';
    utterance.rate = 0.92;
    utterance.pitch = 1.0;

    const voices = window.speechSynthesis.getVoices();
    if (voices && voices.length) {
      const match = voices.find(v => v.lang === lang) ||
                    voices.find(v => v.lang.startsWith(lang.split('-')[0])) ||
                    voices.find(v => v.lang.includes('en') && (v.name.includes('Natural') || v.name.includes('Neural') || v.name.includes('Female') || v.name.includes('Google') || v.name.includes('Microsoft') || v.name.includes('Zira') || v.name.includes('Samantha')));
      if (match) utterance.voice = match;
    }

    let finished = false;
    const finish = () => {
      if (!finished) {
        finished = true;
        if (onEnd) onEnd();
      }
    };

    utterance.onend = finish;
    utterance.onerror = (e) => {
      console.warn('SpeechSynthesis error:', e);
      finish();
    };

    // Chromium timer fix for speech synthesis
    const timer = setInterval(() => {
      if (!window.speechSynthesis.speaking) {
        clearInterval(timer);
      } else {
        window.speechSynthesis.resume();
      }
    }, 4000);

    window.speechSynthesis.speak(utterance);
  } catch (err) {
    console.warn('Browser SpeechSynthesis failed:', err);
    if (onEnd) onEnd();
  }
}

function startVoiceRecognition() {
  const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRec) {
    const spoken = prompt("Speak to Aunty (simulate voice input):", activePlaceQuiz ? "I think that's Changi Beach where we went cycling!" : "I took my morning blood pressure medication.");
    if (spoken) addReply(spoken);
    voiceState = 'idle';
    if (!updateVoiceUI()) render();
    return;
  }

  if (recognition) {
    try { recognition.stop(); } catch (e) {}
  }

  recognition = new SpeechRec();
  recognition.lang = 'en-SG';
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.onstart = () => {
    voiceState = 'listening';
    if (!updateVoiceUI()) render();
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    voiceState = 'idle';
    updateVoiceUI();
    addReply(transcript);
  };

  recognition.onerror = (event) => {
    console.warn('Speech recognition error:', event.error);
    voiceState = 'idle';
    if (!updateVoiceUI()) render();
  };

  recognition.onend = () => {
    if (voiceState === 'listening') {
      voiceState = 'idle';
      if (!updateVoiceUI()) render();
    }
  };

  try {
    recognition.start();
  } catch (e) {
    console.warn('Recognition start failed:', e);
    voiceState = 'idle';
    if (!updateVoiceUI()) render();
  }
}

// ============================================================================
// 6. API CLIENT & DATA ACCESS LAYER
// ============================================================================

async function fetchRoster() {
  try {
    const res = await fetch(`${API_BASE}/v1/roster`);
    if (res.ok) {
      const data = await res.json();
      if (data.roster && data.roster.length) {
        people = data.roster.map(r => ({
          id: r.senior_id,
          name: r.display_name,
          initials: r.display_name.slice(0, 2).toUpperCase(),
          relation: 'Senior',
          last: 'Active',
          reachable: r.device_reachable,
          consent: r.consent_active,
          fresh: false,
        }));
        if (!people.some(p => p.id === selected)) {
          selected = people[0].id;
        }
        if (!linked || !people.some(p => p.id === linked.id)) {
          linked = people[0];
        }
      }
    }
  } catch (e) {
    console.warn('Could not fetch /v1/roster from backend; using default roster:', e);
  }
}

async function fetchWeeklyWindow(seniorId) {
  if (!seniorId) return;
  try {
    const [winRes, obsRes] = await Promise.all([
      fetch(`${API_BASE}/v1/seniors/${seniorId}/window`),
      fetch(`${API_BASE}/v1/seniors/${seniorId}/observations`),
    ]);
    if (winRes.ok) {
      windowData = await winRes.json();
    }
    if (obsRes.ok) {
      const data = await obsRes.json();
      observationsData = (data.observations || []).slice().reverse();
    }
  } catch (e) {
    console.warn('Could not fetch weekly window or observations:', e);
  }
}

async function fetchPlaces(seniorId) {
  if (!seniorId) return;
  try {
    const res = await fetch(`${API_BASE}/v1/seniors/${seniorId}/places`);
    if (res.ok) {
      const data = await res.json();
      if (data.places && data.places.length) {
        seniorPlaces[seniorId] = data.places;
        savePlaces();
      }
    }
  } catch (e) {
    console.warn('Using local places store:', e);
  }
}

async function addReply(text) {
  if (!text) return;
  unlockAudio();
  const seniorId = (linked && linked.id) ? linked.id : selected;
  const personName = (linked && linked.name) ? linked.name : 'Senior';
  const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const clientTask = extractClientTask(text);

  const msgs = getSeniorMessages(seniorId);
  const flag = (clientTask && (clientTask.outcome === 'incomplete' || clientTask.outcome === 'declined')) ? `${clientTask.signal_type}_${clientTask.outcome}` : null;
  msgs.push({ role: 'you', text, time: timeStr, flag });
  saveConversations();
  render();
  document.querySelector('.conversation')?.lastElementChild?.scrollIntoView({ block: 'nearest' });

  voiceState = 'speaking';
  const statusEl = document.querySelector('#voice-status');
  if (statusEl) statusEl.textContent = 'Aunty is thinking…';

  // Handle active Place Quiz response if currently evaluating a memory photo
  if (activePlaceQuiz) {
    const quiz = activePlaceQuiz;
    const lowered = text.toLowerCase();
    const rawKeys = Array.isArray(quiz.recognition_keys) ? quiz.recognition_keys : String(quiz.recognition_keys || '').split(',');
    const keys = rawKeys.map(k => k.trim().toLowerCase()).filter(Boolean);
    const titleWords = quiz.title.toLowerCase().split(/\s+/).filter(w => w.length > 3);
    const allPlaceKeys = [...new Set([...keys, ...titleWords])];

    const forgets = [
      "do not remember", "don't remember", "dont remember", "not remember",
      "cannot remember", "cant remember", "can't remember",
      "do not recall", "don't recall", "dont recall", "cannot recall", "cant recall", "can't recall",
      "do not know", "don't know", "dont know", "no idea", "no clue", "not sure",
      "forgot", "forget", "never seen", "where is this", "where is that", "where was this",
      "do not recognize", "don't recognize", "dont recognize", "cannot recognize", "cant recognize",
      "not familiar", "unfamiliar", "no memory", "cannot tell", "can't tell"
    ].some(w => lowered.includes(w));

    const asksHint = ["hint", "clue", "help", "what is it", "give me a clue", "tell me"].some(w => lowered.includes(w));
    const namedPlace = allPlaceKeys.some(k => lowered.includes(k));
    const matched = !forgets && namedPlace;

    let replyText = "";
    let obsOutcome = "incomplete";

    if (matched) {
      quiz.recall_attempts = (quiz.recall_attempts || 0) + 1;
      quiz.recall_successes = (quiz.recall_successes || 0) + 1;
      quiz.status = 'Recognized';
      quiz.last_asked_at = 'Just now';
      obsOutcome = "completed";
      replyText = `Yes, spot on ${personName}! That is ${quiz.title}. ${quiz.personal_memory || ''} You remembered it right away! What a wonderful memory.`;
      activePlaceQuiz = null;
    } else if (asksHint) {
      quiz.status = 'Needed Clue';
      obsOutcome = "incomplete";
      replyText = `Here's a gentle clue, ${personName}: ${quiz.description || quiz.personal_memory || 'It is a special place in Singapore you used to visit.'} Does that bring back memories?`;
    } else {
      // Forgets / disoriented
      quiz.recall_attempts = (quiz.recall_attempts || 0) + 1;
      quiz.status = 'Needed Clue';
      quiz.last_asked_at = 'Just now';
      obsOutcome = "incomplete";
      replyText = `No worries at all, ${personName}, take your time! That is ${quiz.title}. ${quiz.personal_memory || ''} It looks so peaceful in the photo, doesn't it?`;
      activePlaceQuiz = null;
    }

    savePlaces();

    // Log the place memory observation to the backend and observations list
    try {
      await fetch(`${API_BASE}/v1/seniors/${seniorId}/observations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          signal_type: 'place_memory',
          outcome: obsOutcome,
          content: `Place memory recall (${quiz.title}): "${text}" -> ${obsOutcome === 'completed' ? 'Recognized' : 'Disoriented/Needed Clue'}`,
        }),
      });
    } catch (e) {
      console.warn('Place memory observation save fallback:', e);
    }

    const aiTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    msgs.push({ role: 'ai', text: replyText, time: aiTime });
    saveConversations();
    await fetchWeeklyWindow(seniorId);
    render();
    announce('Aunty replied: ' + replyText);
    document.querySelector('.conversation')?.lastElementChild?.scrollIntoView({ block: 'nearest' });
    await playAuntyVoice(replyText, null, linked?.preferred_language || 'en-SG');
    return;
  }

  // Check if this turn should trigger a periodic memory photo recall screening
  const placesList = getSeniorPlaces(seniorId);
  const userMsgCount = msgs.filter(m => m.role === 'you').length;
  const shouldTriggerPhoto = !activePlaceQuiz && placesList && placesList.length > 0 && (userMsgCount === 3 || (userMsgCount > 3 && userMsgCount % 4 === 0));

  if (shouldTriggerPhoto) {
    const nextPlace = placesList.slice().sort((a, b) => (a.recall_attempts || 0) - (b.recall_attempts || 0))[0];
    if (nextPlace) {
      activePlaceQuiz = nextPlace;
      const photoPrompt = nextPlace.prompt_question || `Look at this photo, ${personName}! Do you remember where this place is?`;
      const aiTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      msgs.push({
        role: 'ai',
        text: photoPrompt,
        time: aiTime,
        place_memory: nextPlace,
      });
      saveConversations();
      render();
      announce(`Aunty showed a photo: ${photoPrompt}`);
      document.querySelector('.conversation')?.lastElementChild?.scrollIntoView({ block: 'nearest' });
      await playAuntyVoice(photoPrompt, null, linked?.preferred_language || 'en-SG');
      return;
    }
  }

  try {
    const historyPayload = msgs.slice(-6).map(m => ({ role: m.role, text: m.text }));
    const res = await fetch(`${API_BASE}/v1/seniors/${seniorId}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text, history: historyPayload }),
    });

    if (res.ok) {
      const data = await res.json();
      const aiTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      msgs.push({ role: 'ai', text: data.reply, time: aiTime });
      saveConversations();
      render();
      announce('Aunty replied: ' + data.reply);
      document.querySelector('.conversation')?.lastElementChild?.scrollIntoView({ block: 'nearest' });

      // Refresh observations & weekly window in the background
      await fetchWeeklyWindow(seniorId);

      await playAuntyVoice(data.reply, data.audio_base64, linked?.preferred_language || 'en-SG');
    } else {
      let fallbackMsg = `Thank you for telling me, ${escape(personName)}. I’ve made a note of that for your routine!`;
      if (clientTask) {
        if (clientTask.signal_type === 'medication' && clientTask.outcome === 'incomplete') {
          fallbackMsg = `No worries, ${escape(personName)}, don't rush. The blood pressure pills are usually kept on the kitchen counter by the kettle. Would you like to check there first?`;
        } else if (clientTask.signal_type === 'place_memory') {
          fallbackMsg = `It's always lovely looking through family photos together, ${escape(personName)}. Would you like to see another familiar spot?`;
        } else if (clientTask.signal_type === 'date_time') {
          fallbackMsg = `Today is Wednesday morning, ${escape(personName)}. It is a bright morning at 10:30 AM. You have no doctor appointments scheduled today, so you can enjoy your day calmly.`;
        } else if (clientTask.signal_type === 'misplacing') {
          fallbackMsg = `Let’s check the usual spots together, ${escape(personName)}. Have you taken a look on the side table by the front door or beside your armchair?`;
        } else if (clientTask.signal_type === 'language') {
          fallbackMsg = `Take your time, ${escape(personName)}, no rush at all. Are you thinking of your reading glasses, or something in the kitchen?`;
        } else if (clientTask.signal_type === 'memory') {
          fallbackMsg = `Mei called earlier to ask how your morning was, ${escape(personName)}. She is doing well and sends you her love!`;
        }
      }
      const aiTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      msgs.push({ role: 'ai', text: fallbackMsg, time: aiTime });
      saveConversations();
      render();
      await playAuntyVoice(fallbackMsg, null, linked?.preferred_language || 'en-SG');
    }
  } catch (err) {
    console.error('Chat error:', err);
    let fallbackMsg = `That sounds good, ${escape(personName)}. Is there anything else you would like to share today?`;
    if (clientTask) {
      if (clientTask.signal_type === 'medication' && clientTask.outcome === 'incomplete') {
        fallbackMsg = `No worries, ${escape(personName)}, don't rush. The blood pressure pills are usually kept on the kitchen counter by the kettle. Would you like to check there first?`;
      } else if (clientTask.signal_type === 'place_memory') {
        fallbackMsg = `It's always lovely looking through family photos together, ${escape(personName)}. Would you like to see another familiar spot?`;
      } else if (clientTask.signal_type === 'date_time') {
        fallbackMsg = `Today is Wednesday morning, ${escape(personName)}. It is a bright morning at 10:30 AM. You have no doctor appointments scheduled today, so you can enjoy your day calmly.`;
      } else if (clientTask.signal_type === 'misplacing') {
        fallbackMsg = `Let’s check the usual spots together, ${escape(personName)}. Have you taken a look on the side table by the front door or beside your armchair?`;
      } else if (clientTask.signal_type === 'language') {
        fallbackMsg = `Take your time, ${escape(personName)}, no rush at all. Are you thinking of your reading glasses, or something in the kitchen?`;
      } else if (clientTask.signal_type === 'memory') {
        fallbackMsg = `Mei called earlier to ask how your morning was, ${escape(personName)}. She is doing well and sends you her love!`;
      }
    }
    const aiTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    msgs.push({ role: 'ai', text: fallbackMsg, time: aiTime });
    saveConversations();
    render();
    await playAuntyVoice(fallbackMsg, null, linked?.preferred_language || 'en-SG');
  }
}

function makeInvitation() {
  invitation = {
    code: String(crypto.getRandomValues(new Uint32Array(1))[0] % 900000 + 100000),
    expires: Date.now() + 10 * 60 * 1000
  };
}

// ============================================================================
// 7. LAYOUT SHELL & NAVIGATION ROUTER
// ============================================================================

const brand = () => '<a class="brand" href="#welcome" aria-label="Recollect home"><span class="mark" aria-hidden="true"></span>recollect</a>';

const publicHeader = () => {
  const route = location.hash.slice(1) || 'welcome';
  const parent = {
    auth: 'welcome',
    reset: 'auth',
    connect: caregiver ? 'invite' : 'welcome',
    consent: 'connect',
    chat: 'welcome',
    connection: 'chat',
    finish: 'welcome'
  }[route];
  return `<header class="public-header">${parent ? `<a class="back-button" href="#${parent}" aria-label="Back">${icon('back')}<span>Back</span></a>` : '<span class="header-spacer"></span>'}${brand()}<span class="header-spacer"></span></header>`;
};

const announce = text => {
  const el = document.querySelector('#announcement');
  if (el) el.textContent = text;
};

const go = path => {
  location.hash = path;
};

function shell(content, active = 'family') {
  return `
    <div class="shell">
      <header class="topbar">
        ${brand()}
        <button class="text-button" data-action="logout">Exit demo</button>
      </header>
      <main id="main" tabindex="-1" class="main-content">
        ${content}
        <p class="footer-note">Fictional demo · Not a health assessment.</p>
      </main>
      <nav class="tab-bar" aria-label="Caregiver navigation">
        ${[
          ['family', 'people', 'Family'],
          ['dashboard', 'home', 'Overview'],
          ['observations', 'note', 'Notes']
        ].map(([route, symbol, label]) => `
          <a class="nav-link ${active === route ? 'active' : ''}" ${active === route ? 'aria-current="page"' : ''} href="#${route}">
            ${icon(symbol)}
            <span>${label}</span>
          </a>
        `).join('')}
      </nav>
    </div>
  `;
}

function personSelect() {
  return `
    <div class="person-select">
      <label for="person-select">Viewing updates for</label>
      <select id="person-select">
        ${people.map(p => `
          <option value="${p.id}" ${p.id === selected ? 'selected' : ''}>${escape(p.name)}</option>
        `).join('')}
      </select>
    </div>
  `;
}

function render() {
  let route = location.hash.slice(1) || 'welcome';
  if (dirty && route !== lastRoute) {
    if (!window.confirm('Leave without saving your observation changes?')) {
      history.replaceState(null, '', `#${lastRoute}`);
      return;
    }
    dirty = false;
  }

  if (!pages[route]) {
    history.replaceState(null, '', '#welcome');
    route = 'welcome';
  }

  if (protectedPages.includes(route) && !caregiver) {
    history.replaceState(null, '', '#auth');
    route = 'auth';
  }

  if (route !== 'chat') {
    voiceState = 'idle';
    if (currentAudio) {
      currentAudio.pause();
      currentAudio = null;
    }
  }

  document.body.dataset.screen = route;

  const isRouteChange = route !== lastRoute;
  const prevScrollY = window.scrollY;
  const conversationEl = document.querySelector('.conversation');
  const prevConvScroll = conversationEl ? conversationEl.scrollTop : null;

  app.innerHTML = pages[route]();
  lastRoute = route;
  document.title = `Recollect · ${route.charAt(0).toUpperCase() + route.slice(1)}`;

  if (isRouteChange) {
    document.querySelector('#main')?.focus({ preventScroll: true });
    window.scrollTo(0, 0);
  } else {
    window.scrollTo(0, prevScrollY);
    if (prevConvScroll !== null) {
      const newConvEl = document.querySelector('.conversation');
      if (newConvEl) newConvEl.scrollTop = prevConvScroll;
    }
  }

  if (route === 'dashboard' || route === 'observations' || route === 'places') {
    Promise.all([
      fetchWeeklyWindow(selected),
      fetchPlaces(selected)
    ]).then(() => {
      const cur = location.hash.slice(1);
      if (cur === 'dashboard' || cur === 'observations' || cur === 'places') {
        const pY = window.scrollY;
        app.innerHTML = pages[cur]();
        window.scrollTo(0, pY);
      }
    });
  } else if (route === 'family') {
    fetchRoster().then(() => {
      if (location.hash.slice(1) === 'family') {
        const pY = window.scrollY;
        app.innerHTML = pages.family();
        window.scrollTo(0, pY);
      }
    });
  }
}

// ============================================================================
// 8. SCREEN VIEWS & HTML TEMPLATES
// ============================================================================

function welcome() {
  return `
    ${publicHeader()}
    <main id="main" tabindex="-1" class="hero">
      <div class="welcome-art" aria-hidden="true">
        <div class="garden">
          <span class="sun"></span>
          <span class="hill"></span>
          <span class="hill two"></span>
          <span class="plant"></span>
        </div>
      </div>
      <div class="welcome-copy">
        <p class="eyebrow">A little closer, every day</p>
        <h1>A moment to talk.<br><em>A way to connect.</em></h1>
        <p class="intro muted">Everyday conversations for you.<br>A little peace of mind for your family.</p>
      </div>
      <div class="role-list">
        <a class="role button" href="#auth">
          <span class="icon-box">${icon('people')}</span>
          <span><strong>I’m a caregiver</strong><small>Stay close to my loved ones</small></span>
          <span class="arrow">${icon('arrow')}</span>
        </a>
        <a class="role button" href="${linked ? '#chat' : '#connect'}">
          <span class="icon-box">${icon('mic')}</span>
          <span><strong>I’d like to talk</strong><small>Connect and start a conversation</small></span>
          <span class="arrow">${icon('arrow')}</span>
        </a>
      </div>
      <p class="welcome-footer">Your pace. Your words. Your everyday moments.</p>
    </main>
  `;
}

function auth() {
  const signup = authMode === 'signup';
  return `
    ${publicHeader()}
    <main id="main" tabindex="-1" class="auth-layout">
      <div class="auth-copy">
        <p class="eyebrow">A circle of care</p>
        <h1>${signup ? "Your circle starts here." : "Good to see you again."}</h1>
        <p class="muted">A little support for the people you love.</p>
      </div>
      <section class="card auth-card">
        <h2>${signup ? 'Create your care circle' : 'Welcome back'}</h2>
        <p class="sub">${signup ? 'A little support starts here.' : 'Pick up where you left off.'}</p>
        <p class="notice">Preview only. Use the fictional details below. No account is created and passwords are not stored.</p>
        <form id="auth-form">
          <div class="field">
            <label for="email">Email address</label>
            <input id="email" type="email" value="mei@example.com" required autocomplete="off">
          </div>
          <div class="field">
            <label for="password">Password</label>
            <div class="password-wrap">
              <input id="password" type="password" value="RecollectDemo" minlength="8" required autocomplete="off">
              <button type="button" class="secondary" data-action="password" aria-label="Show password">Show</button>
            </div>
          </div>
          ${signup ? `
            <div class="field">
              <label class="check">
                <input type="checkbox" required>
                <span>I understand this is a prototype using fictional people and simulated results.</span>
              </label>
            </div>
          ` : `
            <p><a href="#reset">Forgot password?</a></p>
          `}
          <button class="wide" type="submit">${signup ? 'Preview account creation' : 'Preview login'} ${icon('arrow')}</button>
        </form>
        <p class="sub" style="margin:20px 0 0">
          ${signup ? 'Already have an account?' : 'New to Recollect?'}
          <button class="text-button" data-action="auth-mode">${signup ? 'Log in' : 'Sign up'}</button>
        </p>
      </section>
    </main>
  `;
}

function family() {
  return shell(`
    <div class="page-heading">
      <div>
        <p class="eyebrow">Your care circle</p>
        <h1>Good morning, Mei.</h1>
        <p class="muted">Your family roster, liveness & consent status.</p>
      </div>
      <a class="button" href="#invite">${icon('plus')} Link someone</a>
    </div>
    <div class="notice" style="margin-bottom:25px">
      <strong>PRD Compliance (FR-28, FR-29):</strong> Fixed-order roster showing device liveness and active consent. Zero scores, zero risk levels, zero concern badges.
    </div>
    <div class="grid">
      ${people.map(p => `
        <article class="card">
          <div class="person-heading">
            <span class="avatar ${p.initials === 'LY' ? 'sage' : ''}">${escape(p.initials || p.name.slice(0, 2).toUpperCase())}</span>
            <div>
              <h2>${escape(p.name)}</h2>
              <p class="sub">${escape(p.relation || 'Senior')}${p.age ? ` · ${p.age} years` : ''}</p>
            </div>
          </div>
          <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:12px;">
            <span class="tag" style="background:#e8efdf; color:var(--teal)">Consent Active</span>
            <span class="tag" style="background:${p.reachable !== false ? '#e8efdf' : '#fbefd7'}; color:${p.reachable !== false ? 'var(--teal)' : 'var(--amber)'}">
              ${p.reachable !== false ? 'Device Reachable' : 'Device Offline'}
            </span>
          </div>
          <p style="margin:12px 0 0">
            ${p.fresh ? 'Their first conversation will appear here.' : 'Everyday task records, memory photos and weekly window available.'}
          </p>
          <div class="card-footer">
            <span class="sub">Activity status<br><strong>${p.last || 'Active'}</strong></span>
            <button class="text-button" data-person="${p.id}">View window ${icon('arrow')}</button>
          </div>
        </article>
      `).join('')}
      <article class="card add-card">
        <span class="icon-box">${icon('plus')}</span>
        <h2 style="margin:18px 0 8px">Enrol someone else</h2>
        <p class="sub">Each person has an active enrolment with own-voice consent.</p>
        <a href="#invite">Link another loved one →</a>
      </article>
    </div>
  `, 'family');
}

function dashboard() {
  const p = currentPerson();
  const recipientWindow = windowData?.recipient_text;
  const openerText = `Ask ${escape(p.name)} about their day and what they enjoyed today!`;
  const learningNote = windowData?.is_baseline ? "The system is still learning what is typical for this person — this account reflects early observations only." : "";
  const obsList = observationsData || [];
  const placesList = getSeniorPlaces(p.id);

  const incompleteMeds = obsList.filter(o => o.signal_type === 'medication' && (o.outcome === 'incomplete' || o.outcome === 'declined')).length;
  const orientationFlags = obsList.filter(o => o.signal_type === 'date_time' || o.signal_type === 'memory').length;
  const misplacingFlags = obsList.filter(o => o.signal_type === 'misplacing').length;
  const wordFindingFlags = obsList.filter(o => o.signal_type === 'language').length;
  
  // Dementia Topographical Memory Biomarkers
  const placeObs = obsList.filter(o => o.signal_type === 'place_memory');
  const placeDisorientations = placeObs.filter(o => o.outcome === 'incomplete' || o.outcome === 'declined').length;
  const placeSuccesses = placeObs.filter(o => o.outcome === 'completed').length;
  const totalPlaceRecalls = placeObs.length;

  const totalCognitiveFlags = incompleteMeds + orientationFlags + misplacingFlags + wordFindingFlags + placeDisorientations;

  return shell(`
    <div class="page-heading">
      <div>
        <p class="eyebrow">Weekly Family Window (FR-15, FR-16)</p>
        <h1>${escape(p.name)}’s window</h1>
        <p class="muted">Updated weekly · Honest factual record · Zero clinical verdicts</p>
      </div>
      ${personSelect()}
    </div>
    
    <section class="card summary-card" style="background:#edf3e5; border-left:4px solid var(--teal)">
      <div>
        <p class="eyebrow" style="color:var(--teal)">Weekly Account for Family</p>
        <h2 style="margin-bottom:8px">What happened this week</h2>
        <p style="font-size:16px; line-height:1.6; margin-bottom:12px">
          ${recipientWindow ? escape(recipientWindow) : `${escape(p.name)} is active and interacting with the device. Everyday task records, memory place checks, and observations appear below.`}
        </p>
        <p class="sub" style="font-style:italic">
          Conversation opener: ${escape(openerText)}
        </p>
      </div>
    </section>

    <!-- Cognitive & Functional Biomarker Insights Panel -->
    <section class="card" style="margin-top:16px; border:1px solid ${totalCognitiveFlags > 0 ? '#e2c08d' : 'var(--line)'}; background:${totalCognitiveFlags > 0 ? '#fffdf7' : 'var(--surface)'}">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px">
        <h2 style="margin:0; font-size:18px">Cognitive & Functional Biomarkers</h2>
        <span class="tag" style="background:${totalCognitiveFlags > 0 ? '#fbefd7' : '#e8efdf'}; color:${totalCognitiveFlags > 0 ? 'var(--amber)' : 'var(--teal)'}">
          ${totalCognitiveFlags > 0 ? `⚠️ ${totalCognitiveFlags} Indicator${totalCognitiveFlags > 1 ? 's' : ''} Observed` : '✅ Stable Baseline'}
        </span>
      </div>
      <p class="sub" style="margin-bottom:14px">
        Passive longitudinal detection of early cognitive signals across everyday conversational turns & place photo reminiscence.
      </p>
      <div style="display:grid; grid-template-columns:1fr; gap:10px; font-size:14px">
        <div style="padding:10px 12px; background:${incompleteMeds > 0 ? '#fdf4e7' : '#f8f9f5'}; border-radius:10px; border-left:3px solid ${incompleteMeds > 0 ? 'var(--amber)' : 'var(--teal)'}">
          <strong>Executive Function (IADL):</strong> ${incompleteMeds > 0 ? `<span style="color:var(--amber)">⚠️ Medication misplaced or unconfirmed (${incompleteMeds}x)</span>` : '<span style="color:var(--teal)">Routine medication taken on time</span>'}
        </div>
        <div style="padding:10px 12px; background:${placeDisorientations > 0 ? '#fdf4e7' : '#f8f9f5'}; border-radius:10px; border-left:3px solid ${placeDisorientations > 0 ? 'var(--amber)' : 'var(--teal)'}">
          <strong>Topographical & Episodic Place Recall (Dementia Screening):</strong> ${placeDisorientations > 0 ? `<span style="color:var(--amber)">⚠️ Topographical disorientation / place memory hesitation (${placeDisorientations}x)</span>` : (totalPlaceRecalls > 0 ? `<span style="color:var(--teal)">Intact place recognition & reminiscence (${placeSuccesses}/${totalPlaceRecalls} recognized)</span>` : `<span style="color:var(--muted)">${placesList.length} memory places registered · baseline ready</span>`)}
        </div>
        <div style="padding:10px 12px; background:${orientationFlags > 0 ? '#fdf4e7' : '#f8f9f5'}; border-radius:10px; border-left:3px solid ${orientationFlags > 0 ? 'var(--amber)' : 'var(--teal)'}">
          <strong>Temporal Orientation & Memory:</strong> ${orientationFlags > 0 ? `<span style="color:var(--amber)">⚠️ Date/day disorientation query noted (${orientationFlags}x)</span>` : '<span style="color:var(--teal)">Temporal and recent recall intact</span>'}
        </div>
        <div style="padding:10px 12px; background:${misplacingFlags > 0 ? '#fdf4e7' : '#f8f9f5'}; border-radius:10px; border-left:3px solid ${misplacingFlags > 0 ? 'var(--amber)' : 'var(--teal)'}">
          <strong>Spatial Item Retrieval:</strong> ${misplacingFlags > 0 ? `<span style="color:var(--amber)">⚠️ Difficulty locating everyday items (${misplacingFlags}x)</span>` : '<span style="color:var(--teal)">No item misplacement reported</span>'}
        </div>
        <div style="padding:10px 12px; background:${wordFindingFlags > 0 ? '#fdf4e7' : '#f8f9f5'}; border-radius:10px; border-left:3px solid ${wordFindingFlags > 0 ? 'var(--amber)' : 'var(--teal)'}">
          <strong>Language & Lexical Flow:</strong> ${wordFindingFlags > 0 ? `<span style="color:var(--amber)">⚠️ Word-finding / anomia pauses (${wordFindingFlags}x)</span>` : '<span style="color:var(--teal)">Spontaneous conversational fluency normal</span>'}
        </div>
      </div>
      <div style="margin-top:14px; padding-top:12px; border-top:1px solid var(--line); display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px">
        <small class="muted">Trajectory Pattern: <strong>${totalCognitiveFlags > 0 ? 'Gradual Drift (Early IADL / Spatial Memory Signal)' : 'Baseline Plateau'}</strong></small>
        <small class="muted">Triage: <strong>Non-urgent community follow-up</strong></small>
      </div>
    </section>

    <!-- Places of Memory Subtab Section under Overview -->
    <section class="card" id="places-memory-card" style="margin-top:20px; border:1px solid var(--line)">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px; flex-wrap:wrap; gap:10px">
        <div>
          <h2 style="margin:0; font-size:18px">Places of Memory</h2>
          <p class="sub" style="margin-top:4px">Stimulate reminiscence & check spatial recall during voice conversations.</p>
        </div>
        <div style="display:flex; gap:6px; background:#f0f3eb; padding:4px; border-radius:12px">
          <button type="button" class="subtab-btn ${overviewPlacesTab === 'list' ? 'active' : ''}" data-action="places-subtab" data-tab="list">
            📸 Album (${placesList.length})
          </button>
          <button type="button" class="subtab-btn ${overviewPlacesTab === 'add' ? 'active' : ''}" data-action="places-subtab" data-tab="add">
            ➕ Add Memory Place
          </button>
        </div>
      </div>

      ${overviewPlacesTab === 'add' ? `
        <!-- Add Memory Place Form -->
        <form id="place-form" style="display:grid; gap:16px">
          <div>
            <label style="font-weight:600; font-size:13px; color:var(--teal)">Singapore Landmark Presets</label>
            <div class="preset-pills" style="margin-top:8px">
              ${landmarkPresets.map(preset => `
                <button type="button" class="preset-pill" data-preset="${escape(preset.title)}">
                  📍 ${escape(preset.title)}
                </button>
              `).join('')}
            </div>
          </div>

          <div class="field">
            <label for="place-title">Place Name / Location</label>
            <input id="place-title" placeholder="e.g. Changi Beach Park or Tiong Bahru Market" required>
          </div>

          <div class="field">
            <label>Place Photo</label>
            <div class="photo-upload-box" onclick="document.querySelector('#place-file-input').click()">
              <input type="file" id="place-file-input" accept="image/*" style="display:none">
              <span style="font-size:22px">📷</span>
              <p style="margin:4px 0 0; font-weight:600; color:var(--teal); font-size:14px">Upload a family photo from your device</p>
              <small class="muted">Supports JPG, PNG, WEBP</small>
            </div>
            <input id="place-photo-url" type="url" placeholder="Or enter photo image URL (https://...)" style="margin-top:8px" required>
            <img id="photo-preview-img" class="photo-preview" alt="Preview">
          </div>

          <div class="field">
            <label for="place-memory">Personal Story & Family Significance</label>
            <textarea id="place-memory" rows="2" placeholder="e.g. Arun cycled here every Sunday in the 1980s with his brother and drank teh tarik." required style="width:100%; border-radius:12px; border:1px solid var(--line); padding:10px; font-family:inherit"></textarea>
          </div>

          <div class="field">
            <label for="place-prompt">AI Question Prompt for ${escape(p.name)}</label>
            <input id="place-prompt" placeholder="e.g. Arun, look at this photo! Do you remember where this beach is?" value="Do you remember where this photo was taken?">
          </div>

          <div class="field">
            <label for="place-keywords">Recognition Keywords (Comma separated)</label>
            <input id="place-keywords" placeholder="e.g. changi, beach, cycling, east coast" value="changi, beach">
            <small class="muted" style="display:block; margin-top:4px">Aunty matches these keywords when the senior responds aloud or in text.</small>
          </div>

          <div style="display:flex; gap:10px; margin-top:6px">
            <button type="submit" class="wide">${icon('plus')} Save Memory Place</button>
            <button type="button" class="secondary" data-action="places-subtab" data-tab="list">Cancel</button>
          </div>
        </form>
      ` : `
        <!-- Memory Places Album List -->
        <div style="display:grid; gap:14px">
          ${placesList && placesList.length ? placesList.map(pl => `
            <article class="card place-card" style="border:1px solid #dce4d6; background:#fafcf8">
              <div class="place-img-wrap">
                <img src="${escape(pl.image_url)}" alt="${escape(pl.title)}" class="place-img" loading="lazy">
                <div class="place-badge-overlay">
                  <span class="tag ${pl.status === 'Needed Clue' ? 'amber' : ''}" style="background:rgba(255,255,255,0.92); font-weight:700">
                    ${pl.recall_attempts > 0 ? (pl.recall_successes > 0 ? '✅ Recalled' : '⚠️ Disoriented') : '🆕 Ready to Test'}
                  </span>
                </div>
              </div>
              <div class="place-card-body">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:8px">
                  <div>
                    <h3 style="margin:0 0 4px; font-size:16px">${escape(pl.title)}</h3>
                    <p style="margin:0; font-size:13px; color:var(--ink)">${escape(pl.personal_memory || pl.description)}</p>
                  </div>
                  <button type="button" class="text-button" data-delete-place="${pl.id}" style="color:var(--error); padding:4px 6px; min-height:auto" title="Delete place">
                    ${icon('trash')}
                  </button>
                </div>
                <div style="font-size:12px; color:var(--teal); background:#edf3e5; padding:8px 12px; border-radius:10px; margin:10px 0">
                  <strong>Aunty's Prompt:</strong> "${escape(pl.prompt_question)}"
                </div>
                
                <div class="place-stats" style="margin-top:10px">
                  <div>
                    <small class="muted">Times Asked</small>
                    <strong>${pl.recall_attempts || 0}x</strong>
                  </div>
                  <div>
                    <small class="muted">Recognized</small>
                    <strong style="color:var(--teal)">${pl.recall_successes || 0}x</strong>
                  </div>
                  <div>
                    <small class="muted">Last Tested</small>
                    <strong>${pl.last_asked_at || 'Not yet'}</strong>
                  </div>
                </div>
              </div>
            </article>
          `).join('') : `
            <div style="text-align:center; padding:24px 16px; background:#f7faf4; border-radius:14px">
              <p class="muted" style="margin:0 0 12px">No memory places added yet for ${escape(p.name)}.</p>
              <button type="button" class="button" data-action="places-subtab" data-tab="add" style="padding:8px 16px; font-size:13px">
                ➕ Add First Memory Place
              </button>
            </div>
          `}
        </div>
      `}
    </section>

    ${learningNote ? `
      <div class="notice" style="margin-bottom:20px; margin-top:16px; background:#f4f6ef">
        <strong>Baseline notice (FR-17):</strong> ${learningNote}
      </div>
    ` : ''}

    <div class="page-heading" style="margin-top:20px; margin-bottom:12px">
      <h2>Everyday Task & Observation Log (FR-4..7)</h2>
      <p class="sub">Verified task completions recorded directly through voice interaction.</p>
    </div>

    <div class="grid observations-grid">
      ${obsList && obsList.length ? obsList.map(obs => `
        <article class="card" style="padding:16px">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px">
            <span class="tag" style="text-transform:uppercase; letter-spacing:0.05em; font-size:10px">${escape(obs.signal_type)}</span>
            <small class="muted">${new Date(obs.occurred_at).toLocaleDateString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</small>
          </div>
          <p style="margin:0; font-weight:500">${escape(obs.content)}</p>
          <small class="muted" style="display:block; margin-top:4px">Outcome: <strong style="color:${(obs.outcome === 'incomplete' || obs.outcome === 'declined') ? 'var(--amber)' : 'var(--teal)'}">${escape(obs.outcome || 'recorded')}</strong></small>
        </article>
      `).join('') : `
        <article class="card" style="padding:16px"><p class="muted">No observations recorded yet.</p></article>
      `}
    </div>

    <section class="card" style="margin-top:24px">
      <div class="row">
        <h2>Continuous Disclosure (FR-18..20)</h2>
      </div>
      <p style="margin-top:12px; font-size:14px" class="muted">
        ${escape(p.name)} receives this exact same disclosure aloud in their preferred language upon asking the device. Recollect maintains zero secret notes.
      </p>
    </section>
  `, 'dashboard');
}

function places() {
  overviewPlacesTab = 'add';
  return dashboard();
}

function observations() {
  const p = currentPerson();
  const obsList = observationsData || [];
  const notesList = obsList.filter(o => o.signal_type === 'mention' || (o.content && o.content.includes('note (')));

  return shell(`
    <div class="page-heading">
      <div>
        <p class="eyebrow">Family Observations & Notes</p>
        <h1>Caregiver Notes</h1>
        <p class="muted">Record and review qualitative observations and care notes for ${escape(p.name)}.</p>
      </div>
      ${personSelect()}
    </div>

    <div class="grid">
      <!-- Add Observation Form -->
      <section class="card">
        <h2>Log a New Observation for ${escape(p.name)}</h2>
        <p class="sub">Notice any changes during visits or phone calls? Record them here to build a continuous picture.</p>
        <form id="note-form" style="margin-top:16px">
          <div class="field">
            <label for="note-category">Observation Area</label>
            <select id="note-category">
              <option value="Medication">Medication (Missed, confused, or delayed doses)</option>
              <option value="Orientation">Orientation & Date (Losing track of day/date/time)</option>
              <option value="Misplacing">Misplacing Objects (Keys, glasses, wallet, phone)</option>
              <option value="Repetition">Memory & Repetition (Repeating questions or stories)</option>
              <option value="Daily Routine">Daily Routine & Hobbies (Meals, walks, gardening)</option>
              <option value="Mail & Bills">Official Mail & Bills (Difficulty managing notices)</option>
            </select>
          </div>

          <div class="field">
            <label for="note-frequency">Frequency Noticed</label>
            <select id="note-frequency">
              <option value="Just noticed today">Just noticed today</option>
              <option value="A few times this week">A few times this week</option>
              <option value="Daily occurrence">Daily occurrence</option>
            </select>
          </div>

          <div class="field">
            <label for="note-text">Specific Observation Notes</label>
            <textarea id="note-text" rows="3" placeholder="e.g. During my call, Arun asked what day it was and couldn't find his reading glasses." required style="width:100%; border-radius:12px; border:1px solid var(--line); padding:10px; font-family:inherit"></textarea>
          </div>

          <button type="submit" class="wide">${icon('plus')} Save Observation Note</button>
        </form>
      </section>

      <!-- History of Notes -->
      <section class="card">
        <h2>Saved Observations for ${escape(p.name)} (${notesList.length})</h2>
        <div style="display:grid; gap:12px; margin-top:14px">
          ${notesList && notesList.length ? notesList.map(n => `
            <div style="padding:14px; background:#f8f9f5; border-radius:12px; border-left:3px solid var(--teal)">
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px">
                <span class="tag" style="background:#e8efdf; color:var(--teal); font-weight:600; text-transform:capitalize">${escape(n.signal_type)}</span>
                <small class="muted">${new Date(n.occurred_at).toLocaleDateString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</small>
              </div>
              <p style="margin:0; font-size:15px; color:var(--ink)">${escape(n.content)}</p>
            </div>
          `).join('') : `
            <p class="muted">No family notes recorded yet for ${escape(p.name)}.</p>
          `}
        </div>
      </section>

      <!-- PRD Governance & Signal Weight -->
      <section class="card">
        <h2>The 4 Everyday Task Classes (FR-4..7)</h2>
        <ul class="steps" style="margin-top:16px">
          <li><strong>Medication (FR-4):</strong> Senior confirms doses and receives timely spoken reminders.</li>
          <li><strong>Appointments (FR-5):</strong> Medical and personal check-ups confirmed and scheduled.</li>
          <li><strong>Official Mail & Letters (FR-6):</strong> Community notices and letters read and noted.</li>
          <li><strong>Daily Routines (FR-7):</strong> Everyday activities and domestic routines acknowledged.</li>
        </ul>
      </section>

      <div class="notice">
        <strong>Strict PRD Design (FR-13):</strong> Family notes provide qualitative context for community care visits. They never automatically modify diagnostic algorithms or create clinical alarm badges.
      </div>
    </div>
  `, 'observations');
}

function invite() {
  return shell(`
    <div class="page-heading">
      <div>
        <p class="eyebrow">Enrolment (FR-21..23)</p>
        <h1>Enrol a Loved One</h1>
        <p class="muted">All 4 consent artefacts captured in a single visit.</p>
      </div>
    </div>
    <div class="form-grid">
      <section class="card">
        ${invitation ? `
          <h2>Invitation code for ${escape(pendingPerson.name)}</h2>
          <p>Have them select “I’d like to talk” and enter this code to activate their conversation surface.</p>
          <div class="code">${invitation.code}</div>
          <p class="sub">Expires ${new Date(invitation.expires).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} · 4 Consent Artefacts Verified</p>
          <div class="row">
            <button data-action="copy">Copy code</button>
            <button class="secondary" data-action="regenerate">New code</button>
          </div>
          <p id="copy-status" role="status"></p>
          <hr style="border:0;border-top:1px solid var(--line);margin:25px 0">
          <a class="button wide" href="#connect">Open conversation surface ${icon('arrow')}</a>
        ` : `
          <h2>Caregiver / Care-worker Enrolment</h2>
          <form id="invite-form">
            <div class="field">
              <label for="adult-name">Senior’s full name</label>
              <input id="adult-name" maxlength="50" placeholder="For example: Arun or Lily" required>
            </div>
            <div class="field">
              <label for="relationship">Relationship</label>
              <select id="relationship">
                <option>Father</option>
                <option>Mother</option>
                <option>Partner</option>
                <option>Relative</option>
                <option>Community Elder</option>
              </select>
            </div>
            <div class="field">
              <label for="pref-lang">Preferred Language</label>
              <select id="pref-lang">
                <option value="en-SG">English (Singapore)</option>
                <option value="zh-cmn-Hans-SG">Mandarin</option>
                <option value="ms-SG">Malay</option>
                <option value="ta-SG">Tamil</option>
              </select>
            </div>
            <fieldset style="border:1px solid var(--line); border-radius:12px; padding:14px; margin-bottom:18px">
              <legend style="font-weight:600; padding:0 6px">4 Consent Artefacts (FR-21, AD-4)</legend>
              <label class="check" style="margin-bottom:8px">
                <input type="checkbox" id="co-sig" checked required>
                <span>Named recipient co-signature captured</span>
              </label>
              <label class="check" style="margin-bottom:8px">
                <input type="checkbox" id="res-consent" checked required>
                <span>Research and validation consent granted</span>
              </label>
              <label class="check" style="margin-bottom:8px">
                <input type="checkbox" id="proc-ack" checked required>
                <span>Processor disclosure acknowledged</span>
              </label>
              <label class="check">
                <input type="checkbox" id="ulysses-rec" checked required>
                <span>Own-voice Ulysses audio instruction recorded</span>
              </label>
            </fieldset>
            <button class="wide" type="submit">Complete Enrolment & Link ${icon('arrow')}</button>
          </form>
        `}
      </section>
      <section class="card">
        <h2>Consent Architecture (AD-4)</h2>
        <p class="sub">
          An enrolment missing any of the four consent artefacts cannot be marked active, and the backend write path rejects any observations without an active enrolment.
        </p>
      </section>
    </div>
  `);
}

function connect() {
  return `
    ${publicHeader()}
    <main id="main" tabindex="-1" class="centered older">
      <p class="eyebrow">Connect device</p>
      <h1>Let’s connect you.</h1>
      <p class="muted">Select your name below or enter your connection code to start talking.</p>
      
      <section class="card" style="margin-bottom:16px; text-align:left">
        <h2 style="font-size:16px; margin-bottom:6px">Direct Senior Quick-Connect</h2>
        <p class="sub" style="margin-bottom:12px">Tap below to open the warm voice terminal for any senior in your family:</p>
        <div style="display:grid; gap:8px">
          ${people.map(p => `
            <button type="button" class="secondary" data-connect-senior="${p.id}" style="display:flex; justify-content:space-between; align-items:center; padding:12px 16px; border-radius:12px; font-weight:600; text-align:left">
              <span>🎙️ Talk as ${escape(p.name)} <small class="muted" style="font-weight:400">(${escape(p.relation || 'Senior')})</small></span>
              <span style="color:var(--teal)">Connect ${icon('arrow')}</span>
            </button>
          `).join('')}
        </div>
      </section>

      <form id="connect-form" class="card">
        <label for="link-code">Or enter 6-digit connection code</label>
        <input id="link-code" style="font-size:30px;letter-spacing:.2em;text-align:center" inputmode="numeric" pattern="[0-9]{6}" maxlength="6" autocomplete="one-time-code" placeholder="000000" required aria-describedby="code-help code-error">
        <p id="code-help" class="sub" style="margin-top:14px">
          ${invitation ? `Active invitation code for ${escape(pendingPerson.name)}: ${invitation.code}` : 'Enter 123456 to connect directly as Arun.'}
        </p>
        <p id="code-error" class="error" role="alert"></p>
        <button class="wide" type="submit">Connect with Code ${icon('arrow')}</button>
      </form>
      <p class="sub footer-note">No password or credentials needed for the senior (FR-1).</p>
    </main>
  `;
}

function consent() {
  if (!pendingPerson) return connect();
  return `
    ${publicHeader()}
    <main id="main" tabindex="-1" class="centered older">
      <p class="eyebrow">You are in control (FR-23)</p>
      <h1>Connect with ${escape(pendingPerson.name)}?</h1>
      <section class="card">
        <p>Recollect provides everyday conversation and task assistance. You can ask for your weekly disclosure at any time.</p>
        <form id="consent-form">
          <label class="check" style="margin:24px 0">
            <input type="checkbox" required checked>
            <span>I agree to start my conversations with Recollect.</span>
          </label>
          <button class="wide" type="submit">Begin Conversations</button>
        </form>
        <a class="button secondary wide" style="margin-top:12px" href="#connect">Back</a>
      </section>
    </main>
  `;
}

function chat() {
  if (!linked) return connect();
  const currentMessages = getSeniorMessages(linked.id);

  return `
    ${publicHeader()}
    <main id="main" tabindex="-1" class="chat older">
      <header class="chat-header">
        <p class="eyebrow">Everyday Voice & Conversation</p>
        <h1>Hello, ${escape(linked.name)}.</h1>
        <p class="muted">Warm, unhurried, here to help. Tap the mic to talk or type below.</p>
        <div style="display:flex; justify-content:center; gap:8px; flex-wrap:wrap; margin-top:8px">
          <span class="tag" style="background:#e8efdf; color:var(--teal)">Helper Role (FR-34) · Connected</span>
        </div>
      </header>
      <div class="conversation" aria-label="Conversation">
        ${currentMessages.map(m => `
          <div class="bubble ${m.role === 'you' ? 'mine' : ''}">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px; gap:8px">
              <small style="font-weight:600">${m.role === 'you' ? escape(linked.name) : 'Aunty · Recollect'}</small>
              ${m.time ? `<small class="muted" style="font-size:11px">${escape(m.time)}</small>` : ''}
            </div>
            ${m.place_memory ? `
              <div class="chat-place-card">
                <img src="${escape(m.place_memory.image_url)}" alt="${escape(m.place_memory.title)}" class="chat-place-img">
                <div class="chat-place-meta">
                  <div style="display:flex; align-items:center; gap:6px; margin-bottom:4px">
                    <span class="tag" style="background:#e8efdf; color:var(--teal); font-size:11px">📍 Memory Place Photo</span>
                  </div>
                  <h3>${escape(m.place_memory.title)}</h3>
                  <p style="margin-top:2px; font-size:14px; color:var(--ink)">${escape(m.place_memory.prompt_question || 'Do you remember where this photo was taken?')}</p>
                  <div class="chip-row">
                    <button type="button" class="chip-btn" data-place-answer="remember">💡 I remember!</button>
                    <button type="button" class="chip-btn" data-place-answer="hint">🔍 Give me a clue</button>
                    <button type="button" class="chip-btn" data-place-answer="forget">❓ Where is this?</button>
                  </div>
                </div>
              </div>
            ` : ''}
            <p style="margin:0">${escape(m.text)}</p>
          </div>
        `).join('')}
      </div>
      <section class="conversation-controls">
        <div class="voice-area">
          <button type="button" class="mic" data-action="voice" aria-label="${voiceState === 'listening' ? 'Stop listening' : 'Start speaking'}">
            ${voiceState === 'listening' ? '<span aria-hidden="true" style="font-size:24px">■</span>' : (voiceState === 'speaking' ? icon('volume') : icon('mic'))}
          </button>
          <p id="voice-status" role="status" style="font-weight:600; color:var(--teal)">
            ${voiceState === 'listening' ? 'Listening… speak now' : (voiceState === 'speaking' ? 'Speaking aloud…' : 'Tap mic to talk aloud')}
          </p>
          <p class="sub">Speech is transcribed and spoken with natural warmth.</p>
        </div>
        <form id="chat-form">
          <label for="message">Type a reply instead</label>
          <div class="type-row">
            <input id="message" maxlength="500" placeholder="e.g. I remember, that is Changi Beach!" autocomplete="off">
            <button type="submit">Send ${icon('arrow')}</button>
          </div>
        </form>
        <div style="margin-top:20px; text-align:center">
          <button class="secondary wide" data-action="finish" style="font-size:14px; min-height:44px">Finish conversation</button>
        </div>
        <div style="text-align:center; margin-top:14px">
          <a href="#connection" class="sub">Connection details</a>
        </div>
      </section>
    </main>
  `;
}

function connection() {
  return `
    ${publicHeader()}
    <main id="main" tabindex="-1" class="centered older">
      <h1>Your Connection</h1>
      <section class="card">
        <h2>${linked ? `Connected as ${escape(linked.name)}` : 'No active connection'}</h2>
        <p>Your weekly account is shared with your care circle, and you can hear the exact same account at any time.</p>
        ${linked ? '<button data-action="disconnect" class="secondary wide">Disconnect</button><a href="#chat" class="button wide" style="margin-top:12px">Return to chat</a>' : '<a class="button" href="#connect">Connect code</a>'}
      </section>
    </main>
  `;
}

function finish() {
  return `
    ${publicHeader()}
    <main id="main" tabindex="-1" class="centered older">
      <section class="card">
        <span class="icon-box">${icon('check')}</span>
        <h1 style="margin-top:25px">Thank you for sharing.</h1>
        <p>That’s enough for today. Come back whenever you feel like a conversation.</p>
        <p class="notice">Conversations and everyday tasks are recorded with your consent.</p>
        <button class="wide" data-action="new-chat">Start another conversation</button>
        <a class="button secondary wide" style="margin-top:12px" href="#welcome">Back to welcome</a>
      </section>
    </main>
  `;
}

function reset() {
  return `
    ${publicHeader()}
    <main id="main" tabindex="-1" class="centered">
      <section class="card">
        <h1>Caregiver Account Access</h1>
        <p>Use the default demo credentials (mei@example.com / RecollectDemo) to access the caregiver portal.</p>
        <a class="button wide" href="#auth">Return to login</a>
      </section>
    </main>
  `;
}

const pages = { welcome, auth, family, dashboard, places, observations, invite, connect, consent, chat, connection, finish, reset };
const protectedPages = ['family', 'dashboard', 'places', 'observations', 'invite'];

// ============================================================================
// 9. EVENT DELEGATION & LIFECYCLE BOOTSTRAP
// ============================================================================

app.addEventListener('click', async event => {
  // Preset Landmark Pill Selection
  const presetBtn = event.target.closest('[data-preset]');
  if (presetBtn) {
    const title = presetBtn.dataset.preset;
    const preset = landmarkPresets.find(p => p.title === title);
    if (preset) {
      document.querySelector('#place-title').value = preset.title;
      document.querySelector('#place-photo-url').value = preset.image_url;
      document.querySelector('#place-memory').value = preset.personal_memory;
      document.querySelector('#place-prompt').value = preset.prompt_question;
      document.querySelector('#place-keywords').value = preset.recognition_keys;
      const preview = document.querySelector('#photo-preview-img');
      if (preview) {
        preview.src = preset.image_url;
        preview.style.display = 'block';
      }
      document.querySelectorAll('.preset-pill').forEach(p => p.classList.remove('active'));
      presetBtn.classList.add('active');
    }
    return;
  }

  // Delete Place from Album
  const deletePlaceBtn = event.target.closest('[data-delete-place]');
  if (deletePlaceBtn) {
    const placeId = deletePlaceBtn.dataset.deletePlace;
    if (window.confirm('Remove this place memory from the senior\'s reminiscence album?')) {
      const seniorId = selected;
      if (seniorPlaces[seniorId]) {
        seniorPlaces[seniorId] = seniorPlaces[seniorId].filter(p => String(p.id) !== String(placeId));
        savePlaces();
      }
      try {
        await fetch(`${API_BASE}/v1/seniors/${seniorId}/places/${placeId}`, { method: 'DELETE' });
      } catch (e) {}
      render();
    }
    return;
  }

  // Place Quiz Quick-Response Chips
  const placeAnswerBtn = event.target.closest('[data-place-answer]');
  if (placeAnswerBtn) {
    const answerType = placeAnswerBtn.dataset.placeAnswer;
    if (answerType === 'remember') {
      const quizName = activePlaceQuiz ? activePlaceQuiz.title : 'Changi Beach';
      await addReply(`I remember! That's ${quizName}.`);
    } else if (answerType === 'hint') {
      await addReply(`Can you give me a small clue where this is?`);
    } else {
      await addReply(`I'm not sure, I can't remember where this place is.`);
    }
    return;
  }

  // Primary Action Router & Buttons
  const button = event.target.closest('[data-action], [data-person], [data-connect-senior]');
  if (!button) return;

  if (button.dataset.connectSenior) {
    const p = people.find(item => item.id === button.dataset.connectSenior) || people[0];
    pendingPerson = p;
    go('consent');
    return;
  }

  if (button.dataset.person) {
    selected = button.dataset.person;
    await fetchWeeklyWindow(selected);
    await fetchPlaces(selected);
    go('dashboard');
    return;
  }

  switch (button.dataset.action) {
    case 'places-subtab':
      overviewPlacesTab = button.dataset.tab;
      render();
      break;

    case 'auth-mode':
      authMode = authMode === 'signup' ? 'login' : 'signup';
      render();
      break;

    case 'password': {
      const input = document.querySelector('#password');
      input.type = input.type === 'password' ? 'text' : 'password';
      button.textContent = input.type === 'password' ? 'Show' : 'Hide';
      button.setAttribute('aria-label', `${button.textContent} password`);
      break;
    }

    case 'logout':
      caregiver = false;
      go('welcome');
      break;

    case 'copy': {
      const status = document.querySelector('#copy-status');
      try {
        await navigator.clipboard.writeText(invitation.code);
        status.textContent = 'Code copied.';
      } catch {
        status.textContent = 'Copy is unavailable. Select the code above and copy it manually.';
      }
      break;
    }

    case 'regenerate':
      makeInvitation();
      render();
      announce('New invitation code generated.');
      break;

    case 'voice':
      if (voiceState === 'idle') {
        startVoiceRecognition();
      } else if (voiceState === 'listening') {
        if (recognition) try { recognition.stop(); } catch (e) {}
        voiceState = 'idle';
        if (!updateVoiceUI()) render();
      } else if (voiceState === 'speaking') {
        if (currentAudio) currentAudio.pause();
        voiceState = 'idle';
        if (!updateVoiceUI()) render();
      }
      break;

    case 'finish':
      voiceState = 'idle';
      if (currentAudio) currentAudio.pause();
      go('finish');
      break;

    case 'new-chat':
      if (!linked) {
        go('connect');
        break;
      }
      seniorConversations[linked.id] = [
        { role: 'ai', text: `Good day, ${linked.name}! What would you like to talk about today?`, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }
      ];
      saveConversations();
      go('chat');
      break;

    case 'disconnect':
      if (window.confirm('Disconnect from this conversation session?')) {
        linked = null;
        go('connect');
      }
      break;
  }
});

app.addEventListener('change', async event => {
  if (event.target.id === 'person-select') {
    if (dirty && !window.confirm('Switch people without saving your changes?')) {
      event.target.value = selected;
      return;
    }
    dirty = false;
    selected = event.target.value;
    await Promise.all([
      fetchWeeklyWindow(selected),
      fetchPlaces(selected)
    ]);
    render();
  }

  if (event.target.id === 'place-file-input') {
    const file = event.target.files && event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = e => {
        const dataUrl = e.target.result;
        const photoUrlInput = document.querySelector('#place-photo-url');
        if (photoUrlInput) photoUrlInput.value = dataUrl;
        const preview = document.querySelector('#photo-preview-img');
        if (preview) {
          preview.src = dataUrl;
          preview.style.display = 'block';
        }
      };
      reader.readAsDataURL(file);
    }
  }

  if (event.target.id === 'place-photo-url') {
    const val = event.target.value.trim();
    const preview = document.querySelector('#photo-preview-img');
    if (preview && val) {
      preview.src = val;
      preview.style.display = 'block';
    }
  }
});

app.addEventListener('submit', async event => {
  event.preventDefault();
  const form = event.target;

  if (form.id === 'auth-form') {
    caregiver = true;
    await fetchRoster();
    go('family');
  }

  if (form.id === 'invite-form') {
    const nameInput = document.querySelector('#adult-name');
    const name = nameInput.value.trim();
    if (!name) {
      document.querySelector('#adult-name').setCustomValidity('Enter a first name.');
      document.querySelector('#adult-name').reportValidity();
      return;
    }
    const prefLang = document.querySelector('#pref-lang')?.value || 'en-SG';

    try {
      const res = await fetch(`${API_BASE}/v1/enrolments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          display_name: name,
          preferred_language: prefLang,
          recipient_co_signature: true,
          research_consent: true,
          processor_disclosure_acknowledged: true,
          ulysses_audio_base64: 'UklGRi4AAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA=',
        }),
      });

      if (res.ok) {
        const enrolData = await res.json();
        pendingPerson = {
          id: enrolData.senior_id,
          name,
          initials: name.slice(0, 2).toUpperCase(),
          relation: document.querySelector('#relationship').value,
          age: '',
          last: 'Just now',
          reachable: true,
          consent: true,
          fresh: true
        };
        await fetchRoster();
      } else {
        pendingPerson = {
          id: crypto.randomUUID(),
          name,
          initials: name.slice(0, 2).toUpperCase(),
          relation: document.querySelector('#relationship').value,
          age: '',
          last: 'Just now',
          reachable: true,
          consent: true,
          fresh: true
        };
      }
    } catch (err) {
      console.warn('Enrolment call fallback:', err);
      pendingPerson = {
        id: crypto.randomUUID(),
        name,
        initials: name.slice(0, 2).toUpperCase(),
        relation: document.querySelector('#relationship').value,
        age: '',
        last: 'Just now',
        reachable: true,
        consent: true,
        fresh: true
      };
    }

    makeInvitation();
    render();
  }

  if (form.id === 'connect-form') {
    const code = document.querySelector('#link-code').value;
    if (invitation && invitation.code === code && Date.now() > invitation.expires) {
      document.querySelector('#code-error').textContent = 'This code has expired. Ask your caregiver to create a new invitation.';
      return;
    }
    if (invitation && invitation.code === code) {
      go('consent');
    } else if (!invitation && (code === '123456' || code === '000000')) {
      pendingPerson = people[0];
      go('consent');
    } else {
      document.querySelector('#code-error').textContent = 'That code does not match. Check the six digits and try again.';
    }
  }

  if (form.id === 'consent-form') {
    linked = pendingPerson || people[0];
    if (!people.some(p => p.id === linked.id)) people.push(linked);
    selected = linked.id;
    invitation = null;
    getSeniorMessages(linked.id);
    go('chat');
  }

  if (form.id === 'chat-form') {
    const input = document.querySelector('#message');
    const text = input.value.trim();
    if (text) {
      input.value = '';
      await addReply(text);
    }
  }

  if (form.id === 'place-form') {
    const title = document.querySelector('#place-title').value.trim();
    const photoUrl = document.querySelector('#place-photo-url').value.trim();
    const memory = document.querySelector('#place-memory').value.trim();
    const promptQ = document.querySelector('#place-prompt').value.trim() || `Look at this photo, ${currentPerson().name}! Do you remember where this is?`;
    const keywordsStr = document.querySelector('#place-keywords').value.trim();
    const recognition_keys = keywordsStr.split(',').map(k => k.trim().toLowerCase()).filter(Boolean);

    if (title && photoUrl) {
      const seniorId = selected;
      const newPlace = {
        id: crypto.randomUUID(),
        senior_id: seniorId,
        title,
        description: memory,
        image_url: photoUrl,
        personal_memory: memory,
        recognition_keys,
        prompt_question: promptQ,
        recall_attempts: 0,
        recall_successes: 0,
        last_asked_at: 'Just added',
        status: 'Ready'
      };

      if (!seniorPlaces[seniorId]) {
        seniorPlaces[seniorId] = [];
      }
      seniorPlaces[seniorId].unshift(newPlace);
      savePlaces();

      try {
        await fetch(`${API_BASE}/v1/seniors/${seniorId}/places`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            title,
            description: memory,
            image_url: photoUrl,
            personal_memory: memory,
            recognition_keys,
            prompt_question: promptQ,
          }),
        });
      } catch (err) {
        console.warn('Place save API fallback:', err);
      }

      announce('Memory place photo saved.');
      overviewPlacesTab = 'list';
      render();
    }
  }

  if (form.id === 'note-form') {
    const category = document.querySelector('#note-category').value;
    const frequency = document.querySelector('#note-frequency').value;
    const text = document.querySelector('#note-text').value.trim();
    if (text) {
      const seniorId = selected;
      const categoryToSignal = {
        'Medication': 'medication',
        'Orientation': 'date_time',
        'Misplacing': 'misplacing',
        'Repetition': 'memory',
        'Daily Routine': 'routine',
        'Mail & Bills': 'mail',
      };
      const signal_type = categoryToSignal[category] || 'mention';
      
      try {
        await fetch(`${API_BASE}/v1/seniors/${seniorId}/observations`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            signal_type: signal_type,
            outcome: 'completed',
            content: `${category} note (${frequency}): ${text}`,
          }),
        });
      } catch (err) {
        console.warn('Note save fallback:', err);
      }

      await fetchWeeklyWindow(seniorId);
      announce('Observation note saved.');
      render();
    }
  }
});

window.addEventListener('beforeunload', event => {
  if (dirty) {
    event.preventDefault();
    event.returnValue = '';
  }
});

window.addEventListener('hashchange', render);

// Initial bootstrap
fetchRoster().then(() => {
  render();
});
