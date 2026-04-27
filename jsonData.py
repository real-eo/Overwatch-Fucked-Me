from resourceManager import prefer_local_resource, PATH
from json import loads


def load():
    global counters                                                                     # Cache the counters in a global variable, so it can be accessed without reloading the file every time

    # Read counters from Json file
    with open(prefer_local_resource("counters.json")[PATH], "r") as jsonFile:
        jsonData = jsonFile.read()

    # Parse Json
    counters = loads(jsonData)                                                          # json.loads()


if __name__ == "__main__":
    print("[!] This file is not ment to be run!\n\n")
    input("Press \"Enter\" to exit . . .")
else:  
    load()                                                                              # ! IMPORTANT: Load the counters when the module is imported so the cache variable `counters` isn't undefined