Set objShell = CreateObject("WScript.Shell")
objShell.CurrentDirectory = "C:\Users\josh\Docs\lab\Magnifier"
objShell.Run "venv\Scripts\pythonw.exe magnifier.py", 0, False
