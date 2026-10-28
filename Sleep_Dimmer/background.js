// Keyboard shortcut (Option+P by default) toggles dimming, even in fullscreen.
chrome.commands.onCommand.addListener(async (command) => {
  if (command !== "toggle-dimmer") return;
  const { active } = await chrome.storage.local.get({ active: false });
  await chrome.storage.local.set(active ? { active: false } : { active: true, startedAt: Date.now() });
});
