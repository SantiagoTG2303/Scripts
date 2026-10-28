(() => {
  const TICK_MS = 5000;   // how often the darkness is recalculated; the CSS transition fills the gap
  const FADE_OUT_MS = 600;

  let state = { ...DIMMER_DEFAULTS };
  let overlay = null;
  let timer = null;
  let pausedForSession = null; // startedAt of the session we already paused video for

  function setStyle(el, prop, value) {
    el.style.setProperty(prop, value, "important"); // !important so the site's CSS can't interfere
  }

  function createOverlay() {
    const el = document.createElement("div");
    // A popover lives in the browser's "top layer", the same place fullscreen elements go.
    // That's what lets it sit above a fullscreen video player.
    el.setAttribute("popover", "manual");
    const styles = {
      position: "fixed", inset: "0", width: "100vw", height: "100vh",
      "max-width": "none", "max-height": "none", margin: "0", padding: "0", border: "none",
      background: "#000", opacity: "0", "pointer-events": "none", // clicks pass straight through
      transition: `opacity ${TICK_MS}ms linear`,
    };
    for (const [prop, value] of Object.entries(styles)) setStyle(el, prop, value);
    return el;
  }

  // Top-layer elements stack in the order they were shown, so after the page enters
  // fullscreen we re-show the overlay to put it back on top.
  function bringToFront() {
    if (!overlay) return;
    const parent = document.body || document.documentElement;
    if (overlay.parentNode !== parent) parent.appendChild(overlay);
    if (overlay.matches(":popover-open")) overlay.hidePopover();
    overlay.showPopover();
  }

  function tick() {
    if (!overlay.isConnected || !overlay.matches(":popover-open")) bringToFront();
    const { opacity, done } = dimmerProgress(state);
    setStyle(overlay, "opacity", String(opacity));

    if (done && state.pauseAtEnd && pausedForSession !== state.startedAt) {
      pausedForSession = state.startedAt;
      document.querySelectorAll("video").forEach((v) => v.pause());
    }
  }

  function start() {
    if (!overlay) overlay = createOverlay();
    setStyle(overlay, "transition", `opacity ${TICK_MS}ms linear`);
    bringToFront();
    getComputedStyle(overlay).opacity; // force a style flush so the first change fades in
    tick();
    if (!timer) timer = setInterval(tick, TICK_MS);
  }

  function stop() {
    clearInterval(timer);
    timer = null;
    if (!overlay) return;
    setStyle(overlay, "transition", `opacity ${FADE_OUT_MS}ms ease-out`);
    setStyle(overlay, "opacity", "0");
    setTimeout(() => {
      if (state.active || !overlay) return;
      if (overlay.matches(":popover-open")) overlay.hidePopover();
      overlay.remove();
    }, FADE_OUT_MS);
  }

  function apply() {
    state.active ? start() : stop();
  }

  chrome.storage.local.get(DIMMER_DEFAULTS).then((saved) => {
    state = saved;
    apply();
  });

  chrome.storage.onChanged.addListener((changes, area) => {
    if (area !== "local") return;
    for (const [key, { newValue }] of Object.entries(changes)) state[key] = newValue;
    apply();
  });

  document.addEventListener("fullscreenchange", () => {
    if (state.active) requestAnimationFrame(bringToFront);
  });
})();
