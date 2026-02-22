Dim shell
Set shell = CreateObject("WScript.Shell")

Dim dir
dir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

Dim cmd
cmd = "cmd /c set PYTHONUTF8=1 && set PYTHONIOENCODING=utf-8 && """ & dir & "\..\바이브 코딩20260205\.venv\Scripts\pythonw.exe"" -X utf8 """ & dir & "\main4.py"""

shell.Run cmd, 0, False
