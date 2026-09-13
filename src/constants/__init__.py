# Common constants for the entire project
try:                from common                 import *
except ImportError: from src.constants.common   import *

# extracter specific constants

# Scraper specific constants
try:                                    import scrape, counterpickgg 
except ImportError: from src.constants  import scrape, counterpickgg

# Create specific constants
try:                                    import create
except ImportError: from src.constants  import create

