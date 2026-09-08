const app = document.querySelector('#app');
const icons = {
  people: '<circle cx="9" cy="8" r="3"/><path d="M3 21v-3a6 6 0 0 1 12 0v3M17 5a3 3 0 0 1 0 6m1 4a5 5 0 0 1 3 5"/>',
  home: '<path d="m3 10 9-7 9 7v11H3zM9 21v-8h6v8"/>',
  note: '<rect x="4" y="3" width="16" height="19" rx="3"/><path d="M8 8h8M8 12h8M8 16h5"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  arrow: '<path d="M4 12h16m-6-6 6 6-6 6"/>',
  leaf: '<path d="M4 20C1 8 10 3 21 3c0 11-5 19-17 17Zm0 0L16 8"/>',
  mic: '<rect x="8" y="2" width="8" height="13" rx="4"/><path d="M5 10v2a7 7 0 0 0 14 0v-2M12 19v3M8 22h8"/>',
  check: '<path d="m5 12 4 4L20 5"/>',
};
const icon = name => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${icons[name] || icons.leaf}</svg>`;
const escape = value => String(value).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const people = [
  { id: 'arun', name: 'Arun', initials: 'AR', relation: 'Father', age: '72', last: 'Today, 9:30 am', sessions: 5, attention: true, concerns: [], notes: '', frequency: 'Sometimes', since: '', fresh: false },
  { id: 'lily', name: 'Lily', initials: 'LY', relation: 'Mother', age: '68', last: 'Yesterday, 4:15 pm', sessions: 4, attention: false, concerns: [], notes: '', frequency: 'Sometimes', since: '', fresh: false },
];
const concerns = ['Repeating questions or stories', 'Difficulty finding words', 'Forgetting recent events or appointments', 'Changes in familiar daily tasks', 'Changes in mood or behaviour', 'Something else'];
let caregiver = false;
let selected = 'arun';
let linked = null;
let pendingPerson = null;
let invitation = null;
let messages = [];
let authMode = 'signup';
let voiceState = 'idle';
let dirty = false;
let lastRoute = '';
const currentPerson = () => people.find(p => p.id === selected) || people[0];
const brand = () => '<a class="brand" href="#welcome" aria-label="Recollect home"><span class="mark" aria-hidden="true"></span>recollect</a>';
const publicHeader = () => `<header class="public-header">${brand()}<a class="text-button" href="#welcome">Back to welcome</a></header>`;
const announce = text => { document.querySelector('#announcement').textContent = text; };
const go = path => { location.hash = path; };
function shell(content, active = 'family') {
  return `<div class="shell"><aside class="sidebar">${brand()}<p class="eyebrow" style="margin:0 12px">Your care circle</p><nav aria-label="Caregiver navigation">
    <a class="nav-link ${active === 'family' ? 'active' : ''}" ${active === 'family' ? 'aria-current="page"' : ''} href="#family">${icon('people')} Your family</a>
    <a class="nav-link ${active === 'dashboard' ? 'active' : ''}" ${active === 'dashboard' ? 'aria-current="page"' : ''} href="#dashboard">${icon('home')} Overview</a>
    <a class="nav-link ${active === 'observations' ? 'active' : ''}" ${active === 'observations' ? 'aria-current="page"' : ''} href="#observations">${icon('note')} Observations</a>
    </nav><div class="sidebar-bottom"><div class="notice">Little moments can help you stay connected.</div><div class="account"><span class="avatar sage">MC</span><p><strong>Mei Chen</strong><br><span class="sub">Demo caregiver</span></p></div></div></aside>
    <div class="workspace"><header class="topbar"><span>Family care, thoughtfully connected</span><button class="text-button" data-action="logout">Exit demo</button></header><main id="main" tabindex="-1" class="main-content">${content}<p class="footer-note">Demo only · Fictional observations and illustrative recommendations. Recollect does not diagnose dementia.</p></main></div></div>`;
}
function personSelect() {
  return `<div class="person-select"><label for="person-select">Viewing updates for</label><select id="person-select">${people.map(p => `<option value="${p.id}" ${p.id === selected ? 'selected' : ''}>${escape(p.name)}</option>`).join('')}</select></div>`;
}
function welcome() {
  return `${publicHeader()}<main id="main" tabindex="-1" class="hero"><div><p class="eyebrow">Every conversation is a connection</p><h1>A little closer.<br><em>Every day.</em></h1><p class="intro muted">A thoughtful space for everyday conversations, and a clearer picture for the people who care.</p><div class="role-list"><a class="role button" href="#auth"><span class="icon-box">${icon('people')}</span><span><strong>I’m supporting someone</strong><small>Stay connected with your loved ones</small></span><span class="arrow">${icon('arrow')}</span></a><a class="role button" href="${linked ? '#chat' : '#connect'}"><span class="icon-box">${icon('mic')}</span><span><strong>I’m here for a conversation</strong><small>A moment to talk about your day</small></span><span class="arrow">${icon('arrow')}</span></a></div><p class="sub">Your pace. Your words. Your everyday moments.</p></div><div class="story-panel"><div class="garden" aria-hidden="true"><span class="sun"></span><span class="hill"></span><span class="hill two"></span><span class="plant"></span></div><p class="display">Small moments.<br>Meaningful connections.</p><div class="quote"><p>“Dad told me about his morning walk.<br>Sometimes, that’s where care begins.”</p><small>Mei · fictional caregiver persona</small></div></div></main>`;
}
function auth() {
  const signup = authMode === 'signup';
  return `${publicHeader()}<main id="main" tabindex="-1" class="auth-layout"><div class="auth-copy"><p class="eyebrow">A circle of care</p><h1>You don’t have to<br>notice everything<br>on your own.</h1><p class="muted">Keep everyday conversations and family observations together, one loved one at a time.</p><ol class="steps"><li>Create your caregiver account</li><li>Invite your loved one with a code</li><li>Stay connected through their updates</li></ol></div><section class="card auth-card"><h2>${signup ? 'Create your care circle' : 'Welcome back'}</h2><p class="sub">${signup ? 'A little support starts here.' : 'Pick up where you left off.'}</p><p class="notice">Preview only. Use the fictional details below. No account is created and passwords are not stored.</p><form id="auth-form"><div class="field"><label for="email">Email address</label><input id="email" type="email" value="mei@example.com" required autocomplete="off"></div><div class="field"><label for="password">Password</label><div class="password-wrap"><input id="password" type="password" value="RecollectDemo" minlength="8" required autocomplete="off"><button type="button" class="secondary" data-action="password" aria-label="Show password">Show</button></div></div>${signup ? '<div class="field"><label class="check"><input type="checkbox" required><span>I understand this is a prototype using fictional people and simulated results.</span></label></div>' : '<p><a href="#reset">Forgot password?</a></p>'}<button class="wide" type="submit">${signup ? 'Preview account creation' : 'Preview login'} ${icon('arrow')}</button></form><p class="sub" style="margin:20px 0 0">${signup ? 'Already have an account?' : 'New to Recollect?'} <button class="text-button" data-action="auth-mode">${signup ? 'Log in' : 'Sign up'}</button></p></section></main>`;
}
function family() {
  return shell(`<div class="page-heading"><div><p class="eyebrow">Your care circle</p><h1>A little closer, Mei.</h1><p class="muted">Everyday moments from the people you care about.</p></div><a class="button" href="#invite">${icon('plus')} Link someone</a></div><div class="notice" style="margin-bottom:25px">You’re exploring a fictional family. New links and observations stay in this page session only.</div><div class="grid">${people.map(p => `<article class="card"><div class="person-heading"><span class="avatar ${p.id === 'lily' ? 'sage' : ''}">${escape(p.initials)}</span><div><h2>${escape(p.name)}</h2><p class="sub">${escape(p.relation)}${p.age ? ` · ${p.age} years` : ''}</p></div></div><span class="tag ${p.attention ? 'amber' : ''}">${p.fresh ? 'Getting started' : p.attention ? 'An update to explore' : 'Recent conversations available'}</span><p style="margin:16px 0 0">${p.fresh ? 'Their first conversation will appear here.' : p.attention ? 'A few changes are worth a closer look together.' : 'Take a moment to catch up on their week.'}</p><div class="card-footer"><span class="sub">Last conversation<br><strong>${p.last}</strong></span><button class="text-button" data-person="${p.id}">View overview ${icon('arrow')}</button></div></article>`).join('')}<article class="card add-card"><span class="icon-box">${icon('plus')}</span><h2 style="margin:18px 0 8px">Room for someone else</h2><p class="sub">Each person has their own invitation and private overview.</p><a href="#invite">Link another loved one →</a></article></div>`);
}
function dashboard() {
  const p = currentPerson();
  return shell(`<div class="page-heading"><div><p class="eyebrow">The everyday picture</p><h1>${escape(p.name)}’s overview</h1><p class="muted">${p.fresh ? 'A new connection, at their own pace.' : 'Illustrative week · 3–9 September 2026'}</p></div>${personSelect()}</div>${p.fresh ? `<section class="card"><span class="icon-box">${icon('leaf')}</span><h2 style="margin-top:20px">A little time to get to know ${escape(p.name)}</h2><p>There aren’t any conversations yet. Missing information is not a reassuring result or a cause for concern.</p><a class="button" href="#chat">Preview their first conversation</a></section>` : `<section class="card summary-card"><span class="icon-box">${icon('leaf')}</span><div><p class="eyebrow">Simulated conversation summary</p><h2>${p.attention ? 'A few changes to talk about, together.' : 'A window into the everyday.'}</h2><p>${p.attention ? 'This example highlights repeated topics and word-finding pauses across recent conversations. These observations have many possible explanations.' : 'This example shows recent conversations without a highlighted change. It cannot rule out a health concern.'}</p></div></section><div class="metric-grid">${[['Conversations', `${p.sessions} this week`, 'Example completed sessions'], ['Repeated topics', p.attention ? '3 mentions' : '1 mention', 'Illustrative transcript markers'], ['Word-finding pauses', p.attention ? '4 moments' : '2 moments', 'Illustrative transcript markers'], ['Information available', 'Limited', 'Not a clinical assessment']].map(([label,value,caption]) => `<article class="card metric"><span class="sub">${label}</span><p class="value">${value}</p><p class="sub">${caption}</p></article>`).join('')}</div><div class="grid"><section class="card"><div class="row"><h2>Making time to talk</h2><span class="tag">Example data</span></div><p class="sub" style="margin-top:8px">Completed conversations per week</p><div class="chart" role="img" aria-label="Simulated conversations: week 1, 3; week 2, 4; week 3, 3; week 4, ${p.sessions}.">${[3,4,3,p.sessions].map(v => `<div class="chart-column"><span>${v}</span><span class="bar" style="height:${v * 20}px"></span></div>`).join('')}</div><div class="chart-labels"><span>Week 1</span><span>Week 2</span><span>Week 3</span><span>This week</span></div><p class="sub" style="margin:20px 0 0">Conversation frequency is activity, not a measure of cognitive health.</p></section><section class="card"><h2>A thoughtful next step</h2><span class="tag ${p.attention ? 'amber' : ''}">${p.attention ? 'Example: consider a check-in' : 'Example: keep in touch'}</span><p style="margin-top:18px">${p.attention ? 'If these changes reflect what you’ve noticed in daily life, consider discussing them with a qualified healthcare professional.' : 'Continue conversations at a comfortable pace. If you have concerns, you can discuss them with a qualified healthcare professional.'}</p><p class="sub">This recommendation is prewritten for the demo, not generated from your entries.</p><a class="button secondary" href="#observations">Add your observations</a></section></div>`}<section class="card" style="margin-top:24px"><div class="row"><h2>What family has noticed</h2><a href="#observations">${p.concerns.length ? 'Edit observations' : 'Add observations'} →</a></div>${p.concerns.length ? p.concerns.map(c => `<div class="list-row"><strong>${escape(c)}</strong><p class="sub">Family-reported · ${escape(p.frequency)}${p.since ? ` · Since ${escape(p.since)}` : ''}</p></div>`).join('') : '<p class="muted" style="margin:18px 0 0">No family observations saved yet. You can add something you’ve noticed, or leave this empty.</p>'}</section>`, 'dashboard');
}
function observations() {
  const p = currentPerson();
  return shell(`<div class="page-heading"><div><p class="eyebrow">Your perspective matters</p><h1>What’s on your mind?</h1><p class="muted">Share what you’ve noticed about ${escape(p.name)}, in your own words.</p></div>${personSelect()}</div><div class="form-grid"><form id="observations-form" class="card"><fieldset style="border:0;padding:0;margin:0"><legend style="font-weight:600;margin-bottom:16px">Have you noticed any of these changes?</legend><p class="sub">Choose any that apply. Leave unchecked if you’re unsure.</p>${concerns.map((c,i) => `<label class="check concern"><input type="checkbox" name="concern" value="${i}" ${p.concerns.includes(c) ? 'checked' : ''}><span>${c}</span></label>`).join('')}</fieldset><div class="grid" style="margin-top:24px"><div class="field"><label for="since">First noticed (optional)</label><input id="since" type="date" value="${escape(p.since)}" max="${new Date().toISOString().slice(0,10)}"></div><div class="field"><label for="frequency">How often?</label><select id="frequency">${['Sometimes','Often','Once','Not sure'].map(f => `<option ${p.frequency === f ? 'selected' : ''}>${f}</option>`).join('')}</select></div></div><div class="field"><label for="notes">An example, in your words (optional)</label><textarea id="notes" maxlength="1000" placeholder="For example: Dad asked about the same appointment twice on Sunday.">${escape(p.notes)}</textarea><small class="muted">Use fictional details in this demo.</small></div><div class="row"><button type="submit">Save observations ${icon('check')}</button><button class="text-button" type="button" data-action="clear-observations">Clear saved observations</button></div><p id="save-status" role="status" style="margin:15px 0 0"></p></form><aside class="stack"><section class="card"><span class="icon-box">${icon('leaf')}</span><h2 style="margin-top:18px">Context, with care.</h2><p>Your observations help describe what matters to your family.</p><p class="sub">In the planned experience, these could guide follow-up topics. Here, they are saved separately and do not change a risk score or the demo recommendations.</p></section><div class="notice">A checkbox is an observation, not a diagnosis. You can change or remove your entries at any time.</div></aside></div>`, 'observations');
}
function invite() {
  return shell(`<div class="page-heading"><div><p class="eyebrow">Grow your care circle</p><h1>Bring someone closer.</h1><p class="muted">One invitation, for one loved one.</p></div></div><div class="form-grid"><section class="card">${invitation ? `<h2>Your invitation for ${escape(pendingPerson.name)}</h2><p>Ask them to choose “I’m here for a conversation” and enter this code on their phone.</p><div class="code">${invitation.code}</div><p class="sub">Expires ${new Date(invitation.expires).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})} · One use · Waiting for consent</p><div class="row"><button data-action="copy">Copy code</button><button class="secondary" data-action="regenerate">New code</button></div><p id="copy-status" role="status"></p><hr style="border:0;border-top:1px solid var(--line);margin:25px 0"><p class="notice">Demo linking works in this page session only. Use the button below to preview their side.</p><a class="button wide" href="#connect">Preview loved one’s phone ${icon('arrow')}</a>` : `<h2>Who would you like to link?</h2><form id="invite-form"><div class="field"><label for="adult-name">Their first name</label><input id="adult-name" maxlength="40" placeholder="For example, Sam" required></div><div class="field"><label for="relationship">Relationship</label><select id="relationship"><option>Parent</option><option>Partner</option><option>Relative</option><option>Friend</option></select></div><button type="submit">Create invitation ${icon('arrow')}</button></form>`}</section><section class="card"><h2>A connection they choose.</h2><ol class="steps"><li>You share their invitation code.</li><li>They check your name and what will be shared.</li><li>They agree to connect, with no password to remember.</li></ol><p class="sub">The planned product remembers their own device and lets them disconnect. This preview resets when the page is reloaded.</p></section></div>`);
}
function connect() {
  return `${publicHeader()}<main id="main" tabindex="-1" class="centered older"><p class="eyebrow">A familiar connection</p><h1>Let’s connect you.</h1><p class="muted">Enter the six-digit code your family member shared with you.</p><form id="connect-form" class="card"><label for="link-code">Your invitation code</label><input id="link-code" style="font-size:30px;letter-spacing:.2em;text-align:center" inputmode="numeric" pattern="[0-9]{6}" maxlength="6" autocomplete="one-time-code" placeholder="000000" required aria-describedby="code-help code-error"><p id="code-help" class="sub" style="margin-top:14px">${invitation ? `Demo code for ${escape(pendingPerson.name)}: ${invitation.code}` : 'Try 123456 to preview Arun’s invitation.'}</p><p id="code-error" class="error" role="alert"></p><button class="wide" type="submit">Continue ${icon('arrow')}</button></form><p class="sub footer-note">No email or password needed. You’ll see who you’re connecting with before you agree.</p></main>`;
}
function consent() {
  if (!pendingPerson) return connect();
  return `${publicHeader()}<main id="main" tabindex="-1" class="centered older"><p class="eyebrow">You’re in control</p><h1>Connect with Mei?</h1><section class="card"><div class="person-heading"><span class="avatar sage">MC</span><div><h2>Mei Chen</h2><p class="sub">Your demo caregiver</p></div></div><p>Hi ${escape(pendingPerson.name)}. Connecting lets Mei see:</p><ul class="steps"><li>When you’ve had a conversation</li><li>A summary of conversation observations</li><li>Suggested next steps</li></ul><p class="sub">In this prototype, conversations are scripted and stay in this page session. Nothing is sent to a caregiver’s device.</p><form id="consent-form"><label class="check" style="margin:24px 0"><input type="checkbox" required><span>I agree to connect with Mei and share these updates.</span></label><button class="wide" type="submit">Connect with Mei</button></form><a class="button secondary wide" style="margin-top:12px" href="#connect">Not now</a></section></main>`;
}
function chat() {
  if (!linked) return connect();
  return `${publicHeader()}<main id="main" tabindex="-1" class="chat older"><header class="chat-header"><p class="eyebrow">A moment, just for you</p><h1>Hello, ${escape(linked.name)}.</h1><p class="muted">No right answers. No rush. Just a little conversation.</p><span class="tag">Connected with Mei · demo</span></header><div class="conversation" aria-label="Conversation">${messages.map(m => `<div class="bubble ${m.role === 'you' ? 'mine' : ''}"><small>${m.role === 'you' ? 'You' : 'Recollect · scripted demo'}</small><p>${escape(m.text)}</p></div>`).join('')}</div><div class="voice-area"><button class="mic" data-action="voice" aria-label="${voiceState === 'listening' ? 'Stop simulated listening' : 'Preview speaking'}">${voiceState === 'listening' ? '<span aria-hidden="true">■</span>' : icon('mic')}</button><p id="voice-status" role="status">${voiceState === 'listening' ? 'Simulated listening… Tap to stop.' : 'Tap to preview speaking'}</p><p class="sub">Demo voice interaction. Your microphone is not recording.</p></div><form id="chat-form"><label for="message">Or type a fictional reply</label><div class="type-row"><input id="message" maxlength="500" placeholder="Tell me about your morning…" required><button type="submit">Send ${icon('arrow')}</button></div></form><div class="row" style="margin-top:25px"><button class="secondary" data-action="finish">Finish conversation</button><a href="#connection">Your connection</a></div></main>`;
}
function connection() {
  return `${publicHeader()}<main id="main" tabindex="-1" class="centered older"><h1>Your connection</h1><section class="card"><h2>${linked ? 'Connected with Mei Chen' : 'No active connection'}</h2><p>Mei can see the updates you agreed to share in the planned experience. This demo stays on this page.</p>${linked ? '<button data-action="disconnect" class="secondary wide">Disconnect from Mei</button><a href="#chat" class="button wide" style="margin-top:12px">Back to conversation</a>' : '<a class="button" href="#connect">Enter an invitation code</a>'}</section></main>`;
}
function finish() {
  return `${publicHeader()}<main id="main" tabindex="-1" class="centered older"><section class="card"><span class="icon-box">${icon('check')}</span><h1 style="margin-top:25px">Thank you for sharing.</h1><p>That’s enough for today. Come back whenever you feel like a conversation.</p><p class="notice">Demo complete. No health assessment was performed and no real update was shared.</p><button class="wide" data-action="new-chat">Start another conversation</button><a class="button secondary wide" style="margin-top:12px" href="#welcome">Back to welcome</a></section></main>`;
}
function reset() {
  return `${publicHeader()}<main id="main" tabindex="-1" class="centered"><section class="card"><h1>Let’s get you back in.</h1><p>In the full product, you’ll receive a password reset link if an account exists for your email.</p><p class="notice">This prototype does not send email or create accounts.</p><a class="button wide" href="#auth">Return to demo login</a></section></main>`;
}
const pages = { welcome, auth, family, dashboard, observations, invite, connect, consent, chat, connection, finish, reset };
const protectedPages = ['family','dashboard','observations','invite'];
function render() {
  let route = location.hash.slice(1) || 'welcome';
  if (dirty && route !== lastRoute) {
    if (!window.confirm('Leave without saving your observation changes?')) { history.replaceState(null, '', `#${lastRoute}`); return; }
    dirty = false;
  }
  if (!pages[route]) { history.replaceState(null, '', '#welcome'); route = 'welcome'; }
  if (protectedPages.includes(route) && !caregiver) { history.replaceState(null, '', '#auth'); route = 'auth'; }
  if (route !== 'chat') voiceState = 'idle';
  app.innerHTML = pages[route]();
  lastRoute = route;
  document.title = `Recollect · ${route.charAt(0).toUpperCase() + route.slice(1)}`;
  document.querySelector('#main')?.focus({ preventScroll: true });
  window.scrollTo(0, 0);
}
function addReply(text) {
  messages.push({role:'you', text});
  const prompts = ['That sounds like a moment worth sharing. What did you enjoy about it?', 'Thank you for telling me. Is there anything else you’d like to talk about?', 'It’s been lovely spending this moment with you. You can finish whenever you’re ready.'];
  const replies = messages.filter(m => m.role === 'you').length;
  messages.push({role:'ai', text: prompts[Math.min(replies - 1, prompts.length - 1)]});
  voiceState = 'idle';
  render();
  announce('Reply added. ' + messages.at(-1).text);
  document.querySelector('#message')?.focus();
}
function makeInvitation() {
  invitation = { code: String(crypto.getRandomValues(new Uint32Array(1))[0] % 900000 + 100000), expires: Date.now() + 10 * 60 * 1000 };
}
app.addEventListener('click', async event => {
  const button = event.target.closest('[data-action], [data-person]');
  if (!button) return;
  if (button.dataset.person) { selected = button.dataset.person; go('dashboard'); return; }
  switch (button.dataset.action) {
    case 'auth-mode': authMode = authMode === 'signup' ? 'login' : 'signup'; render(); break;
    case 'password': {
      const input = document.querySelector('#password');
      input.type = input.type === 'password' ? 'text' : 'password';
      button.textContent = input.type === 'password' ? 'Show' : 'Hide';
      button.setAttribute('aria-label', `${button.textContent} password`); break;
    }
    case 'logout': caregiver = false; go('welcome'); break;
    case 'copy': {
      const status = document.querySelector('#copy-status');
      try { await navigator.clipboard.writeText(invitation.code); status.textContent = 'Code copied.'; }
      catch { status.textContent = 'Copy is unavailable. Select the code above and copy it manually.'; }
      break;
    }
    case 'regenerate': makeInvitation(); render(); announce('New invitation code generated.'); break;
    case 'clear-observations': {
      if (!window.confirm('Clear the saved observations for this person?')) return;
      Object.assign(currentPerson(), { concerns: [], notes: '', since: '', frequency: 'Sometimes' });
      dirty = false; render(); announce('Saved observations cleared.'); break;
    }
    case 'voice':
      if (voiceState === 'idle') { voiceState = 'listening'; render(); document.querySelector('.mic').focus(); }
      else addReply('I took a walk this morning and saw the flowers in the garden.');
      break;
    case 'finish': voiceState = 'idle'; go('finish'); break;
    case 'new-chat': if (!linked) { go('connect'); break; } messages = [{role:'ai', text:'It’s good to see you. What has your day been like so far?'}]; go('chat'); break;
    case 'disconnect': if (window.confirm('Disconnect from Mei? You’ll need a new invitation to connect again.')) { linked = null; messages = []; go('connect'); } break;
  }
});
app.addEventListener('input', event => {
  if (event.target.closest('#observations-form')) dirty = true;
  if (event.target.id === 'adult-name') event.target.setCustomValidity('');
});
app.addEventListener('change', event => {
  if (event.target.id === 'person-select') {
    if (dirty && !window.confirm('Switch people without saving your changes?')) { event.target.value = selected; return; }
    dirty = false; selected = event.target.value; render();
  }
});
app.addEventListener('submit', event => {
  event.preventDefault();
  const form = event.target;
  if (form.id === 'auth-form') { caregiver = true; go('family'); }
  if (form.id === 'invite-form') {
    const name = document.querySelector('#adult-name').value.trim();
    if (!name) { document.querySelector('#adult-name').setCustomValidity('Enter a first name.'); document.querySelector('#adult-name').reportValidity(); return; }
    pendingPerson = { id: crypto.randomUUID(), name, initials: name.slice(0,2).toUpperCase(), relation: document.querySelector('#relationship').value, age:'', last:'Not yet', sessions:0, attention:false, concerns:[], notes:'', since:'', frequency:'Sometimes', fresh:true };
    makeInvitation(); render();
  }
  if (form.id === 'connect-form') {
    const code = document.querySelector('#link-code').value;
    if (invitation && invitation.code === code && Date.now() > invitation.expires) { document.querySelector('#code-error').textContent = 'This code has expired. Ask Mei to create a new invitation.'; return; }
    if (invitation && invitation.code === code) { go('consent'); }
    else if (!invitation && code === '123456') { pendingPerson = people[0]; go('consent'); }
    else document.querySelector('#code-error').textContent = 'That code doesn’t match. Check the six digits and try again.';
  }
  if (form.id === 'consent-form') {
    if (invitation && Date.now() > invitation.expires) { go('connect'); return; }
    linked = pendingPerson;
    if (!people.some(p => p.id === linked.id)) people.push(linked);
    selected = linked.id;
    invitation = null;
    messages = [{role:'ai', text:'It’s good to see you. What has your day been like so far?'}];
    go('chat');
  }
  if (form.id === 'observations-form') {
    Object.assign(currentPerson(), {
      concerns: [...form.querySelectorAll('input[name=concern]:checked')].map(input => concerns[Number(input.value)]),
      notes: document.querySelector('#notes').value.trim(),
      since: document.querySelector('#since').value,
      frequency: document.querySelector('#frequency').value,
    });
    dirty = false;
    document.querySelector('#save-status').textContent = 'Saved for ' + currentPerson().name + ' in this demo session.';
  }
  if (form.id === 'chat-form') {
    const text = document.querySelector('#message').value.trim();
    if (text) addReply(text);
  }
});
window.addEventListener('beforeunload', event => { if (dirty) { event.preventDefault(); event.returnValue = ''; } });
window.addEventListener('hashchange', render);
render();
