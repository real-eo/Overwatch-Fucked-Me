try:                from parse.translate        import heroID
except ImportError: from src.parse.translate    import heroID


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

HEROES = {
    ROLE_TANK: ['D.Va', 'Domina', 'Doomfist', 'Hazard', 'Junker Queen', 'Mauga', 'Orisa', 'Ramattra', 'Reinhardt', 'Roadhog', 'Sigma', 'Winston', 'Wrecking Ball', 'Zarya'],
    ROLE_DPS: ['Anran', 'Ashe', 'Bastion', 'Cassidy', 'Echo', 'Emre', 'Freja', 'Genji', 'Hanzo', 'Junkrat', 'Mei', 'Pharah', 'Reaper', 'Sierra', 'Sojourn', 'Soldier_ 76', 'Sombra', 'Symmetra', 'Torbjörn', 'Tracer', 'Vendetta', 'Venture', 'Widowmaker'],
    ROLE_SUPPORT: ['Ana', 'Baptiste', 'Brigitte', 'Illari', 'Jetpack Cat', 'Juno', 'Kiriko', 'Lifeweaver', 'Lúcio', 'Mercy', 'Mizuki', 'Moira', 'Wuyang', 'Zenyatta']
}

HERO_IDS = {
    ROLE_TANK: [heroID(char) for char in HEROES[ROLE_TANK]],
    ROLE_DPS: [heroID(char) for char in HEROES[ROLE_DPS]],
    ROLE_SUPPORT: [heroID(char) for char in HEROES[ROLE_SUPPORT]]
}


ALL_HEROES = HEROES[ROLE_TANK] + HEROES[ROLE_DPS] + HEROES[ROLE_SUPPORT]
ALL_HERO_IDS = HERO_IDS[ROLE_TANK] + HERO_IDS[ROLE_DPS] + HERO_IDS[ROLE_SUPPORT]


# ? This might eventually be how we store the heroes, and might replace "HEROES". But for now, we just assing a new constant
HERO_ROLES = {
    hero: role 
    for role, heroList in HEROES.items()                                                # Loop through each role
    for hero in heroList                                                                # Loop through each list of heroes for that role
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
