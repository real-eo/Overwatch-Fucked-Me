from pathlib import Path
import win32com.client

def shortcut(shortcut_path: Path) -> Path:
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(str(shortcut_path.resolve()))
    return Path(shortcut.Targetpath)