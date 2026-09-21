# Git Reminder

A small macOS automation that periodically scans your local git repositories
for uncommitted changes or unpushed commits, and fires a native notification
summarizing which ones need attention.

For example, if `RepoA` has uncommitted changes *and* unpushed commits,
and `RepoB` just has uncommitted changes, you'd get a notification like:

```
Uncommitted: RepoA, RepoB
Unpushed: RepoA
```

## How it works

- **[`GitChecker.py`](GitChecker.py)** — the script. On each run it walks
  `SCAN_ROOTS` looking for `.git` folders (skipping anything listed in
  `SILENCED_REPOS`), then for each repo it finds checks:
  - whether there are uncommitted changes (`git status --porcelain`)
  - whether there are commits that haven't been pushed to the branch's
    upstream (`git log @{u}..`)
  - how long ago the last commit was made

  A repo is only flagged once it's been sitting stale for longer than
  `STALE_THRESHOLD_HOURS`, so you won't get pinged about a repo you're
  actively working in right now. A small JSON state file
  (`.notified_state.json`) tracks when each repo was last notified about, so
  the same issue doesn't re-notify you again until that same threshold has
  passed a second time.
- **[`com.git_reminder.plist`](com.git_reminder.plist)** — a macOS
  LaunchAgent that runs the script once a day at a fixed time
  (`StartCalendarInterval`)

Notifications are delivered via [`pync`](https://pypi.org/project/pync/)


## Requirements

- macOS
- Python 3
- [`uv`](https://docs.astral.sh/uv/) (manages the virtual environment and
  the `pync` dependency)
- `git`, available on your `PATH`

## Installation

1. Clone this repo somewhere permanent, e.g. `~/Scripts/Git_Reminder`.

2. From inside that directory, install dependencies:
   ```bash
   uv sync
   ```
   This creates a `.venv` folder with `pync` (and `terminal-notifier`)
   installed. The LaunchAgent points directly at this venv's Python, not
   your system Python.

3. Edit `com.git_reminder.plist` and replace every `/Users/YOUR_USERNAME/...`
   path with your actual home directory path (or the path where you cloned
   this repo, if different from `~/Scripts/Git_Reminder`).

4. Copy the plist into `~/Library/LaunchAgents/`:
   ```bash
   cp com.git_reminder.plist ~/Library/LaunchAgents/
   ```

5. Load the LaunchAgent:
   ```bash
   launchctl load ~/Library/LaunchAgents/com.git_reminder.plist
   ```

6. Grant notification permission. 
Go to **System Settings → Notifications**, find
   `terminal-notifier` in the list, and make sure it's allowed.

## Configuration

All configuration lives at the top of `GitChecker.py`:

- **`SCAN_ROOTS`** — list of parent directories to search for repos (e.g.
  `~/Scripts`, `~/Projects`). Any `.git` folder found under these is picked
  up automatically, so new repos don't need to be added manually.
- **`SCAN_MAX_DEPTH`** — how many directory levels deep to search for a
  `.git` folder under each root.
- **`SILENCED_REPOS`** — repo folder names to always skip, regardless of
  their git status.
- **`STALE_THRESHOLD_HOURS`** — how many hours old the last commit must be
  before a repo's uncommitted/unpushed state is considered worth flagging,
  and also how long to wait before re-notifying about the same repo. Set
  this to something like `24` for a "once a day at most" reminder.

## Managing the LaunchAgent

```bash
# Check status (a "0" exit status means the last run succeeded)
launchctl list | grep com.git_reminder

# Run it immediately, without waiting for the scheduled time
launchctl start com.git_reminder

# Reload after editing the plist or moving the project
launchctl unload ~/Library/LaunchAgents/com.git_reminder.plist
launchctl load ~/Library/LaunchAgents/com.git_reminder.plist

# Stop it entirely
launchctl unload ~/Library/LaunchAgents/com.git_reminder.plist
```