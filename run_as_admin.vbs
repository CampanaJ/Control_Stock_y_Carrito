Set UAC = CreateObject("Shell.Application")
UAC.ShellExecute "main.exe", "", "", "runas", 1
