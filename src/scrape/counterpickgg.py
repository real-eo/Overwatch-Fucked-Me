# Request constants
URL = "https://counterpickgg.com/heroes"
HEADERS = {'rsc': '1'}
PARAMS = {'_rsc': '1jsli'}

# The different chunks in the response (only counters chunk is relevant)
ABILITIES_CHUNK = "1b"                                                                  # This contains the abilities data in a JSON string format 
COUNTERS_CHUNK = "1c"                                                                   # This contains the counters data in a JSON string format
WINRATE_BY_RANK_CHUNK = "1d"                                                            # This contains the winrate by rank data in a JSON string format
WINRATE_BY_MAP_CHUNK = "1e"                                                             # This contains the winrate by map data in a JSON string format
KNOWN_PROFESSIONAL_PLAYERS_CHUNK = "1f"                                                 # This contains known professional players on a certain hero in a JSON string format

PROPS_INDEX = 3                                                                         # The index in the array where the actual props object is located (0-based index)
