import json
import subprocess
import time
from pathlib import Path

# Directories to scan for repos
SCAN_ROOTS = [
    Path.home() / "Scripts", Path.home() / "Projects"
]
SCAN_MAX_DEPTH = 3
STALE_THRESHOLD_HOURS = 24

# Store last notification sate per repo -> LaunchAgent won't renotify constantly
STATE_FILE = Path.home() / "Scripts" / "Git_Reminder" / ".notified_state.json"

def discover_repos(roots: list[Path], max_depth: int) -> list[Path]:
    """
    Walk each root in `roots` up to `max_depth` levels and return the
    parent directory of every ".git" folder found.

    Hints:
    - Path.rglob("*") or a manual recursive walk both work; rglob is
      simpler but doesn't have a built-in depth limit, so you'll need to
      check len(path.relative_to(root).parts) if you want to enforce one.
    - A repo's marker is a ".git" directory (or file, for worktrees) in
      its root — not deeper.
    """
    repos = [
        # return path to all .git files (marker of a repo) -> return the parent (the actual repo)
        repo.parent
        for path in roots
        for repo in path.rglob(".git")
        if len(repo.relative_to(path).parts) <= max_depth
    ]
    return repos

def has_uncommitted_changes(repo: Path) -> bool:
    """
    Return True if `repo` has any uncommitted changes (staged, unstaged,
    or untracked).

    Hint: `git -C <repo> status --porcelain` prints nothing when the
    working tree is clean, and one line per changed/untracked file
    otherwise. Run it with subprocess.run(..., capture_output=True,
    text=True) and check whether stdout is empty.
    """

    git_status = subprocess.run(["git","-C",repo,"status","--porcelain"], capture_output = True, text = True)
    # if git_status.stdout is empty -> False -> no uncommitted changes
    return bool(git_status.stdout)
    
def seconds_since_last_commit(repo: Path) -> int:
    """
    Return how many seconds old the last commit is.

    Hint: `git -C <repo> log -1 --format=%ct` prints the last commit's
    Unix timestamp. Compare it against time.time().
    """

    seconds = int(subprocess.run(["git","-C",repo,"log","-1","--format=%ct"], capture_output = True, text = True).stdout)
    return int(time.time() - seconds)

def has_unpushed_commits(repo: Path) -> bool:
    """
    Return True if the current branch has commits that haven't been
    pushed to its upstream tracking branch.

    Hints:
    - `git -C <repo> log @{u}.. --oneline` lists commits present locally
      but not on the upstream branch.
    - This will error (nonzero return code) if the branch has no
      upstream configured — treat that as "nothing to report" rather
      than a crash. Check subprocess.run(...).returncode.
    """

    unpushed_commits = subprocess.run("git","-C",repo,"log","@{u}..","--oneline"], capture_output = True, text = True)
    if unpushed_commits.returncode != 0:
        # no upstream, or some other error -> nothing to report
        return False
    return bool(unpushed_commits.stdout)

# region --- Stale Determination ---
def check_repo(repo: Path) -> dict | None:
    """
    Combine the checks above into one verdict for a single repo.

    Should return something like:
        {"repo": repo, "reason": "uncommitted changes"} or
        {"repo": repo, "reason": "unpushed commits"}
    if the repo is stale, or None if it's clean / too recent to flag.

    Suggested logic:
    - Not stale at all if there are no uncommitted changes AND no
      unpushed commits.
    - Even if there ARE uncommitted changes, don't flag it unless
      seconds_since_last_commit(repo) exceeds STALE_THRESHOLD_HOURS
      (converted to seconds) -- otherwise you'll get pinged for a repo
      you're actively working in right now.
    """
    raise NotImplementedError


# endregion --- Stale Determination ---


# region --- Notification State (avoid duplicate nagging) ---
def load_notified_state() -> dict:
    """
    Read STATE_FILE (JSON) and return its contents, or an empty dict if
    the file doesn't exist yet.
    """
    raise NotImplementedError


def save_notified_state(state: dict) -> None:
    """
    Write `state` back to STATE_FILE as JSON.
    """
    raise NotImplementedError


def should_renotify(repo: Path, state: dict) -> bool:
    """
    Return True if `repo` either has no recorded notification yet, or
    its last notification was more than 24h ago (so you get a daily
    reminder, not a one-time-ever nag).
    """
    raise NotImplementedError


# endregion --- Notification State ---


# region --- Notification ---
def notify(stale: list[dict]) -> None:
    """
    Fire a single macOS notification summarizing every stale repo.

    Hint: shell out to `osascript -e 'display notification "<body>" with
    title "<title>"'` via subprocess.run(). Build the body string from
    the repo names in `stale` (e.g. "Scripts, project-x, dotfiles").

    Watch out for quote-escaping: repo names or the body string could
    break the AppleScript string if they contain quotes -- keep this in
    mind when formatting the -e argument.
    """
    raise NotImplementedError


# endregion --- Notification ---


def main():
    repos = discover_repos(SCAN_ROOTS, SCAN_MAX_DEPTH)
    state = load_notified_state()

    stale = []
    for repo in repos:
        result = check_repo(repo)
        if result and should_renotify(repo, state):
            stale.append(result)
            state[str(repo)] = {"last_notified": ...}  # TODO: timestamp

    if stale:
        notify(stale)
        save_notified_state(state)


if __name__ == "__main__":
    main()
