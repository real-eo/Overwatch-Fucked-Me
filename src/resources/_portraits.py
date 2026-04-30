# Global imports
from tkinter import PhotoImage
from pathlib import Path
import sys

# Same level imports
try:                from manager                    import resource_path
except ImportError: from src.resources.manager      import resource_path

# Super level imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path: sys.path.insert(0, str(PROJECT_ROOT))

from src.constants import ALL_HERO_IDS, ROLE_ALL


# ? We need to keep a reference to the portraits we set on the
# ? labels, otherwise they get garbage collected and disappear
# ? from the UI. This is a quirk of how Tkinter handles images
# Store the portraits as PhotoImage objects in a dictionary for easy access. 
HERO_3X3 = {
    hero: PhotoImage(
        file=resource_path(
            "res", 
            "portraits", 
            "" if hero == "blank" else ROLE_ALL, 
            f"{hero}.png"
        )
    ).subsample(3, 3)
    for hero in ["blank"] + ALL_HERO_IDS
}
    
HERO_4X4 = {
        hero: PhotoImage(
        file=resource_path(
            "res", 
            "portraits", 
            "" if hero == "blank" else ROLE_ALL, 
            f"{hero}.png"
        )
    ).subsample(4, 4)
    for hero in ["blank"] + ALL_HERO_IDS
}

HERO_6X6 = {
        hero: PhotoImage(
        file=resource_path(
            "res", 
            "portraits", 
            "" if hero == "blank" else ROLE_ALL, 
            f"{hero}.png"
        )
    ).subsample(6, 6)
    for hero in ["blank"] + ALL_HERO_IDS
}

