import json


if __name__ == "__main__":
    print("[!] This file is not ment to be run!\n\n")
    input("Press \"Enter\" to exit . . .")
else:
    # Read counters from Json file
    with open("counters.json", "r") as jsonFile:
        jsonData = jsonFile.read()

    # Parse Json
    counters = json.loads(jsonData)