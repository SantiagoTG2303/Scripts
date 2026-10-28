const $ = (id) => document.getElementById(id);
let state = { ...DIMMER_DEFAULTS };

function render() {
  $("startVal").textContent = Math.round(state.startOpacity * 100) + "%";
  $("endVal").textContent = Math.round(state.endOpacity * 100) + "%";
  $("toggle").textContent = state.active ? "Stop" : "Start dimming";
  $("toggle").classList.toggle("on", state.active);

  if (state.active) {
    const { opacity, msLeft } = dimmerProgress(state);
    const min = Math.floor(msLeft / 60000);
    const sec = Math.floor((msLeft % 60000) / 1000);
    $("status").textContent = msLeft > 0
      ? `${Math.round(opacity * 100)}% dark · ${min}:${String(sec).padStart(2, "0")} left`
      : `${Math.round(opacity * 100)}% dark · fully dimmed`;
  } else {
    $("status").textContent = "";
  }
}

function save(changes) {
  Object.assign(state, changes);
  chrome.storage.local.set(changes);
  render();
}

chrome.storage.local.get(DIMMER_DEFAULTS).then((saved) => {
  state = saved;
  $("startOpacity").value = Math.round(state.startOpacity * 100);
  $("endOpacity").value = Math.round(state.endOpacity * 100);
  $("durationMin").value = state.durationMin;
  $("pauseAtEnd").checked = state.pauseAtEnd;
  render();
});

// Settings apply live, so you can drag a slider mid-session to go darker right away.
$("startOpacity").addEventListener("input", (e) => save({ startOpacity: e.target.value / 100 }));
$("endOpacity").addEventListener("input", (e) => save({ endOpacity: e.target.value / 100 }));
$("durationMin").addEventListener("input", (e) => {
  const minutes = Number(e.target.value);
  if (minutes >= 1) save({ durationMin: minutes });
});
$("pauseAtEnd").addEventListener("change", (e) => save({ pauseAtEnd: e.target.checked }));

$("toggle").addEventListener("click", () => {
  save(state.active ? { active: false } : { active: true, startedAt: Date.now() });
});

// Keep the countdown ticking, and stay in sync if the keyboard shortcut is used.
setInterval(render, 1000);
chrome.storage.onChanged.addListener((changes) => {
  for (const [key, { newValue }] of Object.entries(changes)) state[key] = newValue;
  render();
});
