# Global imports
from pathlib import Path
import requests
import json
import sys

# Same level imports
try:                from counterpickgg                import HEADERS, PARAMS, COUNTERS_CHUNK, PROPS_INDEX, URL as COUNTERS_WEBSITE
except ImportError: from src.scrape.counterpickgg     import HEADERS, PARAMS, COUNTERS_CHUNK, PROPS_INDEX, URL as COUNTERS_WEBSITE

# Super level imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path: sys.path.insert(0, str(PROJECT_ROOT))

from src.constants import ALL_HERO_IDS
from src import parse


# Counters specific constants
DISCARD_KEYS = {"locale", "translations"}


def counters(heroID: str, saveDirectory: Path = None):
    # Make the GET request to the hero counters page with the appropriate headers and params
    response = requests.get(f"{COUNTERS_WEBSITE}/{heroID}", params=PARAMS, headers=HEADERS)

    # Extract the rsc records using the custom parser
    records = parse.rsc(response.text)

    # Get the props object containing the counters data
    chunk1c = json.loads(records[COUNTERS_CHUNK])                                       # ["$","$L22",null,{...props...}]
    props: dict = chunk1c[PROPS_INDEX]                                                  # The 4th element in array is the actual props object containing the counters data

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
    with open(savePath, "w") as f:
        json.dump(props, f, indent=4)



if __name__ == "__main__":
    # Execution constants
    OUTPUT_DIRECTORY = Path("out/scraped/").resolve()

    # Scrape counters for all heroes and save them to "out/scraped/" directory
    for heroID in ALL_HERO_IDS:
        print(f"Scraping counters for {heroID}...")
        counters(heroID, saveDirectory=OUTPUT_DIRECTORY)