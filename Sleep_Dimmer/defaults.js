// Shared by the content script and the popup. Everything lives in chrome.storage.local,
// so every open tab dims together and a page reload picks up where it left off.
const DIMMER_DEFAULTS = {
  active: false,
  startedAt: 0,         // ms timestamp when dimming started
  startOpacity: 0.3,    // how dark it is right away (0 = no dimming, 1 = black)
  endOpacity: 0.9,      // how dark it ends up
  durationMin: 45,      // minutes to go from start to end
  pauseAtEnd: false,    // pause any playing video once fully dark
};

function dimmerProgress(s, now = Date.now()) {
  const t = Math.min(1, Math.max(0, (now - s.startedAt) / (s.durationMin * 60000)));
  return {
    opacity: s.startOpacity + (s.endOpacity - s.startOpacity) * t,
    done: t >= 1,
    msLeft: Math.max(0, s.startedAt + s.durationMin * 60000 - now),
  };
}
