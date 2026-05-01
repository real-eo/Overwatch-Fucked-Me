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

from src.constants import ALL_HERO_IDS, COUNTERS_FILE


# Generate the empty dictionary for the counters
counters = {
    character: {} 
    for character in ALL_HERO_IDS
}

# Use json.dump to write the dictionary to a file
with open(COUNTERS_FILE, "w") as countersFile:
    json.dump(counters, countersFile, indent=4)
