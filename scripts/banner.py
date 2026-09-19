import os
import sys
import re
from datetime import datetime

# Enable ANSI colors and UTF-8 in Windows terminal
if sys.platform == "win32":
    os.system("")
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ANSI TrueColor / Colors matching the official SIH palette
SIH_ORANGE = "\033[38;2;255;110;35m"   # Left brain / circuit
SIH_GREEN  = "\033[38;2;45;210;90m"    # Right brain / binary
SIH_BLUE   = "\033[38;2;60;150;255m"   # SIH text & accents
WHITE      = "\033[97m"
GREEN      = "\033[38;2;152;195;121m"
KEY_CLR    = "\033[38;2;160;205;105m"
BORDER     = "\033[38;2;75;105;125m"
VAL_CLR    = "\033[97m"
AMBER      = "\033[38;2;255;165;95m"
RESET      = "\033[0m"

def visible_len(s):
    return len(re.sub(r'\033\[[0-9;]*m', '', s))

def make_box_row(key, val_str, inner_w=54):
    prefix = f"{KEY_CLR}{key:<8}{RESET} {VAL_CLR}{val_str}{RESET}"
    vis = visible_len(prefix)
    padding = " " * max(0, inner_w - vis)
    return f"{BORDER}│{RESET} {prefix}{padding} {BORDER}│{RESET}"

def make_box_top(title, inner_w=54):
    t_vis = len(title)
    left_dashes = "─" * 14
    right_dashes = "─" * max(0, inner_w - 16 - t_vis)
    return f"{BORDER}┌{left_dashes} {GREEN}{title}{RESET} {BORDER}{right_dashes}┐{RESET}"

def make_box_bottom(inner_w=54):
    return f"{BORDER}└{'─' * (inner_w + 2)}┘{RESET}"

date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Left-side ASCII Art: Exact match to the user's SIH Brain-Bulb Logo
sih_logo = [
    f"           {WHITE}│{RESET}           ",
    f"     {WHITE}╲     │     ╱{RESET}     ",
    f"  {WHITE}───   ┌──┴──┐   ───{RESET}  ",
    f"      {SIH_ORANGE}▄███{RESET}{WHITE}│{RESET}{SIH_GREEN}███▄{RESET}      ",
    f"  {WHITE}───{RESET} {SIH_ORANGE}██{WHITE}•{SIH_ORANGE}──{WHITE}•{RESET}{WHITE}│{RESET}{SIH_GREEN}10110{RESET} {SIH_GREEN}██{RESET}  {WHITE}───{RESET} ",
    f"     {SIH_ORANGE}███{WHITE}│{SIH_ORANGE}█{WHITE}│{RESET}{WHITE}│{RESET}{SIH_GREEN}010101{RESET}{SIH_GREEN}██{RESET}     ",
    f" {WHITE}───{RESET} {SIH_ORANGE}██{WHITE}•──•{RESET}{WHITE}│{RESET}{SIH_GREEN}101010{RESET}{SIH_GREEN}██{RESET} {WHITE}───{RESET} ",
    f"     {SIH_ORANGE}███{WHITE}│{SIH_ORANGE}█{WHITE}│{RESET}{WHITE}│{RESET}{SIH_GREEN}010101{RESET}{SIH_GREEN}██{RESET}     ",
    f"  {WHITE}───{RESET} {SIH_ORANGE}██{WHITE}└──•{RESET}{WHITE}│{RESET}{SIH_GREEN}10101{RESET} {SIH_GREEN}██{RESET}  {WHITE}───{RESET} ",
    f"      {SIH_ORANGE}▀███{RESET}{WHITE}│{RESET}{SIH_GREEN}███▀{RESET}      ",
    f"     {WHITE}╱     │     ╲{RESET}     ",
    f"  {WHITE}───      │      ───{RESET}  ",
    f"        {WHITE}┌─────┐{RESET}        ",
    f"        {WHITE}│ {SIH_BLUE}SIH{RESET} {WHITE}│{RESET}        ",
    f"        {WHITE}├──┬──┤{RESET}        ",
    f"        {WHITE}│  │  │{RESET}        ",
    f"        {WHITE}└──┴──┘{RESET}        ",
    f"          {WHITE}▀▀▀{RESET}          ",
    f" {WHITE}SMART INDIA HACKATHON{RESET} ",
    f"        {SIH_BLUE}2 0 2 6{RESET}        "
]

INNER_W = 54

# Right-side Content Boxes (Hardware box completely removed per request)
right_lines = [
    make_box_top("Session / SIH 2026", INNER_W),
    make_box_row("TEAM", "HEXARK // Smart India Hackathon 2026", INNER_W),
    make_box_row("PROJECT", "Veyra Sentinel — Forecast Reliability", INNER_W),
    make_box_row("PROBLEM", "PS 26079 // When Weather Forecasts Fail", INNER_W),
    make_box_row("DATE", date_str, INNER_W),
    make_box_bottom(INNER_W),
    "",
    make_box_top("Services & Endpoints", INNER_W),
    make_box_row("BACKEND", "http://127.0.0.1:8000  [FastAPI Engine]", INNER_W),
    make_box_row("FRONTEND", "http://127.0.0.1:5173  [React Dashboard]", INNER_W),
    make_box_row("DOCS", "http://127.0.0.1:8000/docs [Swagger UI]", INNER_W),
    make_box_bottom(INNER_W),
    "",
    f"{AMBER}Team HEXARK // Know When Forecasts May Fail.{RESET}",
    "",
    f"\033[90m● \033[36m● \033[35m● \033[34m● \033[33m● \033[32m● \033[31m● \033[37m●{RESET}"
]

print()
print(f"{GREEN}Veyra Sentinel v2.0 // Team HEXARK [SIH 2026]{RESET}")
print()

max_rows = max(len(sih_logo), len(right_lines))
ART_W = 27

for i in range(max_rows):
    if i < len(sih_logo):
        vis_w = visible_len(sih_logo[i])
        pad = " " * max(0, ART_W - vis_w)
        left_str = f"{sih_logo[i]}{pad}"
    else:
        left_str = " " * ART_W
    right_str = right_lines[i] if i < len(right_lines) else ""
    print(f"{left_str}   {right_str}")

print()
