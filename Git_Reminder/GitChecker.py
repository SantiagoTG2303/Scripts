import json
import subprocess
import time
from pathlib import Path
import pync

# Directories to scan for repos
SCAN_ROOTS = [
    Path.home() / "Scripts", Path.home() / "Projects"
]
SILENCED_REPOS = ["LaloStockTest","ESPP_Backtester"]
SCAN_MAX_DEPTH = 3
STALE_THRESHOLD_HOURS = 0

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
        and repo.parent.name not in SILENCED_REPOS
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
    
def seconds_since_last_commit(repo: Path) -> float:
    """
    Return how many seconds old the last commit is.

    Hint: `git -C <repo> log -1 --format=%ct` prints the last commit's
    Unix timestamp. Compare it against time.time().
    """

    result = subprocess.run(["git","-C",repo,"log","-1","--format=%ct"], capture_output = True, text = True)
    if result.returncode != 0:
        # repo has no commits yet -> treat as infinitely stale
        return float("inf")
    return (time.time() - float(result.stdout))

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

    # git log --oneline : prints out commit history, one per line : <commit_hash> /
    #                                                               <commits with HEAD -> main or origin/main pointing at them> /
    #                                                               <gc message>
    # with @{u}.. flag : only outputs local commits not no upstream branch
    unpushed_commits = subprocess.run(["git","-C",repo,"log","@{u}..","--oneline"], capture_output = True, text = True)
    if unpushed_commits.returncode != 0:
        # no upstream, or some other error -> nothing to report
        return False
    return bool(unpushed_commits.stdout)

def check_repo(repo: Path) -> dict | None:

    repo_status = {}

    # a little inefficient -> each of these function calls initiates a subprocess -> 6 initiated, only 3 actually needed
    if has_uncommitted_changes(repo) and has_unpushed_commits(repo) and seconds_since_last_commit(repo) > (STALE_THRESHOLD_HOURS * 3600):
        repo_status[repo.name] = "uncommited changes and unpushed commits"
    elif has_uncommitted_changes(repo) and seconds_since_last_commit(repo) > (STALE_THRESHOLD_HOURS * 3600):
        repo_status[repo.name] = "uncommited changes"
    elif has_unpushed_commits(repo) and seconds_since_last_commit(repo) > (STALE_THRESHOLD_HOURS * 3600):
        repo_status[repo.name] = "unpushed commits"

    return repo_status if repo_status else None

def load_notified_state() -> dict:

    if not STATE_FILE.exists():
        return {}
    with open(STATE_FILE) as f:
        return json.load(f)


def save_notified_state(state: dict) -> None:

    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def should_renotify(repo: Path, state: dict) -> bool:
    """
    Return True if `repo` either has no recorded notification yet, or
    its last notification was more than 24h ago
    """

    last_notified = state.get(str(repo))
    if last_notified is None:
        return True
    return (time.time() - last_notified) > (STALE_THRESHOLD_HOURS * 3600)

def notify(stale: list[dict]) -> None:

    uncommitted_repos = []
    unpushed_repos = []
    # stale contains a list of dicts in the form repo:reason (see check_repo)
    for entry in stale:
        [(repo, reason)] = entry.items()
        if "uncommited changes" in reason:
            uncommitted_repos.append(repo)
        if "unpushed commits" in reason:
            unpushed_repos.append(repo)

    lines = []
    if uncommitted_repos:
        lines.append(f"Uncommitted: {', '.join(uncommitted_repos)}")
    if unpushed_repos:
        lines.append(f"Unpushed: {', '.join(unpushed_repos)}")

    notif = "\n".join(lines)

    pync.notify(notif, title="Git Reminder")


def main():
    repos = discover_repos(SCAN_ROOTS, SCAN_MAX_DEPTH)
    state = load_notified_state()

    stale = []
    for repo in repos:
        result = check_repo(repo)
        if result and should_renotify(repo, state):
            stale.append(result)
            state[str(repo)] = time.time()

    if stale:
        notify(stale)
        save_notified_state(state)


if __name__ == "__main__":
    main()
