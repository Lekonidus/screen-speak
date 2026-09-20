#!/usr/bin/env python3
"""Stop screen-speak Piper / ffplay playback (Windows)."""

from __future__ import annotations

import subprocess
import sys


def main() -> int:
    if sys.platform != "win32":
        subprocess.run(["pkill", "-f", "[p]ython.*-m piper"], check=False)
        subprocess.run(["pkill", "-x", "ffplay"], check=False)
        return 0

    flags = subprocess.CREATE_NO_WINDOW
    # Kill Piper python workers and ffplay audio.
    subprocess.run(
        ["taskkill", "/F", "/IM", "ffplay.exe"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=flags,
    )
    # Match python -m piper (wmic is deprecated; use PowerShell).
    subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            "Get-CimInstance Win32_Process -Filter \"Name = 'python.exe' OR Name = 'pythonw.exe'\" "
            "| Where-Object { $_.CommandLine -match '-m piper' } "
            "| ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }",
        ],
        check=False,
        creationflags=flags,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
