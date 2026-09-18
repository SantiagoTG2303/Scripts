from calendar import month_abbr
from pathlib import Path
from time import sleep as s

# region ---CONFIG---
ROOT_DIR = Path.home()
# pathlib overloads the '/' operator -> joins path components
# *** RHS can not have leading '/' bc this makes path absolute, not relative to LHS
# *** If RHS did have '/', this line would effectively ignore the ROOT_DIR
SCREENSHOT_BASE_DIR = ROOT_DIR / Path("Screenshots")
ICLOUD_BASE_DIR = ROOT_DIR/ Path("Library/Mobile Documents/com~apple~CloudDocs/Screenshots")
# endregion ---CONFIG---

# region --- Setting Directory Names ---
def get_week_and_day(p : Path):
    day_of_month = int(p.name.strip()[19:21])
    # [1,2,3,4] - min to shrink 5 to 4
    week = min(((day_of_month - 1) // 7) + 1, 4)
    # constrain day to be 1-7 for weeks 1-3, and balloon to possibly 10 for the 4th week
    day = day_of_month - (7 * (week - 1))
    return (f"Week-{week:02d}", f"Day-{day:02d}")

def get_month(p : Path):
    month_num = int(p.name.strip()[16:18])
    return month_abbr[month_num]

def get_year(p : Path):
    return p.name.strip()[11:15]
# endregion --- Setting Directory Names ---

# region --- Path Verification / Building ---
def is_screenshot(p : Path):
    return p.name.startswith("Screenshot") and p.name.endswith(".png")

def move_file(p : Path):
    # builds directory path as : year/month/week/dayofweek and moves file there
    # ex:
    # Screenshot 2026-02-09 at 11.40.21 AM.png
    # 2026/Feb/Week-02/Day-02
    year = get_year(p)
    month = get_month(p)
    week, day = get_week_and_day(p)
    # build path
    screenshot_dir = ICLOUD_BASE_DIR / year / month / week / day
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    # move file
    p.rename(screenshot_dir / p.name)
# endregion --- Path Verification / Building ---

def main():
    # get all non directories
    s(5)
    files = [item for item in SCREENSHOT_BASE_DIR.iterdir() if item.is_file()]
    for file in files:
        if is_screenshot(file):
            move_file(file)

if __name__ == "__main__":
    main()