#!/usr/bin/env python3
"""Stop screen-speak Piper / ffplay playback (Windows)."""

from __future__ import annotations

import subprocess
import sys


def main() -> int:
    # Only the ffplay Piper spawned, not every ffplay on the machine.
    if sys.platform != "win32":
        pids = subprocess.run(
            ["pgrep", "-d,", "-f", "[p]ython.*-m piper"], capture_output=True, text=True
        ).stdout.strip()
        if pids:
            subprocess.run(["pkill", "-x", "ffplay", "-P", pids], check=False)
            subprocess.run(["pkill", "-f", "[p]ython.*-m piper"], check=False)
        return 0

    # wmic is deprecated; use PowerShell. Kill Piper's ffplay children, then Piper.
    subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            "$p = @(Get-CimInstance Win32_Process -Filter \"Name = 'python.exe' OR Name = 'pythonw.exe'\" "
            "| Where-Object { $_.CommandLine -match '-m piper' }); "
            "$ids = @($p | ForEach-Object { $_.ProcessId }); "
            "Get-CimInstance Win32_Process -Filter \"Name = 'ffplay.exe'\" "
            "| Where-Object { $ids -contains $_.ParentProcessId } "
            "| ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }; "
            "$p | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }",
        ],
        check=False,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
