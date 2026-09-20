; Screen-speak hotkeys (AutoHotkey v1 or v2 compatible syntax via v2)
; Ctrl+Shift+PrintScreen → speak selection
; Ctrl+Shift+Backspace   → stop speaking

#Requires AutoHotkey v2.0

InstallDir := EnvGet("LOCALAPPDATA") "\screen-speak"
SpeakBat := InstallDir "\screen-speak.bat"
StopBat := InstallDir "\screen-speak-stop.bat"

^+PrintScreen:: {
    if FileExist(SpeakBat)
        Run SpeakBat, InstallDir, Hide
}

^+Backspace:: {
    if FileExist(StopBat)
        Run StopBat, InstallDir, Hide
}
