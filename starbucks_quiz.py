"""
Starbucks Drink Quiz
====================
Guess the drink from its description. Multiple choice, 4 options.
Run with:  python starbucks_quiz.py
"""

import csv
import os
import random
import sys

# ── CONFIG ────────────────────────────────────────────────────────────────────
CSV_FILE     = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "starbucks_drinks_short_descriptions.csv")
NUM_CHOICES  = 4
DIVIDER      = "-" * 60


# ── COLORS (works in PowerShell / Windows Terminal) ───────────────────────────
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    GREEN  = "\033[92m"
    RED    = "\033[91m"
    YELLOW = "\033[93m"
    CYAN   = "\033[96m"
    DIM    = "\033[2m"
    WHITE  = "\033[97m"

def enable_ansi():
    """Enable ANSI escape codes and UTF-8 output on Windows."""
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass
    # Force UTF-8 stdout so special chars don't crash on cp1252
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

def bold(text):     return f"{C.BOLD}{text}{C.RESET}"
def green(text):    return f"{C.GREEN}{C.BOLD}{text}{C.RESET}"
def red(text):      return f"{C.RED}{C.BOLD}{text}{C.RESET}"
def yellow(text):   return f"{C.YELLOW}{text}{C.RESET}"
def cyan(text):     return f"{C.CYAN}{text}{C.RESET}"
def dim(text):      return f"{C.DIM}{text}{C.RESET}"


# ── LOAD DATA ─────────────────────────────────────────────────────────────────
def load_drinks(path):
    drinks = []
    try:
        with open(path, encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            next(reader)                       # skip header
            for row in reader:
                if len(row) >= 2 and row[0].strip() and row[1].strip():
                    drinks.append({
                        "name":        row[0].strip(),
                        "description": row[1].strip(),
                    })
    except FileNotFoundError:
        print(red(f"\n  Error: could not find '{path}'"))
        print(dim("  Make sure starbucks_drinks_short_descriptions.csv is in the same folder.\n"))
        sys.exit(1)

    if len(drinks) < NUM_CHOICES:
        print(red(f"\n  Error: need at least {NUM_CHOICES} drinks in the CSV.\n"))
        sys.exit(1)

    return drinks


# ── BUILD A QUESTION ──────────────────────────────────────────────────────────
def make_question(correct, all_drinks):
    """Return (description, [(label, name)], correct_label)."""
    wrong_pool = [d for d in all_drinks if d["name"] != correct["name"]]
    wrong      = random.sample(wrong_pool, NUM_CHOICES - 1)
    options    = [correct["name"]] + [d["name"] for d in wrong]
    random.shuffle(options)

    labels        = ["A", "B", "C", "D"]
    labeled       = list(zip(labels, options))
    correct_label = next(lbl for lbl, name in labeled if name == correct["name"])

    return correct["description"], labeled, correct_label


# ── DISPLAY HELPERS ───────────────────────────────────────────────────────────
def clear():
    os.system("cls" if sys.platform == "win32" else "clear")

def print_header(current, total, score):
    print(f"\n  {dim(DIVIDER)}")
    print(f"  {bold('☕  STARBUCKS DRINK QUIZ')}")
    print(f"  {dim(DIVIDER)}")
    status = (
        f"  Question {cyan(str(current))}/{cyan(str(total))}   "
        f"Score: {green(str(score))} correct"
    )
    print(status)
    print(f"  {dim(DIVIDER)}\n")

def print_description(desc):
    # Word-wrap at ~55 chars
    words  = desc.split()
    lines  = []
    line   = []
    length = 0
    for word in words:
        if length + len(word) + 1 > 55 and line:
            lines.append(" ".join(line))
            line, length = [], 0
        line.append(word)
        length += len(word) + 1
    if line:
        lines.append(" ".join(line))

    print(f"  {bold('Description:')}")
    for ln in lines:
        print(f"    {yellow(ln)}")
    print()

def print_choices(labeled):
    for lbl, name in labeled:
        print(f"    {bold(lbl)})  {name}")
    print()

def print_hint():
    print(f"  {dim('Type A, B, C, or D — or Q to quit')}\n")


# ── MAIN QUIZ LOOP ────────────────────────────────────────────────────────────
def run_quiz(drinks):
    clear()
    total     = len(drinks)
    queue     = drinks[:]
    random.shuffle(queue)
    score     = 0
    asked     = 0

    print(f"\n  {bold('Welcome to the Starbucks Drink Quiz!  [Q to quit at any time]')}")
    print(f"  {dim(f'{total} drinks loaded. Press Enter to start...')}")
    input()

    while queue:
        asked  += 1
        current = queue.pop(0)
        desc, choices, correct_label = make_question(current, drinks)

        answered_correctly = False
        while not answered_correctly:
            clear()
            print_header(asked, total, score)
            print_description(desc)
            print_choices(choices)
            print_hint()

            try:
                raw = input("  Your answer: ").strip().upper()
            except (EOFError, KeyboardInterrupt):
                print(f"\n\n  {dim('Quiz exited. Final score:')} {green(str(score))}/{asked - 1}\n")
                sys.exit(0)

            if raw == "Q":
                print(f"\n  {dim('Quitting. Final score:')} {green(str(score))}/{asked - 1}\n")
                sys.exit(0)

            if raw not in ("A", "B", "C", "D"):
                print(f"\n  {red('Invalid input.')} Please type A, B, C, D, or Q.\n")
                input(dim("  Press Enter to try again..."))
                continue

            if raw == correct_label:
                score += 1
                answered_correctly = True
                clear()
                print_header(asked, total, score)
                print_description(desc)
                print_choices(choices)
                print(f"  {green('>>  Correct!')}  The answer is: {bold(current['name'])}\n")
                if queue:
                    input(dim("  Press Enter for the next question..."))
                else:
                    print(f"  {bold('You finished all questions!')}")
                    print(f"  Final score: {green(str(score))}/{total}\n")
                    input(dim("  Press Enter to exit..."))
            else:
                chosen_name = next(name for lbl, name in choices if lbl == raw)
                clear()
                print_header(asked, total, score)
                print_description(desc)
                print_choices(choices)
                print(f"  {red('XX  Incorrect.')} '{chosen_name}' is not right -- try again.\n")
                input(dim("  Press Enter to retry..."))

    print(f"\n  {green('Quiz complete!')} Final score: {bold(str(score))}/{total}\n")


# ── ENTRY POINT ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    enable_ansi()
    drinks = load_drinks(CSV_FILE)
    run_quiz(drinks)
