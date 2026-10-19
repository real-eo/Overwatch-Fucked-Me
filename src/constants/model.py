# Global imports
from keras.models import load_model
from pathlib import Path
from keras import Model
import numpy
import sys

numpy.set_printoptions(suppress=True)

# Same level imports
try:                from common                 import ROLE_TANK, ROLE_DPS, ROLE_SUPPORT, ALL_HERO_IDS
except ImportError: from src.constants.common   import ROLE_TANK, ROLE_DPS, ROLE_SUPPORT, ALL_HERO_IDS

try:                from parse.translate        import heroID
except ImportError: from src.parse.translate    import heroID

# Super level imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path: sys.path.insert(0, str(PROJECT_ROOT))

from src.resources.manager import resource_path


# * Model
MODEL: Model = load_model(resource_path("model", "keras_model.h5"), compile=False)


# * Model labels
MODEL_IDS = tuple(map(                                                                  # ? Used for actual logic                                                        
    lambda label: heroID(label.split(maxsplit=1)[1]),                                   
    open(resource_path("model", "labels.txt"), 'r', encoding="utf-8").readlines()
))

SPECIAL_CLASSES: set = set(                                                             # ? Whitelist used when categorizing roles
    classId
    for classId in MODEL_IDS
    if classId not in ALL_HERO_IDS
)

MODEL_LABELS = tuple(                                                                   # ? Used for output
    f"{index} {name}"
    for index, name in enumerate(MODEL_IDS)
)


# * Enemy leaderboard order
ASSUME_REGULAR_ENEMY_ORDER = True
EXPECTED_ROLE_ORDER = (
    ROLE_TANK,
    ROLE_DPS,
    ROLE_DPS,
    ROLE_SUPPORT,
    ROLE_SUPPORT,
)

