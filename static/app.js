/* FaceVision dashboard - vanilla JS, no build step */
(() => {
"use strict";

// ------------------------------------------------------------------ icons
const P = {
  scan: '<path d="M3 7V5a2 2 0 0 1 2-2h2M17 3h2a2 2 0 0 1 2 2v2M21 17v2a2 2 0 0 1-2 2h-2M7 21H5a2 2 0 0 1-2-2v-2"/><circle cx="12" cy="10" r="3"/><path d="M7 17c1.2-2 3-3 5-3s3.8 1 5 3"/>',
  grid: '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
  video: '<path d="m22 8-6 4 6 4V8Z"/><rect x="2" y="6" width="14" height="12" rx="2"/>',
  videoOff: '<path d="M10.66 6H14a2 2 0 0 1 2 2v2.34l1 1L22 8v8M16 16a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h2"/><path d="m2 2 20 20"/>',
  userPlus: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M19 8v6M22 11h-6"/>',
  userCheck: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="m16 11 2 2 4-4"/>',
  userX: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="m17 8 5 5M22 8l-5 5"/>',
  user: '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
  users: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
  cpu: '<rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3"/>',
  calendar: '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/><path d="m9 16 2 2 4-4"/>',
  image: '<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.1-3.1a2 2 0 0 0-2.8 0L6 21"/>',
  menu: '<path d="M4 6h16M4 12h16M4 18h16"/>',
  moon: '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>',
  sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/>',
  layers: '<path d="m12 2 10 5-10 5L2 7l10-5Z"/><path d="m2 17 10 5 10-5M2 12l10 5 10-5"/>',
  check: '<path d="M20 6 9 17l-5-5"/>',
  play: '<path d="m6 3 14 9-14 9V3Z"/>',
  stop: '<rect x="5" y="5" width="14" height="14" rx="2"/>',
  camera: '<path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3Z"/><circle cx="12" cy="13" r="3"/>',
  move: '<path d="m5 9-3 3 3 3M9 5l3-3 3 3M15 19l-3 3-3-3M19 9l3 3-3 3M2 12h20M12 2v20"/>',
  smile: '<circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2M9 9h.01M15 9h.01"/>',
  glasses: '<circle cx="6" cy="15" r="4"/><circle cx="18" cy="15" r="4"/><path d="M14 15a2 2 0 0 0-4 0M2.5 13 5 7c.7-1.3 1.4-2 3-2M21.5 13 19 7c-.7-1.3-1.5-2-3-2"/>',
  alert: '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4M12 17h.01"/>',
  search: '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
  trash: '<path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  chart: '<path d="M3 3v18h18"/><path d="M7 16v-5M12 16V8M17 16v-8"/>',
  refresh: '<path d="M3 12a9 9 0 0 1 15-6.7L21 8M21 3v5h-5M21 12a9 9 0 0 1-15 6.7L3 16M3 21v-5h5"/>',
  download: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/>',
  upload: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/>',
  percent: '<path d="M19 5 5 19"/><circle cx="6.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/>',
  info: '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>',
  x: '<path d="M18 6 6 18M6 6l12 12"/>',
};
const icon = n => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${P[n] || ""}</svg>`;
const paintIcons = (root = document) => root.querySelectorAll("i[data-icon]:not([data-done])").forEach(el => {
  el.innerHTML = icon(el.dataset.icon); el.dataset.done = "1";
});
const ic = n => `<i data-icon="${n}" data-done="1">${icon(n)}</i>`;

// ------------------------------------------------------------------ helpers
const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const pretty = n => String(n || "").replace(/_/g, " ");
const initials = n => pretty(n).split(/\s+/).filter(Boolean).slice(0, 2).map(w => w[0].toUpperCase()).join("") || "?";
const BLANK = "data:image/gif;base64,R0lGODlhAQABAAAAACw=";
const store = {
  get(k) { try { return localStorage.getItem(k); } catch { return null; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch { /* ignore */ } },
};

async function api(path, opts = {}) {
  const o = { ...opts };
  if (o.json !== undefined) {
    o.method = o.method || "POST";
    o.headers = { "Content-Type": "application/json" };
    o.body = JSON.stringify(o.json);
  }
  let res, data;
  try {
    res = await fetch(path, o);
    data = await res.json();
  } catch (e) {
    throw new Error(res ? `Server error (${res.status})` : "Cannot reach the server. Is app.py running?");
  }
  if (!data.ok) throw new Error(data.error || "Request failed");
  return data;
}

function toast(msg, type = "info", ms = 3500) {
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  el.innerHTML = `${ic(type === "ok" ? "check" : type === "err" ? "alert" : "info")}<span>${esc(msg)}</span>`;
  $("#toasts").appendChild(el);
  setTimeout(() => { el.classList.add("out"); setTimeout(() => el.remove(), 300); }, ms);
}

function confirmDialog(title, text, okLabel = "Delete") {
  return new Promise(resolve => {
    $("#modal-title").textContent = title;
    $("#modal-text").textContent = text;
    $("#modal-ok").textContent = okLabel;
    $("#modal").hidden = false;
    const done = v => { $("#modal").hidden = true; $("#modal-ok").onclick = $("#modal-cancel").onclick = null; resolve(v); };
    $("#modal-ok").onclick = () => done(true);
    $("#modal-cancel").onclick = () => done(false);
    $("#modal").onclick = e => { if (e.target.id === "modal") done(false); };
  });
}

function lightbox(src) {
  const lb = $("#lightbox");
  lb.querySelector("img").src = src;
  lb.hidden = false;
}
$("#lightbox").onclick = () => { $("#lightbox").hidden = true; };
document.addEventListener("keydown", e => { if (e.key === "Escape") { $("#lightbox").hidden = true; $("#modal").hidden = true; } });

function setRing(el, pct, colorize = false) {
  const p = Math.max(0, Math.min(100, pct || 0));
  el.querySelector(".fg").setAttribute("stroke-dasharray", `${p} 100`);
  if (colorize) {
    el.classList.remove("good", "mid", "bad");
    el.classList.add(p >= 85 ? "good" : p >= 60 ? "mid" : "bad");
  }
}

// cached people (for avatars)
let peopleCache = {};
function avatar(name, cls = "") {
  const p = peopleCache[name];
  if (p && p.thumb) return `<div class="avatar ${cls}"><img src="/dataset/${encodeURIComponent(name)}/${encodeURIComponent(p.thumb)}" alt=""></div>`;
  return `<div class="avatar ${cls}">${esc(initials(name))}</div>`;
}
async function refreshPeopleCache() {
  try {
    const d = await api("/api/people");
    peopleCache = Object.fromEntries(d.people.map(p => [p.name, p]));
    updateModelMini(d.model);
    return d;
  } catch (e) { return null; }
}

function updateModelMini(m) {
  const el = $("#model-mini");
  const dot = el.querySelector(".dot"), txt = el.querySelector(".txt");
  dot.className = "dot " + (!m.trained ? "bad" : m.stale ? "warn" : "ok");
  txt.textContent = !m.trained ? "Model not trained" : m.stale ? "Model needs retraining" : `Model ready · ${m.people.length} people`;
}

// ------------------------------------------------------------------ theme
function applyTheme(t) {
  document.documentElement.dataset.theme = t;
  $("#theme-btn").innerHTML = ic(t === "light" ? "moon" : "sun");
}
applyTheme(store.get("theme") || "dark");
$("#theme-btn").onclick = () => {
  const t = document.documentElement.dataset.theme === "light" ? "dark" : "light";
  store.set("theme", t); applyTheme(t);
};

// ------------------------------------------------------------------ router
const PAGES = {
  dashboard: ["Dashboard", "Overview of your face recognition system"],
  live: ["Live Camera", "Real-time detection and recognition from your webcam"],
  register: ["Register Person", "Collect face samples to build the dataset"],
  people: ["People", "Everyone in the dataset"],
  train: ["Train Model", "Build the LBPH face recogniser"],
  attendance: ["Attendance", "Automatically recorded by live recognition"],
  image: ["Image Test", "Detect or recognise faces in a photo"],
};
let page = null;
let pendingLiveMode = null, pendingAutoTrain = false;

document.addEventListener("click", e => {
  const a = e.target.closest("a[href^='#']");
  if (!a) return;
  if (a.dataset.liveMode) pendingLiveMode = a.dataset.liveMode;
  if (a.dataset.autotrain) pendingAutoTrain = true;
  $("#sidebar").classList.remove("open");
});
$("#menu-btn").onclick = () => $("#sidebar").classList.toggle("open");

async function route() {
  const next = (location.hash.slice(1) || "dashboard");
  const target = PAGES[next] ? next : "dashboard";
  const prev = page;
  page = target;
  // leaving a camera page -> switch the camera off
  if (prev && prev !== target && (prev === "live" || prev === "register") && camStatus.running) {
    await stopCamera(true);
  }
  $$(".page").forEach(s => s.classList.toggle("active", s.id === `page-${target}`));
  $$(".nav a").forEach(a => a.classList.toggle("active", a.dataset.page === target));
  $("#page-title").textContent = PAGES[target][0];
  $("#page-sub").textContent = PAGES[target][1];
  document.title = `${PAGES[target][0]} · FaceVision`;
  ({ dashboard: loadDashboard, live: enterLive, register: enterRegister, people: loadPeople,
     train: enterTrain, attendance: loadAttendance, image: () => {} })[target]();
}
window.addEventListener("hashchange", route);

// ------------------------------------------------------------------ camera status & stream
let camStatus = { running: false, mode: "idle" };
let pollTimer = null;

function streamImg() { return page === "register" ? $("#reg-img") : $("#live-img"); }
function streamWrap() { return page === "register" ? $("#reg-wrap") : $("#live-wrap"); }

function attachStream() {
  const img = streamImg();
  if (!img.dataset.on) {
    img.src = "/video_feed?t=" + Date.now();
    img.dataset.on = "1";
  }
  streamWrap().classList.add("on");
}
function detachStreams() {
  ["#live-img", "#reg-img"].forEach(s => { const i = $(s); i.src = BLANK; delete i.dataset.on; });
  ["#live-wrap", "#reg-wrap"].forEach(s => $(s).classList.remove("on"));
}

function updateCamPill(s) {
  const pill = $("#cam-pill");
  const dot = pill.querySelector(".dot");
  dot.className = "dot " + (s.running ? "live" : "");
  const label = { detect: "Detecting", recognize: "Recognising", capture: "Capturing" }[s.mode];
  pill.querySelector("span:last-child").textContent = s.running ? `Camera on · ${label}` : "Camera off";
}

async function poll() {
  clearTimeout(pollTimer);
  try {
    const d = await api("/api/status");
    const s = d.status;
    const wasRunning = camStatus.running;
    camStatus = s;
    updateCamPill(s);
    if (s.running && (page === "live" || page === "register")) attachStream();
    if (!s.running && wasRunning) {
      detachStreams();
      if (s.error) toast(s.error, "err");
    }
    if (page === "live") renderLive(s);
    if (page === "register") renderRegister(s);
  } catch (e) { /* server down - keep trying */ }
  const fast = camStatus.running && (page === "live" || page === "register");
  pollTimer = setTimeout(poll, fast ? 400 : 3000);
}

async function startCamera(payload, loader) {
  $(loader).classList.add("show");
  try {
    const d = await api("/api/camera/start", { json: { camera: +$("#cam-index").value, ...payload } });
    camStatus = d.status;
    attachStream();
    updateCamPill(camStatus);
    poll();
    return true;
  } catch (e) {
    toast(e.message, "err", 5000);
    return false;
  } finally {
    $(loader).classList.remove("show");
  }
}

async function stopCamera(silent = false) {
  detachStreams();
  try {
    const d = await api("/api/camera/stop", { method: "POST" });
    camStatus = d.status;
    updateCamPill(camStatus);
  } catch (e) { if (!silent) toast(e.message, "err"); }
}

// ------------------------------------------------------------------ dashboard
async function loadDashboard() {
  let d;
  try { d = await api("/api/overview"); } catch (e) { return toast(e.message, "err"); }
  await refreshPeopleCache();
  $("#st-people").textContent = d.people;
  $("#st-images").textContent = d.images;
  const m = d.model;
  $("#st-model").textContent = !m.trained ? "Not trained" : m.stale ? "Retrain needed" : "Ready";
  $("#st-model-sub").textContent = m.trained ? `Trained ${m.trained_at}` : "Train after registering";
  $("#st-today").textContent = d.today.length;

  // steps
  const done = [d.people > 0, m.trained && !m.stale, d.today.length > 0];
  const cur = done.indexOf(false);
  $$("#steps li").forEach((li, i) => {
    li.classList.toggle("done", done[i]);
    li.classList.toggle("current", i === cur);
    li.querySelector(".step-num").innerHTML = done[i] ? ic("check") : i + 1;
  });

  // week chart
  const max = Math.max(1, ...d.week.map(w => w.count));
  const todayStr = d.week[d.week.length - 1].date;
  $("#week-bars").innerHTML = d.week.map(w => `
    <div class="bar ${w.date === todayStr ? "today" : ""}" title="${w.date}: ${w.count} present">
      <div class="bar-val">${w.count}</div>
      <div class="bar-track"><div class="bar-fill" style="height:${(w.count / max) * 100}%"></div></div>
      <div class="bar-lbl">${w.label}</div>
    </div>`).join("");

  // today
  $("#today-count").textContent = d.today.length;
  $("#today-list").innerHTML = d.today.length ? d.today.slice().reverse().slice(0, 6).map(r => `
    <div class="item">${avatar(r.Name)}<div class="grow"><b>${esc(pretty(r.Name))}</b><small>Marked at ${esc(r.Time)}</small></div>
    <span class="tag green">${esc(r["Match %"])}%</span></div>`).join("")
    : `<div class="empty-line">No one marked present yet today. Start <a class="link" href="#live" data-live-mode="recognize">recognition</a> with attendance on.</div>`;

  // screenshots
  try {
    const s = await api("/api/screenshots");
    $("#shots-count").textContent = d.screenshots ? `${d.screenshots} saved in screenshots/` : "";
    $("#shots").innerHTML = s.files.length ? s.files.slice(0, 12).map(f => `<img src="${f.url}" alt="${esc(f.name)}" loading="lazy">`).join("")
      : `<div class="empty-line" style="grid-column:1/-1">Use the Screenshot button on the Live Camera page.</div>`;
    $$("#shots img").forEach(img => img.onclick = () => lightbox(img.src));
  } catch (e) { /* ignore */ }
}

// ------------------------------------------------------------------ live
let liveMode = "detect";
function setLiveMode(mode) {
  liveMode = mode;
  $$("#mode-seg button").forEach(b => b.classList.toggle("active", b.dataset.mode === mode));
  $$("#page-live [data-for]").forEach(el => { el.hidden = el.dataset.for !== mode; });
}
$$("#mode-seg button").forEach(b => b.onclick = async () => {
  setLiveMode(b.dataset.mode);
  if (camStatus.running) await startLive();       // switch mode on the fly
});

function liveOptions() {
  return { mode: liveMode, eyes: $("#opt-eyes").checked, attendance: $("#opt-att").checked, threshold: +$("#opt-thr").value };
}
async function startLive() {
  if (await startCamera(liveOptions(), "#live-loading")) {
    $("#live-results").innerHTML = `<div class="empty-line">Looking for faces…</div>`;
  }
}
$("#live-start").onclick = startLive;
$("#live-stop").onclick = () => stopCamera();
$("#live-shot").onclick = async () => {
  try {
    const d = await api("/api/screenshot", { method: "POST" });
    toast(`Saved screenshots/${d.file}`, "ok");
  } catch (e) { toast(e.message, "err"); }
};
$("#cam-index").onchange = () => { store.set("cam", $("#cam-index").value); if (camStatus.running && page === "live") startLive(); };
$("#cam-index").value = store.get("cam") || "0";

const pushSettings = () => { if (camStatus.running) api("/api/camera/settings", { json: liveOptions() }).catch(e => toast(e.message, "err")); };
$("#opt-eyes").onchange = pushSettings;
$("#opt-att").onchange = pushSettings;
let thrTimer;
$("#opt-thr").oninput = () => {
  $("#thr-val").textContent = $("#opt-thr").value;
  clearTimeout(thrTimer); thrTimer = setTimeout(pushSettings, 200);
};

async function enterLive() {
  await refreshPeopleCache();
  setLiveMode(pendingLiveMode || liveMode);
  renderLive(camStatus);
  if (pendingLiveMode) { pendingLiveMode = null; startLive(); }
  poll();
}

let lastLiveKey = "";
function renderLive(s) {
  const on = s.running && s.mode !== "capture";
  $("#live-start").hidden = on;
  $("#live-stop").hidden = !on;
  $("#live-shot").disabled = !on;
  if (!on) {
    if (!s.running) $("#live-wrap").classList.remove("on");
    $("#live-count").textContent = 0;
    return;
  }
  $("#hud-mode").textContent = s.mode === "recognize" ? "RECOGNISING" : "DETECTING";
  $("#hud-fps").textContent = `${s.fps.toFixed(1)} FPS`;
  $("#hud-faces").textContent = `${s.faces} face${s.faces === 1 ? "" : "s"}`;
  $("#live-count").textContent = s.faces;

  const key = JSON.stringify(s.results.map(r => [r.name, Math.round(r.score || 0), r.eyes])) + s.mode;
  if (key !== lastLiveKey) {
    lastLiveKey = key;
    $("#live-results").innerHTML = s.results.length ? s.results.map(r => {
      if (r.known === null) {
        return `<div class="item"><div class="avatar face">${ic("scan")}</div><div class="grow"><b>${esc(r.name)}</b>
          <small>${r.box[2]}×${r.box[3]} px${s.eyes ? ` · ${r.eyes} eye${r.eyes === 1 ? "" : "s"}` : ""}</small></div></div>`;
      }
      const sc = Math.round(r.score);
      return `<div class="item">${r.known ? avatar(r.name) : `<div class="avatar unknown">?</div>`}
        <div class="grow"><b>${esc(pretty(r.name))}</b><small>${r.known ? "Recognised" : "Not in dataset"} · dist ${r.distance}</small></div>
        <div class="score"><span>${sc}%</span><div class="meter"><div style="width:${sc}%;background:${r.known ? "var(--green)" : "var(--red)"}"></div></div></div></div>`;
    }).join("") : `<div class="empty-line">No faces in frame</div>`;
  }
  if (s.mode === "recognize") {
    $("#live-marks").innerHTML = s.recent_marks.length ? s.recent_marks.map(m => `
      <div class="item">${avatar(m.name)}<div class="grow"><b>${esc(pretty(m.name))}</b><small>Marked at ${esc(m.time)}</small></div><span class="tag green">${Math.round(m.score)}%</span></div>`).join("")
      : `<div class="empty-line">${s.attendance ? "Nobody marked in this session" : "Attendance is off"}</div>`;
  }
}

// ------------------------------------------------------------------ register
$("#reg-samples").oninput = () => { $("#reg-samples-val").textContent = $("#reg-samples").value; };
let regActive = false;

$("#reg-form").onsubmit = async e => {
  e.preventDefault();
  const name = $("#reg-name").value.trim();
  if (!name) return toast("Please enter a name", "err");
  const existing = peopleCache[name.replace(/\s+/g, "_")];
  if (existing && !(await confirmDialog("Add more samples?", `${pretty(name)} already has ${existing.images} samples. New samples will be added to the existing ones.`, "Add samples"))) return;
  $("#reg-done").hidden = true;
  regActive = true;
  const ok = await startCamera({ mode: "capture", name, samples: +$("#reg-samples").value }, "#reg-loading");
  if (!ok) regActive = false;
};
$("#reg-stop").onclick = async () => { await stopCamera(); regActive = false; renderRegister(camStatus); toast("Capture stopped", "info"); };
$("#reg-again").onclick = () => {
  $("#reg-done").hidden = true; $("#reg-name").value = ""; $("#reg-name").focus();
  resetRegisterView();
};

function resetRegisterView() {
  setRing($("#reg-ring"), 0);
  $("#reg-pct").textContent = "0%";
  $("#reg-title").textContent = "Waiting to start";
  $("#reg-status").textContent = "Fill in the form on the right.";
}

async function enterRegister() {
  await refreshPeopleCache();
  if (pendingRegisterName) { $("#reg-name").value = pendingRegisterName; pendingRegisterName = null; }
  renderRegister(camStatus);
  poll();
  setTimeout(() => $("#reg-name").focus(), 50);
}
let pendingRegisterName = null;

function renderRegister(s) {
  const c = s.capture || {};
  const capturing = s.running && s.mode === "capture";
  $("#reg-start").hidden = capturing;
  $("#reg-stop").hidden = !capturing;
  $("#reg-name").disabled = capturing;
  $("#reg-samples").disabled = capturing;
  if (!regActive || !c.name) return;
  const pct = Math.round((c.count / Math.max(1, c.target)) * 100);
  setRing($("#reg-ring"), pct);
  $("#reg-pct").textContent = pct + "%";
  $("#reg-hud-count").textContent = `${c.count} / ${c.target}`;
  $("#reg-title").textContent = c.done ? `Captured ${c.count} samples of ${pretty(c.name)}` : `Capturing ${pretty(c.name)}…`;
  $("#reg-status").textContent = c.status || "";
  if (c.done) {
    regActive = false;
    $("#reg-done-title").textContent = `${pretty(c.name)} registered!`;
    $("#reg-done").hidden = false;
    toast(`Saved ${c.count} samples for ${pretty(c.name)}`, "ok");
    refreshPeopleCache();
  } else if (!s.running) {
    regActive = false;
  }
}

// ------------------------------------------------------------------ people
let peopleData = [];
async function loadPeople() {
  const d = await refreshPeopleCache();
  if (!d) return;
  peopleData = d.people;
  $("#stale-banner").hidden = !(d.model.trained && d.model.stale) && !(d.people.length && !d.model.trained);
  if (!d.model.trained && d.people.length) {
    $("#stale-banner").querySelector("div").innerHTML = "<b>The model has not been trained yet.</b> Train it so these people can be recognised.";
  }
  renderPeople();
}
$("#people-search").oninput = renderPeople;

function renderPeople() {
  const q = $("#people-search").value.trim().toLowerCase();
  const list = peopleData.filter(p => pretty(p.name).toLowerCase().includes(q));
  if (!peopleData.length) {
    $("#people-grid").innerHTML = `<div class="card empty-state"><div class="empty-ico">${ic("users")}</div>
      <div class="empty-title">No one registered yet</div><div class="muted">Register a person to start building the dataset.</div>
      <a class="btn primary" style="margin-top:12px" href="#register">${ic("userPlus")}Register person</a></div>`;
    return;
  }
  $("#people-grid").innerHTML = list.map(p => {
    const src = f => `/dataset/${encodeURIComponent(p.name)}/${encodeURIComponent(f)}`;
    const quality = p.images >= 50 ? ["green", "Good dataset"] : p.images >= 20 ? ["amber", "Add more samples"] : ["red", "Too few samples"];
    return `<div class="card person">
      <div class="person-cover">${p.thumb ? `<img src="${src(p.thumb)}" alt="" loading="lazy">` : ""}
        <span class="tag ${quality[0]} status">${quality[1]}</span><span class="count">${p.images} samples</span></div>
      <div class="person-strip">${p.samples.map(f => `<img src="${src(f)}" alt="" loading="lazy">`).join("")}</div>
      <div class="person-body"><b title="${esc(p.name)}">${esc(pretty(p.name))}</b>
        <button class="btn sm" data-add="${esc(p.name)}" title="Capture more samples">${ic("plus")}Samples</button>
        <button class="btn sm ghost-danger" data-del="${esc(p.name)}" title="Delete">${ic("trash")}</button></div>
    </div>`;
  }).join("") || `<div class="empty-line" style="grid-column:1/-1">No match for "${esc(q)}"</div>`;
  $$("#people-grid .person-strip img, #people-grid .person-cover img").forEach(img => img.onclick = () => lightbox(img.src));
  $$("[data-add]").forEach(b => b.onclick = () => { pendingRegisterName = b.dataset.add; location.hash = "register"; });
  $$("[data-del]").forEach(b => b.onclick = async () => {
    const n = b.dataset.del;
    if (!(await confirmDialog(`Delete ${pretty(n)}?`, "All face samples of this person will be permanently deleted. Retrain the model afterwards."))) return;
    try {
      await api(`/api/people/${encodeURIComponent(n)}`, { method: "DELETE" });
      toast(`${pretty(n)} deleted`, "ok");
      loadPeople();
    } catch (e) { toast(e.message, "err"); }
  });
}

// ------------------------------------------------------------------ train
function renderModelBox(m) {
  $("#train-model-box").innerHTML = `
    <div class="row"><span>Status</span><b>${!m.trained ? '<span class="tag red">Not trained</span>' : m.stale ? '<span class="tag amber">Outdated</span>' : '<span class="tag green">Up to date</span>'}</b></div>
    <div class="row"><span>Last trained</span><b>${m.trained_at || "–"}</b></div>
    <div class="row"><span>People in model</span><b>${m.people.length}</b></div>`;
}
async function enterTrain() {
  const d = await refreshPeopleCache();
  if (d) renderModelBox(d.model);
  if (pendingAutoTrain) { pendingAutoTrain = false; runTraining(); }
}
$("#train-btn").onclick = runTraining;

async function runTraining() {
  const btn = $("#train-btn");
  btn.disabled = true;
  btn.innerHTML = `<div class="spinner" style="width:18px;height:18px;border-width:2px"></div>Training…`;
  try {
    const d = await api("/api/train", { json: { eval: $("#train-eval").checked } });
    const r = d.result;
    renderModelBox(d.model);
    updateModelMini(d.model);
    $("#train-empty").hidden = true;
    $("#train-out").hidden = false;
    $("#train-time").textContent = `${r.images} images · ${r.seconds}s`;
    const ev = r.evaluation;
    const ring = $("#acc-ring");
    if (ev) {
      setRing(ring, ev.accuracy, true);
      $("#acc-val").textContent = `${Math.round(ev.accuracy)}%`;
      $("#metrics").innerHTML = [
        [ev.test, "Test samples"], [ev.correct, "Correct"], [ev.unknown, "Rejected as unknown"], [ev.wrong, "Wrong person"],
      ].map(([v, l]) => `<div class="metric"><b>${v}</b><span>${l}</span></div>`).join("");
    } else {
      setRing(ring, 100); ring.classList.remove("good", "mid", "bad");
      $("#acc-val").textContent = "✓";
      $("#metrics").innerHTML = `<div class="metric"><b>${r.people.length}</b><span>People</span></div><div class="metric"><b>${r.images}</b><span>Images</span></div>`;
    }
    const max = Math.max(...r.people.map(p => p.images));
    $("#train-table").innerHTML = r.people.map(p => `<tr><td class="mono">${p.id}</td><td><div class="who">${avatar(p.name)}${esc(pretty(p.name))}</div></td>
      <td class="mono">${p.images}</td><td><div class="mini-bar"><div style="width:${(p.images / max) * 100}%"></div></div></td></tr>`).join("");
    $("#train-log").textContent = r.log.join("\n");
    toast(ev ? `Model trained · accuracy ${ev.accuracy}%` : "Model trained", "ok");
  } catch (e) {
    toast(e.message, "err", 5000);
  } finally {
    btn.disabled = false;
    btn.innerHTML = `${ic("cpu")}Train model`;
  }
}

// ------------------------------------------------------------------ attendance
async function loadAttendance(date) {
  let d;
  try { d = await api("/api/attendance" + (date ? `?date=${date}` : "")); } catch (e) { return toast(e.message, "err"); }
  await refreshPeopleCache();
  const sel = $("#att-date");
  const today = new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 10);
  const dates = [...new Set([today, ...d.dates])].sort().reverse();
  sel.innerHTML = dates.map(x => `<option value="${x}">${x === today ? `Today (${x})` : x}</option>`).join("");
  sel.value = d.date;
  $("#att-export").href = `/api/attendance/download?date=${d.date}`;
  $("#att-export").toggleAttribute("disabled", !d.rows.length);
  $("#att-export").style.pointerEvents = d.rows.length ? "" : "none";
  $("#att-export").style.opacity = d.rows.length ? "" : ".5";
  $("#att-present").textContent = d.rows.length;
  $("#att-absent").textContent = d.absent.length;
  $("#att-rate").textContent = d.registered ? `${Math.round((d.rows.filter(r => peopleCache[r.Name]).length / d.registered) * 100)}%` : "–";
  $("#att-empty").hidden = d.rows.length > 0;
  $("#att-table").innerHTML = d.rows.map((r, i) => {
    const m = parseFloat(r["Match %"]) || 0;
    return `<tr><td class="mono muted">${i + 1}</td><td><div class="who">${avatar(r.Name)}${esc(pretty(r.Name))}</div></td>
      <td class="mono">${esc(r.Time)}</td>
      <td><div style="display:flex;align-items:center;gap:8px"><div class="mini-bar" style="width:70px"><div style="width:${m}%;background:var(--green)"></div></div><span class="mono small">${m.toFixed(0)}%</span></div></td>
      <td style="text-align:right"><button class="btn sm ghost-danger" data-rm="${esc(r.Name)}" title="Remove entry">${ic("x")}</button></td></tr>`;
  }).join("");
  $("#att-absent-list").innerHTML = d.absent.length ? d.absent.map(n => `<span class="chip">${avatar(n)}${esc(pretty(n))}</span>`).join("")
    : `<div class="empty-line" style="width:100%">${d.registered ? "Everyone is present 🎉" : "No registered people"}</div>`;
  $$("[data-rm]").forEach(b => b.onclick = async () => {
    if (!(await confirmDialog("Remove entry?", `Remove ${pretty(b.dataset.rm)} from attendance on ${d.date}? Use this to fix a wrong match.`, "Remove"))) return;
    try { await api(`/api/attendance/${d.date}/${encodeURIComponent(b.dataset.rm)}`, { method: "DELETE" }); loadAttendance(d.date); }
    catch (e) { toast(e.message, "err"); }
  });
}
$("#att-date").onchange = () => loadAttendance($("#att-date").value);
$("#att-refresh").onclick = () => loadAttendance($("#att-date").value);

// ------------------------------------------------------------------ image test
let imgMode = "recognize", lastFile = null;
$$("#img-seg button").forEach(b => b.onclick = () => {
  imgMode = b.dataset.mode;
  $$("#img-seg button").forEach(x => x.classList.toggle("active", x === b));
  if (lastFile) analyse(lastFile);
});
$("#img-thr").oninput = () => { $("#img-thr-val").textContent = $("#img-thr").value; };
$("#img-thr").onchange = () => { if (lastFile && imgMode === "recognize") analyse(lastFile); };
$("#img-pick").onclick = () => $("#img-file").click();
$("#img-file").onchange = () => { if ($("#img-file").files[0]) analyse($("#img-file").files[0]); $("#img-file").value = ""; };
const drop = $("#drop");
["dragenter", "dragover"].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.add("over"); }));
["dragleave", "drop"].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.remove("over"); }));
drop.addEventListener("drop", e => { const f = e.dataTransfer.files[0]; if (f) analyse(f); });

async function analyse(file) {
  if (!file.type.startsWith("image/")) return toast("Please choose an image file", "err");
  lastFile = file;
  await refreshPeopleCache();
  const fd = new FormData();
  fd.append("image", file); fd.append("mode", imgMode); fd.append("threshold", $("#img-thr").value);
  $("#img-loading").classList.add("show");
  try {
    const d = await api("/api/image", { method: "POST", body: fd });
    $("#img-out").src = d.image; $("#img-out").hidden = false;
    $("#drop-inner").hidden = true; drop.classList.add("has-img");
    $("#img-count").textContent = d.results.length;
    $("#img-results").innerHTML = d.results.length ? d.results.map(r => r.known === null
      ? `<div class="item"><div class="avatar face">${ic("scan")}</div><div class="grow"><b>${esc(r.name)}</b><small>${r.box[2]}×${r.box[3]} px at (${r.box[0]}, ${r.box[1]})</small></div></div>`
      : `<div class="item">${r.known ? avatar(r.name) : `<div class="avatar unknown">?</div>`}<div class="grow"><b>${esc(pretty(r.name))}</b><small>dist ${r.distance}</small></div>
         <div class="score"><span>${Math.round(r.score)}%</span><div class="meter"><div style="width:${r.score}%;background:${r.known ? "var(--green)" : "var(--red)"}"></div></div></div></div>`
    ).join("") : `<div class="empty-line">No faces found. Try a clearer, frontal photo.</div>`;
  } catch (e) {
    toast(e.message, "err", 5000);
  } finally {
    $("#img-loading").classList.remove("show");
  }
}

// ------------------------------------------------------------------ boot
paintIcons();
setLiveMode("detect");
window.addEventListener("beforeunload", () => { if (camStatus.running) navigator.sendBeacon("/api/camera/stop"); });
route();
poll();
})();
