import sys


# Application
IS_EXE = getattr(sys, "frozen", False)
BUNDLED_ASSETS = IS_EXE and hasattr(sys, "_MEIPASS")
DEBUG = not IS_EXE 

# Heroes
ROLE_ALL = "all"
ROLE_TANK = "tank"
ROLE_DPS = "dps"
ROLE_SUPPORT = "support"

CHARACTERS = {
    ROLE_TANK: ['D.Va', 'Domina', 'Doomfist', 'Hazard', 'Junker Queen', 'Mauga', 'Orisa', 'Ramattra', 'Reinhardt', 'Roadhog', 'Sigma', 'Winston', 'Wrecking Ball', 'Zarya'],
    ROLE_DPS: ['Anran', 'Ashe', 'Bastion', 'Cassidy', 'Echo', 'Emre', 'Freja', 'Genji', 'Hanzo', 'Junkrat', 'Mei', 'Pharah', 'Reaper', 'Sierra', 'Sojourn', 'Soldier_ 76', 'Sombra', 'Symmetra', 'Torbjörn', 'Tracer', 'Vendetta', 'Venture', 'Widowmaker'],
    ROLE_SUPPORT: ['Ana', 'Baptiste', 'Brigitte', 'Illari', 'Jetpack Cat', 'Juno', 'Kiriko', 'Lifeweaver', 'Lúcio', 'Mercy', 'Mizuki', 'Moira', 'Wuyang', 'Zenyatta']
}




# // m = set("""
# // Kiriko
# // 
# // Lifeweaver
# // 
# // Mercy
# // 
# // Moira
# // 
# // Brigitte
# // 
# // Illari
# // 
# // Juno
# // 
# // Mizuki
# // 
# // Wuyang
# // 
# // Ana
# // 
# // Baptiste
# // 
# // Jetpack Cat
# // 
# // Lúcio
# // 
# // Zenyatta
# // """.replace("\t", "").replace(":", "_").splitlines())
# // 
# // m.remove("")
# // m = sorted(m)
# // 
# // 
# // print(m)
