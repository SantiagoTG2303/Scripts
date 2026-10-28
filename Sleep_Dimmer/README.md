# Sleep Dimmer

A Chrome extension for falling asleep to videos. It puts a black layer over
the page that slowly gets darker over time, so the screen can go dimmer than
macOS's minimum brightness. It keeps working when a video is fullscreen.

For example, with the default settings the page starts out 30% darker and
fades to 90% darker over 45 minutes:

```
 0 min  → 30% dark
15 min  → 50% dark
30 min  → 70% dark
45 min  → 90% dark (stays here until you stop it)
```

## How it works

- **[`manifest.json`](manifest.json)**: tells Chrome what the extension is
  and what it's allowed to do. It loads the content script on every site,
  sets up the toolbar popup and background worker, and registers the
  keyboard shortcut. The only permission it needs is `storage`.
- **[`defaults.js`](defaults.js)**: the default settings, plus
  `dimmerProgress()`. That function works out how dark the overlay should be
  right now from when dimming started and how long it's set to take. Both
  the content script and the popup use it, so they always agree.
- **[`content.js`](content.js)**: runs inside every webpage and draws the
  overlay.
  - The overlay is a full-screen black `div` with `pointer-events: none`, so
    clicks go through it to the video controls underneath.
  - Every 5 seconds it recalculates the darkness. A 5-second CSS transition
    on `opacity` smooths out the steps between updates.
  - **Fullscreen:** normally, when a site goes fullscreen, only the
    fullscreen element is drawn and everything else on the page is hidden.
    To get around that, the overlay is a
    [popover](https://developer.mozilla.org/en-US/docs/Web/API/Popover_API),
    which puts it in the browser's *top layer*, the same layer fullscreen
    elements go in. Whatever enters the top layer last is drawn on top, so
    on every `fullscreenchange` event the overlay hides and re-shows itself
    to land above the player.
  - It listens to `chrome.storage.onChanged`, so starting, stopping or
    changing a setting takes effect right away in every open tab.
- **[`popup.html`](popup.html) / [`popup.js`](popup.js)**: the panel that
  opens from the toolbar button. It has sliders and settings, a
  Start/Stop button, and a live countdown. It only reads and writes
  `chrome.storage`; the content script does all the actual dimming.
- **[`background.js`](background.js)**: a service worker whose only job is
  the keyboard shortcut. It flips `active` in storage, the same thing the
  Start/Stop button does.

Because everything goes through `chrome.storage.local`, all tabs dim
together, and reloading a page picks up at the current darkness instead of
starting over.

## Installation

1. Go to `chrome://extensions`.
2. Turn on **Developer mode** (top right).
3. Click **Load unpacked** and choose this `Sleep_Dimmer` folder.
4. (Optional) Pin it from the puzzle-piece menu so the button stays in the
   toolbar.
5. Refresh any tabs that were already open. Chrome only adds the content
   script to pages loaded after the extension is installed.

**After editing any files**, click the reload icon on the extension's card
in `chrome://extensions`, then refresh the page you're testing on.

## Usage

- Click the toolbar button and press **Start dimming**, or press **⌥P**
  (Option+P) from any tab, including in fullscreen. Press it again to
  stop.
- To change the shortcut, go to `chrome://extensions/shortcuts`.

## Configuration

All settings are in the popup and apply immediately, even during a session.
The defaults live in [`defaults.js`](defaults.js):

- **Start darkness** (`startOpacity`): how dark it is as soon as you press
  Start. `0` is no dimming and `1` is fully black.
- **End darkness** (`endOpacity`): how dark it ends up. Setting this to 100%
  makes the screen completely black.
- **Minutes to reach end** (`durationMin`): how long the fade from start to
  end takes.
- **Pause video when fully dark** (`pauseAtEnd`): pauses any playing
  `<video>` on the page once the end darkness is reached. It only pauses
  once per session, so if you press play again it won't keep pausing.
