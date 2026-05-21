# Create a shortcut in the Start Menu for the Magnifier application

$WshShell = New-Object -ComObject WScript.Shell
$StartMenuPath = [Environment]::GetFolderPath("StartMenu")
$ShortcutPath = Join-Path $StartMenuPath "Programs\Desktop Magnifier.lnk"

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "C:\Users\josh\Docs\lab\Magnifier\run_silent.vbs"
$Shortcut.WorkingDirectory = "C:\Users\josh\Docs\lab\Magnifier"
$Shortcut.Description = "Desktop Magnifier - Magnify areas of your screen"
$Shortcut.IconLocation = "C:\Windows\System32\imageres.dll,11"
$Shortcut.Save()

Write-Host "Shortcut created successfully in Start Menu!"
Write-Host "You can now find 'Desktop Magnifier' in your Start Menu."
