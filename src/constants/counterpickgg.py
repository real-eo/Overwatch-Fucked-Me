URL = "https://counterpickgg.com/heroes"
HEADERS = {'rsc': '1'}
PARAMS = {'_rsc': '1jsli'}

# The different chunks in the response (only counters chunk is relevant)
ABILITIES_CHUNK = "1a"                                                                  # This contains the abilities data in a JSON string format 
COUNTERS_CHUNK = "1b"                                                                   # This contains the counters data in a JSON string format
WINRATE_BY_RANK_CHUNK = "1d"                                                            # This contains the winrate by rank data in a JSON string format
WINRATE_BY_MAP_CHUNK = "1e"                                                             # This contains the winrate by map data in a JSON string format
KNOWN_PROFESSIONAL_PLAYERS_CHUNK = "1f"                                                 # This contains known professional players on a certain hero in a JSON string format

# ! SOME TANKS HAVE THEIR COUNTER DATA STORED IN A DIFFERENT CHUNK!
SPECIAL_CASE_ABILITIES_CHUNK = "1b"                                                     # ? This contains the abilities data in a JSON string format. But for some reason, tanks have their data stored in different chunks compared to the other heroes 
SPECIAL_CASE_COUNTERS_CHUNK = "1c"                                                      # ? This contains the counters data in a JSON string format. But for some reason, tanks have their data stored in different chunks compared to the other heroes

PROPS_INDEX = 3                                                                         # The index in the array where the actual props object is located (0-based index)


# Special cases
OLD = 0                                                                                 # ? I just defined these to avoid mixing which number is the 
NEW = 1                                                                                 # ? actual index used in `HERO_ID_COMPATIBILITY_CONVERSIONS`

SPECIAL_CASE_REPLACE_PARAMETERS = (                                                     # ! NOTE: THERE CAN'T BE ANY " OR ' IN EITHER
    # ? https://counterpickgg.com uses "freya" instead of "freja" :shrug:
    ("freya", "freja"),
    ("Freya", "Freja"),
)

HERO_ID_COMPATIBILITY_CONVERSIONS = {                                                   # ! ONLY USED FOR `counterpickggID` FUNCTION 
    SPECIAL_CASE_REPLACE_PARAMETERS[0][NEW]: SPECIAL_CASE_REPLACE_PARAMETERS[0][OLD],   # freja -> freya
}


def counterpickggID(name: str) -> str:
    from src.parse.translate import heroID

    # First parse the name through heroID to ensure consistent formatting
    id = heroID(name)

    # Then apply any special cases specific to counterpickgg
    id = HERO_ID_COMPATIBILITY_CONVERSIONS[id] if id in HERO_ID_COMPATIBILITY_CONVERSIONS else id

    return id