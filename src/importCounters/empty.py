# Global imports
from pathlib import Path
from PIL import Image
import shutil
import json

# Same level imports
# // try:                from resolve                    import Path, shortcut
# // except ImportError: from src.extractHeroes.resolve  import Path, shortcut

# Super level imports
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path: sys.path.insert(0, str(PROJECT_ROOT))

from src.constants import CHARACTERS, ROLE_ALL, ROLE_TANK, ROLE_DPS, ROLE_SUPPORT


# Generate the empty dictionary for the counters
counters = {
    character: {
        "Tank": {}, 
        "DPS": {}, 
        "Support": {}
    } 
    for character in CHARACTERS[ROLE_TANK] 
                   + CHARACTERS[ROLE_DPS] 
                   + CHARACTERS[ROLE_SUPPORT]
}

# Use json.dump to write the dictionary to a file
with open("counters.json", "w") as countersFile:
    json.dump(counters, countersFile, indent=4)
