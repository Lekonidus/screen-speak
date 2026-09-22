-- Screen-select OCR + TTS (A/B: Piper vs Kokoro)
-- Add to ~/.config/hypr/bindings.lua
o.bind("SUPER + CTRL + SHIFT + PRINT", "Speak selection (Piper)", "screen-speak piper")
o.bind("SUPER + CTRL + ALT + PRINT", "Speak selection (Kokoro)", "screen-speak kokoro")
o.bind("SUPER + CTRL + SHIFT + BACKSPACE", "Stop speaking selection", "screen-speak-stop")
