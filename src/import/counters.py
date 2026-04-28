output = "{{"

with open("src/importCounters/importCounters.txt", "r") as countersFile:
    counters = countersFile.read()

characters = {"Ana": 2, "Ashe": 1, "Baptiste": 2, "Bastion": 1, "Brigitte": 2, "Cassidy": 1, "D.Va": 0, "Doomfist": 0, "Echo": 1, "Genji": 1, "Hanzo": 1, "Kiriko": 0, "Junker Queen": 0, "Junkrat": 1, "Lucio": 2, "Mei": 1, "Mercy": 2, "Moira": 2, "Orisa": 0, "Pharah": 1, "Ramattra": 0, "Reaper": 1, "Reinhardt": 0, "Roadhog": 0, "Sigma": 0, "Sojourn": 1, "Soldier: 76": 1, "Sombra": 1, "Symmetra": 1, "Torbjorn": 1, "Tracer": 1, "Widowmaker": 1, "Winston": 0, "Wrecking Ball": 0, "Zarya": 0, "Zenyatta": 2}

for y, o in enumerate(counters.split("-")[1:]):
    output += "\n\t\"{0}\": {1}".format(o.split('\n')[0], "{")

    data = [[], [], []]

    for i in o[:-1].split("\n")[1:]:
        data[characters[i]].append(i)
    
    classList = ["Tank", "DPS", "Support"]

    for i in range(3):
        output += "\n\t\t\"{0}\": {1}".format(classList[i], "{")

        tempData = output

        for x, i in enumerate(data[i]):
            output += f"\n\t\t\t\"{x}\": \"{i}\","
        
        if tempData == output:
            output += "\n\t\t\t,"
        
        output = output[:-1] + "\n\t\t},"

    # Character end line
    output = output[:-1] + "\n\t},"


# print(output[1:-1])
with open("counters.json", "w") as jsonFile:
    jsonFile.truncate(0)
    jsonFile.write(output[1:-1] + "\n}")
