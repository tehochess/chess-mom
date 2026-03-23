"""
Vocabulary Trainer — powered by 3000.xlsx
A professional terminal-based study app with smart answer checking,
progress tracking, session stats, and multiple practice modes.
"""

import io
import json
import os
import re
import sys
import random
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Optional

# Force UTF-8 output on Windows so box-drawing / tick chars render correctly
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    import ctypes
    ctypes.windll.kernel32.SetConsoleOutputCP(65001)

import pandas as pd
from thefuzz import fuzz

# ─────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────
SCRIPT_DIR  = Path(__file__).parent
EXCEL_FILE  = SCRIPT_DIR / "3000.xlsx"
PROGRESS_FILE = SCRIPT_DIR / "vocab_progress.json"

# ─────────────────────────────────────────────
# ANSI colors (Windows 10+ supports these natively)
# ─────────────────────────────────────────────
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    GREEN  = "\033[92m"
    RED    = "\033[91m"
    YELLOW = "\033[93m"
    CYAN   = "\033[96m"
    DIM    = "\033[2m"
    BLUE   = "\033[94m"
    MAGENTA= "\033[95m"

def enable_ansi():
    """Enable ANSI on Windows console."""
    if sys.platform == "win32":
        import ctypes
        k32 = ctypes.windll.kernel32
        k32.SetConsoleMode(k32.GetStdHandle(-11), 7)

# ─────────────────────────────────────────────
# Data loading & cleaning
# ─────────────────────────────────────────────

# Regex to strip Chinese / CJK characters and leftover Chinese punctuation
_CHINESE_RE  = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\uff00-\uffef\u3000-\u303f]+')
_CLEAN_PUNCT = re.compile(r'[，。！？【】（）""''：；、]+')
_MULTI_DEF   = re.compile(r'\(\d+\)\s*')  # splits "(1)v. ... (2)v. ..."
_POS_RE      = re.compile(r'^((?:v\.|n\.|adj\.|adv\.|prep\.|conj\.|pron\.|int\.|phrase)\s*)', re.IGNORECASE)

def _clean_definition(raw: str) -> str:
    """Strip Chinese characters and tidy up a definition string."""
    text = _CHINESE_RE.sub('', raw)
    text = _CLEAN_PUNCT.sub('', text)
    text = re.sub(r'\s{2,}', ' ', text).strip(' ,;/')
    return text

def _extract_pos(definition: str) -> str:
    """Pull part-of-speech tag from the start of a definition."""
    m = _POS_RE.match(definition.strip())
    return m.group(1).strip().lower() if m else ''

def _split_multidefs(raw_def: str) -> list[str]:
    """
    Handle entries like '(1)v. meaning one (2)n. meaning two'.
    Returns a list of individual definition strings.
    """
    parts = _MULTI_DEF.split(raw_def)
    parts = [p.strip() for p in parts if p.strip()]
    return parts if parts else [raw_def.strip()]

def load_vocabulary() -> list[dict]:
    """
    Load 3000.xlsx.
    Schema (no header row — row 0 is real data):
      col 0 : English word
      col 1 : definition with Chinese translation
      col 2 : English-only definition (may have leftover Chinese punctuation)
    Returns a list of word dicts.
    """
    df = pd.read_excel(EXCEL_FILE, header=None)

    # The file has no header; pandas would have used row 0 as columns if
    # read with header=0, but we read with header=None so col names are 0,1,2.
    df.columns = ['word', 'def_with_cn', 'def_en_raw']

    # Drop completely blank rows
    df = df.dropna(how='all')

    # Coerce all values to string and strip
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()

    # Drop rows where the word looks like garbage (numbers, single chars, NaN string)
    df = df[df['word'].str.len() > 1]
    df = df[df['word'] != 'nan']

    # Normalise definitions
    df['def_clean'] = df['def_en_raw'].apply(_clean_definition)
    # Fallback: if def_en_raw was empty/short, derive from def_with_cn
    mask = df['def_clean'].str.len() < 4
    df.loc[mask, 'def_clean'] = df.loc[mask, 'def_with_cn'].apply(_clean_definition)

    # Extract part of speech
    df['pos'] = df['def_clean'].apply(_extract_pos)

    # Deduplicate: keep all entries (a word may have multiple rows = rare)
    # but build unique id = word (lowercase)
    df['word_lower'] = df['word'].str.lower()

    words = []
    seen: dict[str, int] = {}  # word_lower -> index into words

    for _, row in df.iterrows():
        wl = row['word_lower']
        raw_defs = _split_multidefs(row['def_clean'])

        entry = {
            'word'        : row['word'],
            'definitions' : raw_defs,      # list of strings
            'pos'         : row['pos'],
            'def_with_cn' : row['def_with_cn'],
        }

        if wl in seen:
            # Merge definitions into existing entry
            words[seen[wl]]['definitions'].extend(raw_defs)
        else:
            seen[wl] = len(words)
            words.append(entry)

    # Deduplicate definitions within each entry
    for w in words:
        seen_defs: list[str] = []
        for d in w['definitions']:
            if d not in seen_defs:
                seen_defs.append(d)
        w['definitions'] = seen_defs

    print(f"{C.DIM}  Loaded {len(words):,} vocabulary entries from {EXCEL_FILE.name}.{C.RESET}")
    return words

# ─────────────────────────────────────────────
# Answer validation
# ─────────────────────────────────────────────

def _normalize(text: str) -> str:
    """Lowercase, strip accents, collapse whitespace, remove most punctuation."""
    text = text.lower().strip()
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r"[^\w\s]", ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def _simple_plural(word: str) -> set[str]:
    """Return a small set of common pluralisations of a word."""
    variants = {word}
    if word.endswith('s'):
        variants.add(word[:-1])     # dogs -> dog
    if word.endswith('es'):
        variants.add(word[:-2])     # boxes -> box
    else:
        variants.add(word + 's')
        variants.add(word + 'es')
    # common -y -> -ies
    if word.endswith('y') and len(word) > 2:
        variants.add(word[:-1] + 'ies')
    return variants

# Fuzzy threshold — must be at least this similar to count as correct.
# 85 is conservative: catches minor typos but rejects clearly wrong answers.
FUZZY_THRESHOLD = 85

def check_answer(user_answer: str, correct_definitions: list[str]) -> tuple[bool, str]:
    """
    Returns (is_correct, best_match_definition).
    Tries exact normalised match first, then fuzzy match.
    For word→definition quizzes.
    """
    ua = _normalize(user_answer)
    if not ua:
        return False, correct_definitions[0]

    for defn in correct_definitions:
        cd = _normalize(defn)
        # Strip leading POS tag for comparison (e.g. "v. to leave..." -> "to leave...")
        cd_stripped = re.sub(r'^[a-z]+\.\s*', '', cd).strip()

        # 1. Exact normalised match
        if ua == cd or ua == cd_stripped:
            return True, defn

        # 2. Keyword/substring — user typed part of the correct answer
        if len(ua) >= 6 and (ua in cd or ua in cd_stripped):
            return True, defn

        # 3. Fuzzy match
        score = max(
            fuzz.ratio(ua, cd),
            fuzz.partial_ratio(ua, cd_stripped),
            fuzz.token_sort_ratio(ua, cd_stripped),
        )
        if score >= FUZZY_THRESHOLD:
            return True, defn

    return False, correct_definitions[0]

def check_word_answer(user_answer: str, correct_word: str) -> bool:
    """
    For definition→word quizzes.
    Allows minor typos and ignores pluralisation.
    """
    ua = _normalize(user_answer)
    cw = _normalize(correct_word)

    if not ua:
        return False
    if ua == cw:
        return True

    # Check pluralisation variants
    if ua in _simple_plural(cw) or cw in _simple_plural(ua):
        return True

    # Accept if correct word is a clear root of the user's answer
    # (e.g. "abandonned" contains "abandon" as a prefix)
    if len(cw) >= 5 and ua.startswith(cw):
        return True

    # Fuzzy — word answers require higher threshold (fewer chars → less tolerance)
    score = max(fuzz.ratio(ua, cw), fuzz.partial_ratio(cw, ua))
    threshold = 90 if len(cw) <= 5 else 80 if len(cw) >= 8 else FUZZY_THRESHOLD
    return score >= threshold

# ─────────────────────────────────────────────
# Progress persistence
# ─────────────────────────────────────────────

def load_progress() -> dict:
    if PROGRESS_FILE.exists():
        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {
        'word_stats': {},     # word -> {attempts, correct, wrong}
        'sessions'  : [],     # list of session summaries
        'last_pool' : [],     # words from last unfinished session
    }

def save_progress(progress: dict):
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

def record_result(progress: dict, word: str, correct: bool):
    ws = progress['word_stats']
    if word not in ws:
        ws[word] = {'attempts': 0, 'correct': 0, 'wrong': 0}
    ws[word]['attempts'] += 1
    if correct:
        ws[word]['correct'] += 1
    else:
        ws[word]['wrong'] += 1

def get_missed_words(progress: dict, all_words: list[dict]) -> list[dict]:
    ws = progress['word_stats']
    missed = [w for w in all_words if ws.get(w['word'], {}).get('wrong', 0) > 0]
    # Sort by wrong count descending
    missed.sort(key=lambda w: ws[w['word']]['wrong'], reverse=True)
    return missed

def build_weighted_pool(all_words: list[dict], progress: dict) -> list[dict]:
    """
    Return a shuffled pool where missed words appear more often.
    Missed words get 3 extra slots; unseen words get 1.
    """
    ws = progress['word_stats']
    pool = []
    for w in all_words:
        wrong = ws.get(w['word'], {}).get('wrong', 0)
        weight = 1 + (wrong * 2)  # more wrong = more slots, up to reasonable limit
        pool.extend([w] * min(weight, 5))
    random.shuffle(pool)
    return pool

# ─────────────────────────────────────────────
# Display helpers
# ─────────────────────────────────────────────

def header(text: str):
    width = 56
    print()
    print(f"{C.CYAN}{'─' * width}{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}  {text}{C.RESET}")
    print(f"{C.CYAN}{'─' * width}{C.RESET}")

def fmt_score(correct: int, total: int) -> str:
    pct = (correct / total * 100) if total else 0
    color = C.GREEN if pct >= 70 else C.YELLOW if pct >= 50 else C.RED
    return f"{color}{correct}/{total}  ({pct:.1f}%){C.RESET}"

def show_session_summary(session: dict):
    header("Session Summary")
    print(f"  Words attempted : {C.BOLD}{session['total']}{C.RESET}")
    print(f"  Correct         : {C.GREEN}{session['correct']}{C.RESET}")
    print(f"  Wrong           : {C.RED}{session['wrong']}{C.RESET}")
    print(f"  Accuracy        : {fmt_score(session['correct'], session['total'])}")
    if session.get('missed'):
        print(f"\n  {C.YELLOW}Words to review:{C.RESET}")
        for w in session['missed'][:10]:
            print(f"    • {C.BOLD}{w}{C.RESET}")
        if len(session['missed']) > 10:
            print(f"    … and {len(session['missed']) - 10} more")

def show_stats(progress: dict, all_words: list[dict]):
    header("Overall Statistics")
    ws = progress['word_stats']

    total_attempts = sum(v['attempts'] for v in ws.values())
    total_correct  = sum(v['correct']  for v in ws.values())
    total_wrong    = sum(v['wrong']    for v in ws.values())
    words_seen     = len(ws)
    words_total    = len(all_words)

    print(f"  Words seen      : {words_seen:,} / {words_total:,}")
    print(f"  Total attempts  : {total_attempts:,}")
    print(f"  Overall accuracy: {fmt_score(total_correct, total_attempts)}")
    print(f"  Sessions played : {len(progress['sessions'])}")

    # Most missed
    missed_sorted = sorted(ws.items(), key=lambda x: x[1]['wrong'], reverse=True)
    if missed_sorted:
        print(f"\n  {C.RED}Top 10 hardest words:{C.RESET}")
        for word, stats in missed_sorted[:10]:
            acc = stats['correct'] / stats['attempts'] * 100 if stats['attempts'] else 0
            print(f"    {C.BOLD}{word:<20}{C.RESET}  wrong={stats['wrong']}  acc={acc:.0f}%")

    # Best words
    best_sorted = [
        (w, s) for w, s in ws.items()
        if s['attempts'] >= 3 and s['wrong'] == 0
    ]
    if best_sorted:
        print(f"\n  {C.GREEN}Mastered words (0 wrong, ≥3 attempts):{C.RESET} {len(best_sorted)}")

    if progress['sessions']:
        print(f"\n  {C.DIM}Last session: {progress['sessions'][-1].get('date', '?')}{C.RESET}")

# ─────────────────────────────────────────────
# Quiz engine
# ─────────────────────────────────────────────

DIRECTIONS = ['word_to_def', 'def_to_word']

def run_quiz(
    pool: list[dict],
    progress: dict,
    direction: Optional[str] = None,   # None = alternate
    session_label: str = 'Quiz',
    limit: Optional[int] = None,
) -> dict:
    """
    Core quiz loop.
    Returns a session dict {total, correct, wrong, missed, date}.
    """
    if not pool:
        print(f"\n  {C.YELLOW}No words in pool.{C.RESET}")
        return {'total': 0, 'correct': 0, 'wrong': 0, 'missed': [], 'date': ''}

    if limit:
        pool = pool[:limit]

    header(session_label)
    print(f"  {len(pool)} words  |  type {C.BOLD}q{C.RESET} to quit anytime\n")

    correct_count = 0
    wrong_count   = 0
    missed_words: list[str] = []
    dir_toggle = 0

    for idx, entry in enumerate(pool, 1):
        word  = entry['word']
        defs  = entry['definitions']
        pos   = entry['pos']

        # Choose direction
        cur_dir = direction if direction else DIRECTIONS[dir_toggle % 2]
        dir_toggle += 1

        # ── Prompt ──────────────────────────────────────
        if cur_dir == 'word_to_def':
            prompt_line = (
                f"{C.BOLD}{C.BLUE}[{idx}/{len(pool)}]{C.RESET} "
                f"Word: {C.BOLD}{C.MAGENTA}{word}{C.RESET}"
                + (f"  {C.DIM}({pos}){C.RESET}" if pos else '')
            )
            print(prompt_line)
            print(f"  {C.DIM}What does it mean?{C.RESET}")
        else:
            display_def = defs[0]
            prompt_line = (
                f"{C.BOLD}{C.BLUE}[{idx}/{len(pool)}]{C.RESET} "
                f"Definition: {C.CYAN}{display_def}{C.RESET}"
            )
            print(prompt_line)
            print(f"  {C.DIM}What is the word?{C.RESET}")

        try:
            user_input = input(f"  {C.BOLD}>{C.RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if user_input.lower() in ('q', 'quit', 'exit'):
            break

        # ── Evaluate ────────────────────────────────────
        if cur_dir == 'word_to_def':
            is_correct, best_def = check_answer(user_input, defs)
        else:
            is_correct = check_word_answer(user_input, word)
            best_def   = defs[0]

        if is_correct:
            correct_count += 1
            record_result(progress, word, True)
            print(f"  {C.GREEN}✓ Correct!{C.RESET}")
        else:
            wrong_count += 1
            record_result(progress, word, False)
            if word not in missed_words:
                missed_words.append(word)
            print(f"  {C.RED}✗ Wrong.{C.RESET}")
            if cur_dir == 'word_to_def':
                print(f"  {C.DIM}Correct answer:{C.RESET} {best_def}")
                if len(defs) > 1:
                    for d in defs[1:3]:
                        print(f"              or: {d}")
            else:
                print(f"  {C.DIM}Correct word:{C.RESET} {C.BOLD}{word}{C.RESET}")

        # Running score every 10 questions
        total_so_far = correct_count + wrong_count
        if total_so_far % 10 == 0:
            print(f"  {C.DIM}Score so far: {fmt_score(correct_count, total_so_far)}{C.RESET}")

        print()

    session = {
        'total'  : correct_count + wrong_count,
        'correct': correct_count,
        'wrong'  : wrong_count,
        'missed' : missed_words,
        'date'   : datetime.now().strftime('%Y-%m-%d %H:%M'),
        'label'  : session_label,
    }
    return session

# ─────────────────────────────────────────────
# Menu screens
# ─────────────────────────────────────────────

def menu_start_quiz(all_words: list[dict], progress: dict):
    header("Start Quiz")
    print("  How many words?  (press Enter for 20, or type a number)")
    try:
        raw = input(f"  {C.BOLD}>{C.RESET} ").strip()
    except (EOFError, KeyboardInterrupt):
        return
    limit = 20
    if raw.isdigit():
        limit = max(1, min(int(raw), len(all_words)))

    print("\n  Direction?")
    print("    1. Alternate (word → meaning, meaning → word)  [default]")
    print("    2. Word → Meaning only")
    print("    3. Meaning → Word only")
    try:
        raw2 = input(f"  {C.BOLD}>{C.RESET} ").strip()
    except (EOFError, KeyboardInterrupt):
        return
    direction_map = {'1': None, '2': 'word_to_def', '3': 'def_to_word'}
    direction = direction_map.get(raw2, None)

    pool = build_weighted_pool(all_words, progress)
    session = run_quiz(pool, progress, direction=direction, session_label='Quiz', limit=limit)

    if session['total'] > 0:
        show_session_summary(session)
        progress['sessions'].append(session)
        save_progress(progress)

def menu_review_missed(all_words: list[dict], progress: dict):
    missed = get_missed_words(progress, all_words)
    if not missed:
        print(f"\n  {C.GREEN}No missed words yet — keep practicing!{C.RESET}")
        return
    print(f"\n  {C.YELLOW}{len(missed)} missed words found.{C.RESET}")
    pool = missed * 2  # review each missed word twice
    random.shuffle(pool)
    session = run_quiz(pool, progress, direction='word_to_def',
                       session_label='Review: Missed Words', limit=len(pool))
    if session['total'] > 0:
        show_session_summary(session)
        progress['sessions'].append(session)
        save_progress(progress)

def menu_practice_by_pos(all_words: list[dict], progress: dict):
    """Group by part of speech since we have no category column."""
    pos_groups: dict[str, list[dict]] = {}
    for w in all_words:
        key = w['pos'] if w['pos'] else 'unknown'
        pos_groups.setdefault(key, []).append(w)

    header("Practice by Part of Speech")
    pos_list = sorted(pos_groups.keys(), key=lambda k: -len(pos_groups[k]))
    for i, pos in enumerate(pos_list, 1):
        print(f"  {i:2}. {C.BOLD}{pos:<10}{C.RESET} ({len(pos_groups[pos])} words)")

    print()
    try:
        raw = input(f"  {C.BOLD}Choose number >{C.RESET} ").strip()
    except (EOFError, KeyboardInterrupt):
        return
    if not raw.isdigit() or not (1 <= int(raw) <= len(pos_list)):
        print(f"  {C.RED}Invalid choice.{C.RESET}")
        return

    chosen_pos = pos_list[int(raw) - 1]
    pool = list(pos_groups[chosen_pos])
    random.shuffle(pool)

    print(f"\n  How many words? (max {len(pool)}, Enter for 20)")
    try:
        raw2 = input(f"  {C.BOLD}>{C.RESET} ").strip()
    except (EOFError, KeyboardInterrupt):
        return
    limit = 20
    if raw2.isdigit():
        limit = max(1, min(int(raw2), len(pool)))

    session = run_quiz(pool, progress, direction=None,
                       session_label=f'Practice: {chosen_pos}', limit=limit)
    if session['total'] > 0:
        show_session_summary(session)
        progress['sessions'].append(session)
        save_progress(progress)

def menu_random_all(all_words: list[dict], progress: dict):
    pool = list(all_words)
    random.shuffle(pool)
    header("Random Mode — All Words")
    print("  How many words? (Enter for 30)")
    try:
        raw = input(f"  {C.BOLD}>{C.RESET} ").strip()
    except (EOFError, KeyboardInterrupt):
        return
    limit = 30
    if raw.isdigit():
        limit = max(1, min(int(raw), len(pool)))
    session = run_quiz(pool, progress, direction=None,
                       session_label='Random: All Words', limit=limit)
    if session['total'] > 0:
        show_session_summary(session)
        progress['sessions'].append(session)
        save_progress(progress)

def menu_resume(all_words: list[dict], progress: dict):
    """Resume last unfinished session pool if saved."""
    last = progress.get('last_pool', [])
    if not last:
        print(f"\n  {C.YELLOW}No saved session to resume.{C.RESET}")
        return
    # Rebuild pool from saved word list
    word_map = {w['word']: w for w in all_words}
    pool = [word_map[wl] for wl in last if wl in word_map]
    if not pool:
        print(f"\n  {C.YELLOW}Saved session words not found in vocabulary.{C.RESET}")
        return
    print(f"\n  Resuming session with {len(pool)} words.")
    session = run_quiz(pool, progress, direction=None,
                       session_label='Resumed Session', limit=None)
    progress['last_pool'] = []
    if session['total'] > 0:
        show_session_summary(session)
        progress['sessions'].append(session)
        save_progress(progress)

# ─────────────────────────────────────────────
# Main menu
# ─────────────────────────────────────────────

MENU_OPTIONS = [
    ("Start Quiz (smart weighted)", menu_start_quiz),
    ("Review Missed Words",         menu_review_missed),
    ("Practice by Part of Speech",  menu_practice_by_pos),
    ("Random Mode (all words)",     menu_random_all),
    ("Show Progress & Stats",       None),
    ("Resume Last Session",         menu_resume),
    ("Exit",                        None),
]

def main_menu(all_words: list[dict], progress: dict):
    enable_ansi()
    while True:
        print()
        print(f"{C.BOLD}{C.CYAN}╔══════════════════════════════════════════════════════╗")
        print(f"║          VOCABULARY TRAINER  ·  3000 Words           ║")
        print(f"╚══════════════════════════════════════════════════════╝{C.RESET}")

        ws = progress['word_stats']
        seen  = len(ws)
        total = len(all_words)
        missed_count = sum(1 for v in ws.values() if v['wrong'] > 0)
        overall_correct = sum(v['correct'] for v in ws.values())
        overall_attempts= sum(v['attempts'] for v in ws.values())
        acc_str = f"{overall_correct/overall_attempts*100:.1f}%" if overall_attempts else "—"

        print(f"  Words seen: {C.BOLD}{seen:,}/{total:,}{C.RESET}  "
              f"Missed: {C.RED}{missed_count}{C.RESET}  "
              f"Accuracy: {C.GREEN}{acc_str}{C.RESET}")
        print()

        for i, (label, _) in enumerate(MENU_OPTIONS, 1):
            print(f"  {C.BOLD}{i}.{C.RESET} {label}")

        print()
        try:
            raw = input(f"  {C.BOLD}Choose >{C.RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n  {C.DIM}Bye!{C.RESET}\n")
            break

        if not raw.isdigit():
            continue
        choice = int(raw)

        if choice == len(MENU_OPTIONS):  # Exit
            print(f"\n  {C.DIM}Progress saved. Goodbye!{C.RESET}\n")
            save_progress(progress)
            break
        elif choice == 5:  # Stats
            show_stats(progress, all_words)
        elif 1 <= choice < len(MENU_OPTIONS):
            _, fn = MENU_OPTIONS[choice - 1]
            if fn:
                fn(all_words, progress)
        else:
            print(f"  {C.RED}Invalid choice.{C.RESET}")

# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────

if __name__ == '__main__':
    print(f"\n{C.CYAN}Loading vocabulary…{C.RESET}")
    try:
        all_words = load_vocabulary()
    except FileNotFoundError:
        print(f"{C.RED}Error: '{EXCEL_FILE}' not found.{C.RESET}")
        sys.exit(1)

    progress = load_progress()
    main_menu(all_words, progress)
