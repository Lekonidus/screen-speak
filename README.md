# screen-speak

Select a screen region (like a screenshot), OCR the text, and read it aloud with **local** Piper TTS. Built for games — notes, dialogue, parchments.

Same idea on Linux (Omarchy/Hyprland) and Windows.

---

## Linux (Omarchy / Hyprland)

### Hotkeys

| Shortcut | Action |
|----------|--------|
| `SUPER CTRL SHIFT + PRINT` | Select region → OCR → speak |
| `SUPER CTRL SHIFT + BACKSPACE` | Stop speaking |

### Install

Needs Wayland capture tools Omarchy already ships: `grim`, `slurp`, `hyprpicker`, `tesseract`, `wl-copy`, `ffplay`.

```bash
pip install --user piper-tts
# or: yay -S piper-tts
sudo pacman -S --needed espeak-ng tesseract tesseract-data-eng

mkdir -p ~/.local/share/piper
python3 -m piper.download_voices en_GB-northern_english_male-medium \
  --data-dir ~/.local/share/piper

install -m 755 screen-speak screen-speak-stop ~/.local/bin/
```

Add the binds from [`hypr/bindings.snippet.lua`](hypr/bindings.snippet.lua) to `~/.config/hypr/bindings.lua`, then:

```bash
hyprctl reload
```

### Check

```bash
screen-speak --check
```

---

## Windows

### Install

In PowerShell (from a clone of this repo):

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\windows\install.ps1
```

The installer will:

1. Install Python, Tesseract OCR, FFmpeg (`ffplay`), and AutoHotkey via `winget` (if available)
2. Install Python packages (`piper-tts`, Pillow, pytesseract)
3. Download the British male voice `en_GB-northern_english_male-medium`
4. Copy scripts to `%LOCALAPPDATA%\screen-speak`
5. Add Start Menu shortcuts and register login hotkeys

Flags:

```powershell
.\windows\install.ps1 -SkipWinget    # you already installed deps
.\windows\install.ps1 -SkipHotkeys   # no AutoHotkey startup entry
```

### Hotkeys

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+PrintScreen` | Select region → OCR → speak |
| `Ctrl+Shift+Backspace` | Stop speaking |

You can also use **Start Menu → screen-speak**.

### Notes

- Drag a rectangle on the dimmed overlay; `Esc` cancels.
- Raw OCR text is copied to the clipboard; speech uses cleaned punctuation (same as Linux).
- Some exclusive-fullscreen games block screen capture — try borderless windowed.
- Voice / speed: set `SCREEN_SPEAK_VOICE` or edit `length-scale` in `screen_speak.py`.

---

## Config

| Env var | Default | Purpose |
|---------|---------|---------|
| `SCREEN_SPEAK_VOICE` | `en_GB-northern_english_male-medium` | Piper voice name |
| `SCREEN_SPEAK_VOICE_DIR` | Linux: `~/.local/share/piper` · Windows: `%LOCALAPPDATA%\screen-speak\voices` | Voice models |
| `OMARCHY_OCR_LANGS` / `SCREEN_SPEAK_OCR_LANGS` | `eng` | Tesseract languages |

Speech speed / naturalness live in the speak scripts (`--length-scale`, `--noise-scale`, `--noise-w-scale`).
Pause lengths for commas / dashes are `COMMA_PAUSE` / `DASH_PAUSE` in the prep code (measured options are listed in a comment there).
