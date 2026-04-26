from typing import Tuple
import shutil
import sys
import os


# * Constants
# prefer_local_resource() 
IS_LOCAL    = True
IS_BUNDLED  = False


# * Functions
def resource_path(*parts) -> str:
    """ 
    Returns bundled assets using _MEIPASS if running as onefile EXE,
    returns using current project directory files, if ran using Python (not exe)
    
    :param parts: The parts of the path to the file, relative to the resource directory
    :return: The path to the file in the resource location
    :rtype: str
    """

    # PyInstaller onefile extracts bundled files to _MEIPASS
    base = getattr(sys, "_MEIPASS", os.path.abspath("."))

    return os.path.join(base, *parts)


def writable_path(*parts) -> str:
    """ 
    Returns bundled assets using _MEIPASS if running as onefile EXE,
    returns using current project directory files, if ran using Python (not exe)
    
    :param parts: The parts of the path to the file, relative to the writable directory
    :return: The path to the file in the writable location
    :rtype: str
    """
    
    # Write next to the exe when frozen, else current project dir
    base = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.abspath(".")

    return os.path.join(base, *parts)


def ensure_configurable(*parts) -> str:
    """
    Ensures that the file at the given path exists in a writable location, 
    if not, it copies it from the resource path to the writable path

    :param parts: The parts of the path to the file, relative to the resource/writable directory
    :return: The path to the file in the writable location
    :rtype: str
    """

    # Get the destination path in the writable location
    destination = writable_path(*parts)

    # If the file doesn't exist in the writable location, copy it from the resource path
    if not os.path.exists(destination):
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        shutil.copy(resource_path(*parts), destination)

    return destination

def prefer_local_resource(*parts) -> Tuple[str, bool]:
    """
    Returns the path to a local resource if it exists, otherwise returns the path to the bundled resource.

    :param parts: The parts of the path to the file, relative to the resource/writable directory
    :return: A tuple containing the path to the file and a boolean indicating whether the file is local or bundled (`True` if local)
    :rtype: Tuple[str, bool]
    """

    # Get the path to the file in the writable location
    localPath = writable_path(*parts)
    
    # Check if the file exists locally
    if os.path.exists(localPath):
        # If it does, return that path
        return localPath, IS_LOCAL

    # Otherwise, return the path to the bundled resource   
    return resource_path(*parts), IS_BUNDLED


if __name__ == "__main__":
    print("[!] This file is not ment to be run!\n\n")
    input("Press \"Enter\" to exit . . .")