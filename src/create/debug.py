# Global imports
from pathlib import Path
import json
import sys
import os

# Same level imports
# // try:                from _              import Path, shortcut
# // except ImportError: from src.create._   import Path, shortcut

# Super level imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path: sys.path.insert(0, str(PROJECT_ROOT))

from src.constants import HERO_ROLES, ROLE_DPS, ROLE_SUPPORT, ROLE_TANK
import jsonData
import json


# (heroID, role, amount)
matrix = []

# Display the amount of counters for each hero based on roles
for heroID, heroCounters in jsonData.counters.items():
    counterRolesCounter = {ROLE_TANK: 0, ROLE_DPS: 0, ROLE_SUPPORT: 0}

    for counterID, data in heroCounters.items():
        counterRole = HERO_ROLES[counterID]
        counterRolesCounter[counterRole] += 1

    print(f"{heroID}:", end=" ")
    print(json.dumps(counterRolesCounter, indent=4))

    for role, count in counterRolesCounter.items():
        matrix.append([heroID, role, count])

# Sort the matrix by heroID and then by role (tank, dps, support)
matrix.sort(key=lambda row: row[2], reverse=True)

# Display the matrix in a readable format
print("\nMatrix (heroID, role, amount): [")
for row in matrix:
    print("    " + str(row))
print("]")