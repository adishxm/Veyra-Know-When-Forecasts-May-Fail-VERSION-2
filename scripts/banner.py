import os
import sys
import re
import subprocess
import shutil
from datetime import datetime

# Enable ANSI colors and UTF-8 in Windows terminal
if sys.platform == "win32":
    os.system("")
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ANSI TrueColor / Colors matching the user's screenshot
PINK    = "\033[38;2;255;110;140m"
GREEN   = "\033[38;2;152;195;121m"
KEY_CLR = "\033[38;2;160;205;105m"
BORDER  = "\033[38;2;75;105;125m"
VAL_CLR = "\033[97m"
GRAY    = "\033[90m"
BAR_FIL = "\033[38;2;152;195;121m"
BAR_DIM = "\033[38;2;55;75;65m"
AMBER   = "\033[38;2;255;165;95m"
CYAN    = "\033[36m"
RESET   = "\033[0m"

def visible_len(s):
    return len(re.sub(r'\033\[[0-9;]*m', '', s))

def make_box_row(key, val_str, inner_w=52):
    prefix = f"{KEY_CLR}{key:<7}{RESET} {VAL_CLR}{val_str}{RESET}"
    vis = visible_len(prefix)
    padding = " " * max(0, inner_w - vis)
    return f"{BORDER}│{RESET} {prefix}{padding} {BORDER}│{RESET}"

def make_box_top(title, inner_w=52):
    t_vis = len(title)
    # ┌────────────── Title ────────────────────────────────┐
    left_dashes = "─" * 14
    right_dashes = "─" * max(0, inner_w - 16 - t_vis)
    return f"{BORDER}┌{left_dashes} {GREEN}{title}{RESET} {BORDER}{right_dashes}┐{RESET}"

def make_box_bottom(inner_w=52):
    return f"{BORDER}└{'─' * (inner_w + 2)}┘{RESET}"

# Query Hardware Info
def get_hardware():
    cpu = "Intel(R) Core(TM) Processor"
    gpu = "NVIDIA GeForce RTX GPU"
    total_ram, used_ram, ram_pct = 16.0, 8.0, 50
    total_disk, used_disk, disk_pct = 500.0, 200.0, 40

    try:
        ps_cmd = (
            "$cpu = (Get-CimInstance Win32_Processor | Select -First 1).Name.Trim(); "
            "$gpu = (Get-CimInstance Win32_VideoController | Where-Object { $_.Name -notmatch 'Virtual|Basic' } | Select -First 1).Name.Trim(); "
            "$os = Get-CimInstance Win32_OperatingSystem; "
            "$tRam = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2); "
            "$fRam = [math]::Round($os.FreePhysicalMemory / 1MB, 2); "
            "$uRam = [math]::Round($tRam - $fRam, 2); "
            "Write-Output \"$cpu`n$gpu`n$tRam`n$uRam\""
        )
        res = subprocess.check_output(["powershell", "-NoProfile", "-Command", ps_cmd], text=True, timeout=5)
        lines = [line.strip() for line in res.strip().splitlines() if line.strip()]
        if len(lines) >= 4:
            cpu = lines[0]
            gpu = lines[1]
            total_ram = float(lines[2])
            used_ram = float(lines[3])
            ram_pct = int(round((used_ram / total_ram) * 100))
    except Exception:
        pass

    try:
        total_b, used_b, free_b = shutil.disk_usage("C:\\")
        total_disk = round(total_b / (1024**3), 1)
        used_disk = round(used_b / (1024**3), 1)
        disk_pct = int(round((used_disk / total_disk) * 100))
    except Exception:
        pass

    return cpu, gpu, total_ram, used_ram, ram_pct, total_disk, used_disk, disk_pct

def make_bar(pct, width=12):
    filled = int(round((pct / 100.0) * width))
    filled = min(width, max(0, filled))
    empty = width - filled
    return f"{GRAY}[{BAR_FIL}{'■' * filled}{BAR_DIM}{'·' * empty}{GRAY}]"

# Collect specs
cpu, gpu, total_ram, used_ram, ram_pct, total_disk, used_disk, disk_pct = get_hardware()
ram_bar = make_bar(ram_pct, 12)
disk_bar = make_bar(disk_pct, 12)

raw_user = os.environ.get("USERNAME", "Aditya")
username = raw_user.capitalize() if raw_user.islower() else raw_user
date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Left-side ASCII Art (exact coral/pink aesthetic from screenshot - 36 chars wide)
art = [
    "              :                     ",
    "             +#-              :-    ",
    "      -.   +#####.           =##-   ",
    "    .###  +#########+       +#####+ ",
    "   +#####- **** -====* .****+* **:  ",
    "  ********--###.:**= *** -=:=:====: ",
    "  =####: ... **.:*###+ -..++- +####:",
    ":    *###+:+++: **. :--.+###.+####. ",
    "**:   **#+ =+        .**: .+#**= -==",
    ".###**+=: +#=-.+.    -*  :=:= -.+###",
    " ##########*..=### +###*   .**=--=##",
    "=######+--..+### -*######: *### -+##",
    " =*#########: .### *#########==-: |=",
    "   =##########. === +########+.**===",
    "      ..+###= . :+********:+   ==##-",
    "     -+##::+###: :=+- .+=. +########",
    "     =#########* =####+ -### :######",
    "   .###########*** *######-.*##:    ",
    "   *###########- -#######+=+*#*     ",
    "          =#######+                 ",
    "           .+###+                   ",
    "             :                      ",
    "                                    ",
    "                                    "
]

INNER_W = 54

# Right-side Content Boxes
right_lines = [
    f"{VAL_CLR}Hey, {GREEN}{username}{RESET}",
    "",
    make_box_top("Hardware", INNER_W),
    make_box_row("CPU", cpu[:43], INNER_W),
    make_box_row("GPU", gpu[:43], INNER_W),
    make_box_row("RAM", f"{used_ram:.2f} GiB / {total_ram:.2f} GiB {ram_bar} {ram_pct:>2}%", INNER_W),
    make_box_row("DRIVE", f"C:\\ {used_disk:.1f} GiB / {total_disk:.1f} GiB {disk_bar} {disk_pct:>2}%", INNER_W),
    make_box_bottom(INNER_W),
    "",
    make_box_top("Session / SIH 2026", INNER_W),
    make_box_row("TEAM", "HEXARK // Smart India Hackathon 2026", INNER_W),
    make_box_row("PROJECT", "Veyra Sentinel — Forecast Reliability", INNER_W),
    make_box_row("PROBLEM", "PS 26079 // When Weather Forecasts Fail", INNER_W),
    make_box_row("DATE", date_str, INNER_W),
    make_box_bottom(INNER_W),
    "",
    make_box_top("Live Services", INNER_W),
    make_box_row("BACKEND", "http://127.0.0.1:8000  [FastAPI Engine]", INNER_W),
    make_box_row("FRONTEND", "http://127.0.0.1:5173  [React Dashboard]", INNER_W),
    make_box_row("DOCS", "http://127.0.0.1:8000/docs [Swagger UI]", INNER_W),
    make_box_bottom(INNER_W),
    "",
    f"{AMBER}Bonsoir! Team HEXARK. Know When Forecasts May Fail.{RESET}",
    "",
    f"\033[90m● \033[36m● \033[35m● \033[34m● \033[33m● \033[32m● \033[31m● \033[37m●{RESET}"
]

print()
print(f"{GREEN}PowerShell 7.6.3 / Veyra Sentinel v2.0{RESET}")
print()

max_rows = max(len(art), len(right_lines))
for i in range(max_rows):
    left_str = f"{PINK}{art[i]}{RESET}" if i < len(art) else " " * 36
    right_str = right_lines[i] if i < len(right_lines) else ""
    print(f"{left_str}   {right_str}")

print()
