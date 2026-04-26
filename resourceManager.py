import sys
import os


def resource_path(*parts):
    """ 
    Returns bundled assets using _MEIPASS if running as onefile EXE,
    returns using current project directory files, if ran using Python (not exe)
    """

    # PyInstaller onefile extracts bundled files to _MEIPASS
    base = getattr(sys, "_MEIPASS", os.path.abspath("."))

    return os.path.join(base, *parts)


def writable_path(*parts):
    """ 
    Returns bundled assets using _MEIPASS if running as onefile EXE,
    returns using current project directory files, if ran using Python (not exe)
    """
    
    # Write next to the exe when frozen, else current project dir
    base = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.abspath(".")

    return os.path.join(base, *parts)


if __name__ == "__main__":
    print("[!] This file is not ment to be run!\n\n")
    input("Press \"Enter\" to exit . . .")