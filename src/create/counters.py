# Global imports
from pathlib import Path
import json
import sys
import os

# Same level imports
# // try:                from _              import Path, shortcut
# // except ImportError: from src.create._   import Path, shortcut

# Super level imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path: sys.path.insert(0, str(PROJECT_ROOT))

from src.constants import scrape, ALL_HERO_IDS, COUNTERS_FILE
from src.constants.create import COUNTER_RATING_THRESHOLD


# This file is responsible for creating the counters.json file
counters = {}


"""
{
    "heroId": "mauga",
    "heroName": "Mauga",
    "countersFor": [
        {
            "counterHeroId": "sigma",
            "hero": {
                "id": "sigma",
                "name": "Sigma",
                "role": "tank",
                "icon": "\u00f0\u009f\u008c\u008c",
                "portrait": "https://d15f34w2p8l1cc.cloudfront.net/overwatch/cd7a4c0a0df8924afb2c9f6df864ed040f20250440c36ca2eb634acf6609c5e4.png"
            },
            "rating": 8,
            "description": "Sigma can interrupt Mauga's healing by using any of his abilities against Mauga:E."
        },
"""


def addCounters(id: str) -> None:
    global counters                                                                     # Global the counters so we can modify it inside the function

    # * Read the counter data
    counterDataJsonFilePath: Path = scrape.OUTPUT_DIRECTORY / f"{id}.json"              # ? Path to the actual json file which contains the counters

    # Ensure the counter data for the hero exists
    if not counterDataJsonFilePath.exists():
        print(f"[!] No counter data found for hero with id \"{id}\"")
        return
    
    # * Store the counter data
    # Create the entry for the hero in the counters dictionary if it doesn't exist
    if id not in counters:  
        counters[id] = {}

    # Read the scraped json file from `scrape.OUTPUT_DIRECTORY/{id}.json`
    with open(counterDataJsonFilePath, "r") as jsonFile:
        scrapedData: dict = json.load(jsonFile)
    
    # Add the specific data to the counters dictionary
    for counter in scrapedData.get("countersFor", []):
        # First ensure that the counter's efficiency is above or equal to the set threshold
        rating: int = counter.get("rating")
        if (rating is None or                                                           # ! Ensure this check comes first to avoid comparing None to an int
            rating < COUNTER_RATING_THRESHOLD): 
            continue
        
        # Extract the rest of the relevant data
        counterHeroID = counter.get("counterHeroId")
        description = counter.get("description")

        # Then add a new entry for the specific hero in the counters dictionary 
        counters[id][counterHeroID] = {
            "rating": rating,
            "description": description
        }


def saveCounters() -> None:
    with open(COUNTERS_FILE, "w") as jsonFile:
        json.dump(counters, jsonFile, indent=4)

    print(f"[+] Counters saved to {COUNTERS_FILE}")



if __name__ == "__main__":
    # Add counters for all heroes in ALL_HERO_IDS
    for id in ALL_HERO_IDS:
        addCounters(id)

    # Preview the generated counters dictionary
    print(json.dumps(counters, indent=4))
    print("\n\n")

    # Wait for user confirmation before continuing
    confirmation = input("Splicing and creating a new `counters.json` complete. Do you want to apply the changes to the app directory (THIS WILL DESTROY THE OLD `counters.json`!)? (Y/n): ")
    if not confirmation.lower() in ["y", "yes"]:
        exit() 

    # Save the counters to the `counters.json` file
    saveCounters()