-- Screen-select OCR + Piper TTS (add to ~/.config/hypr/bindings.lua)
-- Next to SUPER CTRL + PRINT (Omarchy OCR)
o.bind("SUPER + CTRL + SHIFT + PRINT", "Speak text from selection", "screen-speak")
o.bind("SUPER + CTRL + SHIFT + BACKSPACE", "Stop speaking selection", "screen-speak-stop")
