try:                from resolve                    import Path, shortcut
except ImportError: from src.extract_heros.resolve  import Path, shortcut
from PIL import Image
import os



# Constants
OVERWATCH_DATATOOL_LNK = Path("Overwatch DataTool.lnk") 
RELATIVE_HERO_ICON_PATH = Path("out", "HeroIcons")
PLAYABLE_HERO_ENTRY_THRESHOLD = 6                                                       # The amount of files+directories that must exist for the playable heros. This is only used as a filter to exclude bots, NPCs, etc.
SAVE_DIRECTORY = Path(".", "out", "imported")

# Variables
overwatchDataToolPath = shortcut(OVERWATCH_DATATOOL_LNK)
heroIconDirectory = Path(overwatchDataToolPath) / RELATIVE_HERO_ICON_PATH

# Get the list of playable heros by filtering the hero icon directory
playableHeroes: list[Path] = [
    hero                                                                                # Add the hero to the list
    for hero in heroIconDirectory.iterdir()                                             # from the hero icon directory
    if hero.is_dir()                                                                    # if it's a directory (not a file)
    and len(list(hero.iterdir())) >= PLAYABLE_HERO_ENTRY_THRESHOLD                      # which contains at least 6 entries (files + directories) 
] 

# Copy over the images which are exactly 256x256 and directly below each directory in playableHeroes into SAVE_DIRECTORY
for hero in playableHeroes:
    for index, file in enumerate(hero.iterdir()):
        if not (file.is_file() and file.suffix == ".png"):  continue
        
        with Image.open(file) as image: 
            image: Image.Image                                                          # Type hint for better autocompletion and readability
            
            if not image.size == (256, 256):                continue
            
            os.makedirs(SAVE_DIRECTORY / hero.name, exist_ok=True)                      # Create the hero's directory in the save directory if it doesn't exist
            image.save(SAVE_DIRECTORY / hero.name / f"{hero.name}-{index}.png")

