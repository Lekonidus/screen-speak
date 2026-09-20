# screen-speak

Select a screen region (like a screenshot), OCR the text, and read it aloud with local Piper TTS. Built for games — notes, dialogue, parchments.

## Hotkeys (Omarchy / Hyprland)

| Shortcut | Action |
|----------|--------|
| `SUPER CTRL SHIFT + PRINT` | Select region → OCR → speak |
| `SUPER CTRL SHIFT + BACKSPACE` | Stop speaking |

## Install

Needs Wayland tools already used by Omarchy screenshots: `grim`, `slurp`, `hyprpicker`, `tesseract`, `wl-copy`, `ffplay`.

```bash
# TTS
pip install --user piper-tts
# or: yay -S piper-tts
sudo pacman -S --needed espeak-ng tesseract tesseract-data-eng

# Voice (British male, Northern English)
mkdir -p ~/.local/share/piper
python3 -m piper.download_voices en_GB-northern_english_male-medium \
  --data-dir ~/.local/share/piper

# Scripts
install -m 755 screen-speak screen-speak-stop ~/.local/bin/
```

Add the binds from [`hypr/bindings.snippet.lua`](hypr/bindings.snippet.lua) to `~/.config/hypr/bindings.lua`, then:

```bash
hyprctl reload
```

## Config

| Env var | Default | Purpose |
|---------|---------|---------|
| `SCREEN_SPEAK_VOICE` | `en_GB-northern_english_male-medium` | Piper voice name |
| `SCREEN_SPEAK_VOICE_DIR` | `~/.local/share/piper` | Voice model directory |
| `OMARCHY_OCR_LANGS` | `eng` | Tesseract languages |

Speech speed / naturalness are set in `screen-speak` (`--length-scale`, `--noise-scale`, `--noise-w-scale`).

## Check

```bash
screen-speak --check
```
