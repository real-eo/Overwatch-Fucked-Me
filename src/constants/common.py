try:                from parse.translate        import heroID
except ImportError: from src.parse.translate    import heroID

from pathlib import Path as _Path
from enum import IntEnum
import sys


# Application
IS_EXE = getattr(sys, "frozen", False)
BUNDLED_ASSETS = IS_EXE and hasattr(sys, "_MEIPASS")
DEBUG = not IS_EXE 


# Files
COUNTERS_FILE = "counters.json"


# Heroes
class ROLE(IntEnum):
    TANK = 0
    DPS = 1
    SUPPORT = 2
    ALL = 3


MAX_SLOTS_TANK = 1                                          # TODO: This implementation has to be reworked once we implement 6v6
MAX_SLOTS_DPS = 2                                           # TODO: This implementation has to be reworked once we implement 6v6
MAX_SLOTS_SUPPORT = 2                                       # TODO: This implementation has to be reworked once we implement 6v6
TOTAL_SLOTS_ALL = 5                                         # TODO: This implementation has to be reworked once we implement 6v6

HERO_ROLES = (ROLE.TANK, ROLE.DPS, ROLE.SUPPORT)
ROLE_COUNT = len(HERO_ROLES)

[DeprecationWarning("`__HEROES` is deprecated, refrain from using! `HERO_IDS` is the new alternative!")]
__HEROES = {
    ROLE.TANK: ['D.Mon', 'D.Va', 'Domina', 'Doomfist', 'Hazard', 'Junker Queen', 'Mauga', 'Orisa', 'Ramattra', 'Reinhardt', 'Roadhog', 'Sigma', 'Winston', 'Wrecking Ball', 'Zarya'],
    ROLE.DPS: ['Anran', 'Ashe', 'Bastion', 'Cassidy', 'Echo', 'Emre', 'Freja', 'Genji', 'Hanzo', 'Junkrat', 'Mei', 'Pharah', 'Reaper', 'Shion', 'Sierra', 'Sojourn', 'Soldier_ 76', 'Symmetra', 'Torbjörn', 'Tracer', 'Vendetta', 'Venture', 'Widowmaker'],
    ROLE.SUPPORT: ['Ana', 'Baptiste', 'Brigitte', 'Doctrine', 'Illari', 'Jetpack Cat', 'Juno', 'Kiriko', 'Lifeweaver', 'Lúcio', 'Mercy', 'Mizuki', 'Moira', 'Sombra', 'Wuyang', 'Zenyatta']
}

HERO_IDS = {
    ROLE.TANK: [heroID(char) for char in __HEROES[ROLE.TANK]],
    ROLE.DPS: [heroID(char) for char in __HEROES[ROLE.DPS]],
    ROLE.SUPPORT: [heroID(char) for char in __HEROES[ROLE.SUPPORT]]
}


ALL_HEROES = __HEROES[ROLE.TANK] + __HEROES[ROLE.DPS] + __HEROES[ROLE.SUPPORT]
ALL_HERO_IDS = HERO_IDS[ROLE.TANK] + HERO_IDS[ROLE.DPS] + HERO_IDS[ROLE.SUPPORT]

# ? This will eventually be how we store the heroes, and replace either "HEROES" or "HERO_IDS". But for now, we just assing a new constant
HERO_ROLE_MAP = {
    hero: role 
    for role, heroList in HERO_IDS.items()                                              # Loop through each role
    for hero in heroList                                                                # Loop through each list of heroes for that role
} 

HERO_COUNTS = {                                                                         # Amount of heroes per role
    ROLE.TANK: len(HERO_IDS[ROLE.TANK]),
    ROLE.DPS: len(HERO_IDS[ROLE.DPS]),
    ROLE.SUPPORT: len(HERO_IDS[ROLE.SUPPORT])
}
