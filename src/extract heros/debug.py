try:                from resolve                    import Path, shortcut
except ImportError: from src.extract_heros.resolve  import Path, shortcut


# Constants
OVERWATCH_DATATOOL_LNK = Path("Overwatch DataTool.lnk") 
RELATIVE_HERO_ICON_PATH = Path("out", "HeroIcons")
PLAYABLE_HERO_ENTRY_THRESHOLD = 6                                                       # The amount of files+directories that must exist for the playable heros. This is only used as a filter to exclude bots, NPCs, etc.

# Variables
overwatchDataToolPath = shortcut(OVERWATCH_DATATOOL_LNK)
heroIconDirectory = Path(overwatchDataToolPath) / RELATIVE_HERO_ICON_PATH


# Loop through all subdirectories, and print the amount of entires (files and directories) in each subdirectory
amountOfFiles = {} 
for entry in heroIconDirectory.iterdir():
    if entry.is_dir():
        amountOfFiles[entry.name] = len(list(entry.iterdir()))

# Filter out subdirectories that do not meet the playable hero entry threshold
amountOfFiles = {k: v for k, v in amountOfFiles.items() if v >= PLAYABLE_HERO_ENTRY_THRESHOLD}

# Sort the dictionary by the amount of files in each subdirectory, and print the result
amountOfFiles = dict(sorted(amountOfFiles.items(), key=lambda item: item[1], reverse=True))
for subdir, amount in amountOfFiles.items():
    print(f"{subdir}: {amount} files") 

print(len(amountOfFiles))