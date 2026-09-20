# Building GitChecker.py — reference notes

Docs to read for each piece of the skeleton in `GitChecker.py`.

## Repo discovery

- `pathlib.Path.rglob` / `Path.glob`:
  https://docs.python.org/3/library/pathlib.html#pathlib.Path.glob
- `Path.relative_to` (useful for depth-limiting an rglob walk):
  https://docs.python.org/3/library/pathlib.html#pathlib.PurePath.relative_to

## Running git commands from Python

- `subprocess.run` — the main tool you'll use for every git check:
  https://docs.python.org/3/library/subprocess.html#subprocess.run
  Key args: `capture_output=True, text=True` to get stdout/stderr as
  strings, and `cwd=repo` (or the `git -C <path>` flag) to run against a
  specific repo without `cd`-ing.
- `git status --porcelain` (machine-readable, stable across git
  versions/config — don't parse plain `git status`):
  https://git-scm.com/docs/git-status#_porcelain_format_version_1
- `git log --format=...` placeholders (`%ct` = committer date, Unix
  timestamp):
  https://git-scm.com/docs/pretty-formats
- `@{u}` / `@{upstream}` revision shorthand for "this branch's tracking
  branch":
  https://git-scm.com/docs/gitrevisions#Documentation/gitrevisions.txt-emltbranchnamegtupstreamemegemmasterupstreamememuem

## Notifications

- `osascript` + `display notification` syntax:
  https://developer.apple.com/library/archive/documentation/LanguagesUtilities/Conceptual/MacAutomationScriptingGuide/PromptforUserInput.html
  (search "display notification" — it's a one-liner:
  `display notification "body" with title "title"`)
- Alternative: the `pync` PyPI package wraps this for you, if you'd
  rather not shell out to osascript directly:
  https://pypi.org/project/pync/

## Scheduling (LaunchAgent)

- Reuse the pattern from `Screenshots_Automation/com.screenshot_automation.plist`,
  but swap `WatchPaths` for `StartCalendarInterval` or `StartInterval`
  since this should run on a timer, not react to file changes:
  - `StartInterval`: run every N seconds. Simple, but drifts relative to
    wall-clock time.
  - `StartCalendarInterval`: run at a specific time of day (e.g. 6pm
    daily) — probably what you want for a "reminder."
  - launchd.plist man page (search both keys):
    https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html

## Persisting state between runs

- `json.load` / `json.dump` for `STATE_FILE`:
  https://docs.python.org/3/library/json.html
- `datetime`/`time` for comparing "now" vs. a stored timestamp:
  https://docs.python.org/3/library/time.html#time.time

## Suggested build order

1. `discover_repos` — print the list, sanity check it finds your repos.
2. `has_uncommitted_changes` + `seconds_since_last_commit` — test against
   a repo you know is dirty vs. one that's clean.
3. `has_unpushed_commits` — test on a repo with no upstream configured
   to make sure it doesn't crash.
4. `check_repo` — combine the above.
5. `notify` — get a single test notification firing manually first
   (`python3 GitChecker.py` from the terminal) before wiring up the
   LaunchAgent.
6. `load_notified_state` / `save_notified_state` / `should_renotify` —
   add last, once the core logic works, so you're not debugging state
   persistence and git logic at the same time.
7. Copy + adapt the plist from `Screenshots_Automation/` last.
