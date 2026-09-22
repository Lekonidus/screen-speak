# screen-speak

Select a screen region (like a screenshot), OCR the text, and read it aloud with **local** TTS. Built for games — notes, dialogue, parchments.

Omarchy/Linux supports **two engines** so you can A/B test:

| Engine | Feel | Hotkey |
|--------|------|--------|
| **Piper** | Fast, lighter | `SUPER CTRL SHIFT + PRINT` |
| **Kokoro** | More natural (British male `bm_george`) | `SUPER CTRL ALT + PRINT` |
| Stop either | | `SUPER CTRL SHIFT + BACKSPACE` |

Both are on-demand (nothing running when idle). Windows port is Piper-only for now.

---

## Linux (Omarchy / Hyprland)

### Install — Piper (already set up if you followed earlier)

```bash
pip install --user piper-tts
sudo pacman -S --needed espeak-ng tesseract tesseract-data-eng

mkdir -p ~/.local/share/piper
python3 -m piper.download_voices en_GB-northern_english_male-medium \
  --data-dir ~/.local/share/piper
```

### Install — Kokoro (second engine)

```bash
pip install --user kokoro-onnx soundfile

mkdir -p ~/.local/share/kokoro
curl -L -o ~/.local/share/kokoro/kokoro-v1.0.onnx \
  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/kokoro-v1.0.onnx
curl -L -o ~/.local/share/kokoro/voices-v1.0.bin \
  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/voices-v1.0.bin
```

### Scripts + binds

```bash
install -m 755 screen-speak screen-speak-stop screen-speak-kokoro-tts ~/.local/bin/
```

Add [`hypr/bindings.snippet.lua`](hypr/bindings.snippet.lua) to `~/.config/hypr/bindings.lua`, then `hyprctl reload`.

### Check

```bash
screen-speak --check
screen-speak-kokoro-tts --check
```

### Config

| Env var | Default | Purpose |
|---------|---------|---------|
| `SCREEN_SPEAK_VOICE` | `en_GB-northern_english_male-medium` | Piper voice |
| `SCREEN_SPEAK_VOICE_DIR` | `~/.local/share/piper` | Piper models |
| `SCREEN_SPEAK_KOKORO_VOICE` | `bm_george` | Kokoro voice (British male) |
| `SCREEN_SPEAK_KOKORO_SPEED` | `1.2` | Kokoro speed (>1 = faster) |
| `SCREEN_SPEAK_KOKORO_DIR` | `~/.local/share/kokoro` | Kokoro model dir |
| `OMARCHY_OCR_LANGS` | `eng` | Tesseract languages |

---

## Windows

See [`windows/`](windows/) — Piper + PowerShell installer. Kokoro not wired on Windows yet.

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\windows\install.ps1
```

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+PrintScreen` | Speak (Piper) |
| `Ctrl+Shift+Backspace` | Stop |
