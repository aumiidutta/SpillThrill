// ------------------------------------------------------------------
// CONFIG: paste your API Gateway invoke URL here after deployment.
// Example: "https://abc123xyz.execute-api.us-east-1.amazonaws.com/challenge"
// ------------------------------------------------------------------
const API_URL = "https://bni91guid1.execute-api.eu-north-1.amazonaws.com/challenge";

const STORAGE_KEY = "truthOrDareSeenIds"; // { truth: [...ids], dare: [...ids] }

// ---- DOM references ----
const promptView = document.getElementById("promptView");
const shuffleView = document.getElementById("shuffleView");
const resultView = document.getElementById("resultView");
const errorView = document.getElementById("errorView");

const truthBtn = document.getElementById("truthBtn");
const dareBtn = document.getElementById("dareBtn");
const anotherBtn = document.getElementById("anotherBtn");
const switchBtn = document.getElementById("switchBtn");
const retryBtn = document.getElementById("retryBtn");
const clearBtn = document.getElementById("clearBtn");

const resultTag = document.getElementById("resultTag");
const resultText = document.getElementById("resultText");
const resetNote = document.getElementById("resetNote");
const errorText = document.getElementById("errorText");
const tally = document.getElementById("tally");

let currentType = null; // "truth" | "dare" — whatever was last picked

// ---- localStorage helpers ----
function loadSeen() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : { truth: [], dare: [] };
  } catch {
    return { truth: [], dare: [] };
  }
}

function saveSeen(seen) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(seen));
}

function markSeen(type, id) {
  const seen = loadSeen();
  if (!seen[type].includes(id)) seen[type].push(id);
  saveSeen(seen);
  updateTally();
}

function resetSeenFor(type) {
  const seen = loadSeen();
  seen[type] = [];
  saveSeen(seen);
}

function updateTally() {
  const seen = loadSeen();
  tally.textContent = `Truths seen: ${seen.truth.length} \u00b7 Dares seen: ${seen.dare.length}`;
}

// ---- View state helpers ----
function showView(view) {
  [promptView, shuffleView, resultView, errorView].forEach((v) => v.classList.add("hidden"));
  view.classList.remove("hidden");
}

// ---- Core flow ----
async function playChallenge(type) {
  currentType = type;
  showView(shuffleView);

  const seen = loadSeen();
  const excludeIds = seen[type];

  try {
    // A tiny artificial delay makes the "shuffling" state feel real even
    // on a fast connection, and gives the die animation a moment to play.
    const [data] = await Promise.all([fetchChallenge(type, excludeIds), delay(500)]);
    renderResult(type, data);
  } catch (err) {
    renderError(err);
  }
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function fetchChallenge(type, excludeIds) {
  const url = new URL(API_URL);
  url.searchParams.set("type", type);
  if (excludeIds.length) url.searchParams.set("exclude", excludeIds.join(","));

  const res = await fetch(url.toString());
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

function renderResult(type, data) {
  if (data.reset) {
    resetSeenFor(type);
    resetNote.classList.remove("hidden");
  } else {
    resetNote.classList.add("hidden");
  }

  markSeen(type, data.id);

  resultTag.textContent = type === "truth" ? "Truth" : "Dare";
  resultTag.className = "result-tag " + (type === "truth" ? "result-tag--truth" : "result-tag--dare");
  resultText.textContent = data.text;
  switchBtn.textContent = type === "truth" ? "Switch to Dare" : "Switch to Truth";

  showView(resultView);
}

function renderError(err) {
  errorText.textContent = err.message || "Couldn't reach the server. Check your connection and try again.";
  showView(errorView);
}

// ---- Event wiring ----
truthBtn.addEventListener("click", () => playChallenge("truth"));
dareBtn.addEventListener("click", () => playChallenge("dare"));
anotherBtn.addEventListener("click", () => playChallenge(currentType));
switchBtn.addEventListener("click", () => playChallenge(currentType === "truth" ? "dare" : "truth"));
retryBtn.addEventListener("click", () => playChallenge(currentType || "truth"));

clearBtn.addEventListener("click", () => {
  saveSeen({ truth: [], dare: [] });
  updateTally();
});

// ---- Init ----
updateTally();
showView(promptView);