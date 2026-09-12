# Global imports
from pathlib import Path
import requests
import json
import sys

# Super level imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path: sys.path.insert(0, str(PROJECT_ROOT))

from src import parse
from src.constants import scrape, ALL_HERO_IDS
from src.constants.counterpickgg import HEADERS, PARAMS, COUNTERS_CHUNK, SPECIAL_CASE_COUNTERS_CHUNK, PROPS_INDEX, counterpickggID, SPECIAL_CASE_REPLACE_PARAMETERS, URL as COUNTERS_WEBSITE


# Counters specific constants
DISCARD_KEYS = {"locale", "translations"}


def counters(heroID: str, saveDirectory: Path = None):
    # Make the GET request to the hero counters page with the appropriate headers and params
    response = requests.get(
        f"{COUNTERS_WEBSITE}/{counterpickggID(heroID)}",                                # ? We have to use counterpickggID due to quirks in how counterpickgg formats heroIDs 
        params=PARAMS, 
        headers=HEADERS
    )        
    
    # Replace all instances of counterpickgg's inconsistencies with the standardized variants
    standardizedResponse = response.text
    for args in SPECIAL_CASE_REPLACE_PARAMETERS:
        standardizedResponse = standardizedResponse.replace(*args)

    # Extract the rsc records using the custom parser
    records = parse.rsc(standardizedResponse)

    # Get the props object containing the counters data
    # ? Try to load the default chunk for counters
    countersChunk = json.loads(records[COUNTERS_CHUNK])                                 # ["$","$L22",null,{...props...}]
    props: dict = countersChunk[PROPS_INDEX]                                            # The 4th element in array is the actual props object containing the counters data

    # | This implemenation is a hotfix
    # Check if the current hero is a special chunk case
    if "abilities" in props:
        # If so, load the counters via the special chunk code
        countersChunk = json.loads(records[SPECIAL_CASE_COUNTERS_CHUNK])       
        props: dict = countersChunk[PROPS_INDEX]                                        # The 4th element in array is the actual props object containing the counters data

    # Remove unnecessary keys from props to reduce memory usage
    for key in DISCARD_KEYS:
        props.pop(key, None)

    # Skip saving if directory isn't provided (used for testing purposes)
    if not saveDirectory:
        # // print("Hero:", props["heroName"])
        # // countersFor = props["countersFor"]
        # // countersAgainst = props["countersAgainst"]
        # //
        # // print("countersFor:", len(countersFor))
        # // print("first:", countersFor[0]["hero"]["name"], countersFor[0]["rating"])

        print(f"No save directory provided, skipping saving counters for {heroID}.")
        return

    # Create output directory if it doesn't exist
    if not saveDirectory.exists(): 
        saveDirectory.mkdir(parents=True)
    
    # Save the counters data to a JSON file
    savePath = saveDirectory / f"{heroID}.json"
    with open(savePath, "w", encoding="utf-8") as f:
        json.dump(props, f, indent=4)



if __name__ == "__main__":
    # Scrape counters for all heroes and save them to "out/scraped/" directory
    for heroID in ALL_HERO_IDS:
        print(f"Scraping counters for {heroID}...")
        counters(heroID, saveDirectory=scrape.OUTPUT_DIRECTORY)
