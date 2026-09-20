#!/usr/bin/env python3
"""Screen-select OCR + local Piper TTS (Windows)."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path


VOICE = os.environ.get("SCREEN_SPEAK_VOICE", "en_GB-northern_english_male-medium")
VOICE_DIR = Path(
    os.environ.get(
        "SCREEN_SPEAK_VOICE_DIR",
        Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "screen-speak" / "voices",
    )
)
OCR_LANGS = os.environ.get("SCREEN_SPEAK_OCR_LANGS", "eng")


def heading(line: str) -> bool:
    letters = [c for c in line if c.isalpha()]
    return (
        bool(letters)
        and len(letters) >= 3
        and len(line) < 60
        and sum(c.isupper() for c in letters) / len(letters) > 0.85
    )


def clean(s: str) -> str:
    s = s.replace("...", ".").replace("…", ".")
    s = re.sub(r'[“”"]', ", ", s)
    s = s.replace("/", ", ")
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\s+([,.;:!?])", r"\1", s)
    s = re.sub(r",\s*,+", ", ", s)
    s = re.sub(r"\s+", " ", s).strip(" ,")
    if s and s[-1] not in ".!?":
        s += "."
    return s


def flow(text: str) -> str:
    parts: list[str] = []
    buf: list[str] = []

    def flush() -> None:
        if buf:
            parts.append(clean(" ".join(buf)))
            buf.clear()

    for raw in text.replace("\r", "").split("\n"):
        line = re.sub(r"[ \t]+", " ", raw).strip()
        if not line:
            flush()
            continue
        letters = sum(c.isalpha() for c in line)
        if letters == 0 or (len(line) > 6 and letters / len(line) < 0.25):
            continue
        if heading(line):
            flush()
            parts.append(clean(line.title()))
            continue
        buf.append(line)
    flush()
    return " ".join(parts)


def self_check() -> None:
    sample = """HYGINUS: FABULAE
Try your hand at these excerpts. The grammar is
very simple and the stories are interesting... Though
they might give you nightmares.
"""
    out = flow(sample)
    assert "grammar is very simple" in out, out
    assert "interesting. Though" in out, out
    assert "Hyginus: Fabulae." in out, out
    assert "\n" not in out, out
    assert flow("Left / right now.") == "Left, right now."
    assert flow('He said "hello" now.') == "He said, hello, now."
    assert flow("Wait. Then go.") == "Wait. Then go."
    print("ok")


def select_region_bbox() -> tuple[int, int, int, int] | None:
    """Fullscreen dim overlay; drag to select. Returns (left, top, right, bottom) or None."""
    import tkinter as tk

    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.attributes("-alpha", 0.25)
    root.attributes("-topmost", True)
    root.configure(bg="black")
    root.config(cursor="crosshair")

    canvas = tk.Canvas(root, cursor="crosshair", bg="black", highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)

    start: list[int] = []
    rect: dict = {"id": None}
    result: dict[str, tuple[int, int, int, int] | None] = {"bbox": None}

    def on_press(event: tk.Event) -> None:
        start.clear()
        start.extend([event.x_root, event.y_root])
        if rect["id"] is not None:
            canvas.delete(rect["id"])
        rect["id"] = canvas.create_rectangle(
            event.x, event.y, event.x, event.y, outline="white", width=2
        )

    def on_drag(event: tk.Event) -> None:
        if not start or rect["id"] is None:
            return
        x0 = start[0] - root.winfo_rootx()
        y0 = start[1] - root.winfo_rooty()
        canvas.coords(rect["id"], x0, y0, event.x, event.y)

    def on_release(event: tk.Event) -> None:
        if not start:
            root.destroy()
            return
        x1, y1 = start[0], start[1]
        x2, y2 = event.x_root, event.y_root
        left, right = sorted((x1, x2))
        top, bottom = sorted((y1, y2))
        if right - left < 4 or bottom - top < 4:
            result["bbox"] = None
        else:
            result["bbox"] = (left, top, right, bottom)
        root.destroy()

    def on_escape(_: tk.Event) -> None:
        result["bbox"] = None
        root.destroy()

    canvas.bind("<ButtonPress-1>", on_press)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)
    root.bind("<Escape>", on_escape)
    root.mainloop()
    return result["bbox"]


def capture_region(bbox: tuple[int, int, int, int]):
    from PIL import ImageGrab

    return ImageGrab.grab(bbox=bbox)


def ocr_image(image) -> str:
    import pytesseract

    tess = os.environ.get("TESSERACT_CMD") or shutil.which("tesseract")
    # Common winget / UB Mannheim install paths when not on PATH yet
    if not tess and sys.platform == "win32":
        for candidate in (
            Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
            / "Tesseract-OCR"
            / "tesseract.exe",
            Path(os.environ.get("LOCALAPPDATA", ""))
            / "Programs"
            / "Tesseract-OCR"
            / "tesseract.exe",
        ):
            if candidate.is_file():
                tess = str(candidate)
                break
    if tess:
        pytesseract.pytesseract.tesseract_cmd = tess
    return pytesseract.image_to_string(
        image,
        lang=OCR_LANGS,
        config="--oem 1 --psm 6 -c preserve_interword_spaces=1",
    )


def set_clipboard(text: str) -> None:
    flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", "Set-Clipboard -Value $input"],
            input=text,
            text=True,
            check=True,
            creationflags=flags,
        )
        return
    except Exception:
        pass
    import tkinter as tk

    r = tk.Tk()
    r.withdraw()
    r.clipboard_clear()
    r.clipboard_append(text)
    r.update()
    r.destroy()


def notify(msg: str) -> None:
    print(msg)


def stop_speak() -> None:
    stop = Path(__file__).with_name("screen_speak_stop.py")
    subprocess.run([sys.executable, str(stop)], check=False)


def speak(text: str) -> None:
    stop_speak()
    cmd = [
        sys.executable,
        "-m",
        "piper",
        "-m",
        VOICE,
        "--data-dir",
        str(VOICE_DIR),
        "--length-scale",
        "0.75",
        "--noise-scale",
        "0.75",
        "--noise-w-scale",
        "1.0",
        "--sentence-silence",
        "0.25",
    ]
    kwargs: dict = {
        "stdin": subprocess.PIPE,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
        "text": True,
    }
    if sys.platform == "win32":
        kwargs["creationflags"] = (
            subprocess.CREATE_NO_WINDOW
            | subprocess.DETACHED_PROCESS
            | subprocess.CREATE_NEW_PROCESS_GROUP
        )
    proc = subprocess.Popen(cmd, **kwargs)
    assert proc.stdin is not None
    proc.stdin.write(text + "\n")
    proc.stdin.close()
    time.sleep(0.05)


def main() -> int:
    if "--check" in sys.argv:
        self_check()
        return 0

    bbox = select_region_bbox()
    if not bbox:
        return 0

    image = capture_region(bbox)
    raw = (ocr_image(image) or "").strip()
    if not raw:
        notify("No text found in selection")
        return 1

    set_clipboard(raw)
    text = flow(raw)
    if not text:
        notify("No readable text in selection")
        return 1

    notify("Speaking selection…")
    speak(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
