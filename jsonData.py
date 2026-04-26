from resourceManager import resource_path
from json import loads


if __name__ == "__main__":
    print("[!] This file is not ment to be run!\n\n")
    input("Press \"Enter\" to exit . . .")
else:
    # Read counters from Json file
    with open(resource_path("counters.json"), "r") as jsonFile:
        jsonData = jsonFile.read()

    # Parse Json
    counters = loads(jsonData)                                                          # json.loads()