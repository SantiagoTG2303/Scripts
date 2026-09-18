# Screenshots Automation

A small macOS automation that watches your local `~/Screenshots` folder and
automatically files every new screenshot away into a dated folder structure
under iCloud Drive:

```
~/com~apple~CloudDocs/Screenshots/<year>/<month>/Week/Day/
```

For example, `Screenshot 2026-02-09 at 11.40.21 AM.png` gets moved to:

```
2026/Feb/Week-02/Day-02/Screenshot 2026-02-09 at 11.40.21 AM.png
```


Weeks are 7-day buckets starting on the 1st of the month.
```
- Week-01 : [Day 1 - Day 7]
- Week-02 : [Day 8 - Day 14]
- Week-03 : [Day 15 - Day 21]
- Week-04 : [Day 22 - Last Day]
```

## How it works

- **[`screenshots_automation.py`](screenshots_automation.py)** — the script.
  On each run it waits 5 seconds (to let macOS finish writing the PNG), scans
  `~/Screenshots` for files matching macOS's `Screenshot ... .png` naming
  convention, and moves each one into its dated folder under iCloud Drive,
  creating folders as needed.
- **[`com.screenshot_automation.plist`](com.screenshot_automation.plist)** —
  a macOS LaunchAgent that watches `~/Screenshots` for changes (`WatchPaths`)
  and runs the script whenever a new file shows up.

## Requirements

- macOS
- Python 3 (uses only the standard library — no dependencies)
- iCloud Drive enabled, with Desktop & Documents sync (or just a
  `Screenshots` folder created manually under your iCloud Drive)

## Installation

1. Clone this repo somewhere permanent, e.g. `~/Scripts/Screenshots_Automation`.

2. Set your screenshot save location to `~/Screenshots`:
   - Press `Cmd+Shift+5` → **Options** → **Save to** → **Other Location...**
     → choose (or create) `~/Screenshots` in your home folder.

3. Edit `com.screenshot_automation.plist` and replace every
   `/Users/YOUR_USERNAME/...` path with your actual home directory path
   (or the path where you cloned this repo, if different from
   `~/Scripts/Screenshots_Automation`).

4. Copy the plist into `~/Library/LaunchAgents/`:
   ```bash
   cp com.screenshot_automation.plist ~/Library/LaunchAgents/
   ```

5. Load the LaunchAgent:
   ```bash
   launchctl load ~/Library/LaunchAgents/com.screenshot_automation.plist
   ```
