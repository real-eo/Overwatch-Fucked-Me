# Common constants for the entire project
try:                from common                 import *
except ImportError: from src.constants.common   import *

# extracter specific constants

# Scraper specific constants
try:                                    import counterpickgg
except ImportError: from src.constants  import counterpickgg

