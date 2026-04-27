try:                from resolve                    import Path, shortcut
except ImportError: from src.extract_heros.resolve  import Path, shortcut
from PIL import Image
import os



# Constants
OVERWATCH_DATATOOL_LNK = Path("Overwatch DataTool.lnk") 
RELATIVE_HERO_ICON_PATH = Path("out", "HeroIcons")

PLAYABLE_HERO_ENTRY_THRESHOLD = 6                                                       # The amount of files+directories that must exist for the playable heros. This is only used as a filter to exclude bots, NPCs, etc.

SAVE_DIRECTORY_2D = Path(".", "out", "imported", "2D")
SAVE_DIRECTORY_3D = Path(".", "out", "imported", "3D")

IMAGE_2D_INDEX = 1                                                                      # ? This is just what i have noticed to be the trend - no other explaination other than that as of now
IMAGE_3D_INDEX = 0                                                                      # ? This is just what i have noticed to be the trend - no other explaination other than that as of now

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

# Ensure the save directories exist
SAVE_DIRECTORY_2D.mkdir(parents=True, exist_ok=True)
SAVE_DIRECTORY_3D.mkdir(parents=True, exist_ok=True)

# Copy over the images which are exactly 256x256 and directly below each directory in playableHeroes into the save directories
for hero in playableHeroes:
    images: list[Image.Image] = [
        Image.open(file)                                                                # Convert and add the file to the list as an Image object
        for file in hero.iterdir()                                                      # from each hero's directory
        if file.is_file()                                                               # if it's a file (not a directory)
        and file.suffix == ".png"                                                       # which is a PNG image
        and Image.open(file).size == (256, 256)                                         # and has the dimensions 256x256
    ]

    # Save 2D image 
    images[IMAGE_2D_INDEX].save(SAVE_DIRECTORY_2D / f"{hero.name}.png")                 # Save the 2D image

    # Save 3D image
    # Special case for Jetpack Cat
    if hero.name == "Jetpack Cat":                                                      # ? I have zero fucking clue why the jetpack joyride ahh is different, but it is :shrug:
        images[2].save(SAVE_DIRECTORY_3D / f"{hero.name}.png")                 
        continue

    images[IMAGE_3D_INDEX].save(SAVE_DIRECTORY_3D / f"{hero.name}.png")                 # Save the 3D image
