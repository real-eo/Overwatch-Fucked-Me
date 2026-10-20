# Global imports
from dataclasses import dataclass

# Same level imports
try:                from common                 import ROLE, ROLE_COUNT, TOTAL_SLOTS_ALL
except ImportError: from src.constants.common   import ROLE, ROLE_COUNT, TOTAL_SLOTS_ALL



@dataclass(frozen=True)
class LAYOUT:
    # * Constants
    # Macros
    X: int = 0
    Y: int = 1

    # Padding
    SMALL_PADDING: int = 2
    ROLE_FRAME_SEPERATOR_PADDING: int = 5
    SELECTED_HERO_COUNTERS_PADDING: int = 5
    WINDOW_PADDING: int = 10
    
    # Sizes
    HERO_BUTTON_SIZE: int = 75
    INPUT_FRAME_HEIGHT: int = 35
    ROLE_ICON_FRAME_HEIGHT: int = 35

    # Selected hero & counters layout
    SELECTED_HERO_HEIGHT: int = 83
    COUNTER_CELL_HEIGHT: int = 42                                                   # ? Actual HERO_6x6 image height                                        
    COUNTERS_AREA_HEIGHT: int = COUNTER_CELL_HEIGHT * ROLE_COUNT

    MAX_COUNTERS_PER_ROLE: int = 7                                                  # TODO: Update this so we can support more counters, and
                                                                                    #     : implement a solution which allows for infinite 
                                                                                    #     : counters to show while retaining the quick and clean
                                                                                    #     : overview the current implementation has

    # Switch- & icon layout constexprs 
    INPUT_FRAME_HEIGHT: int = 35
    ROLE_ICON_FRAME_HEIGHT: int = 35
    
    ROLE_ICON_X_OFFSET: int = -5
    ROLE_ICON_Y_OFFSET: int = -7
    
    # Hero grid
    NON_HERO_BUTTON_WIDTH: int = sum((
        WINDOW_PADDING,
        ROLE_FRAME_SEPERATOR_PADDING,
        ROLE_FRAME_SEPERATOR_PADDING,
        ROLE_FRAME_SEPERATOR_PADDING,                                                
    ))

    NON_HERO_BUTTON_HEIGHT: int = sum((
        SELECTED_HERO_HEIGHT, 
        COUNTERS_AREA_HEIGHT, 
        INPUT_FRAME_HEIGHT,
        SMALL_PADDING, 
        ROLE_ICON_FRAME_HEIGHT,
    ))

    class Default:
        # TODO: Implement storing of the window size between sessions so 
        #     : the program doesn't just start with the default window size.
        #     : These default values still have to be here regardless for the
        #     : first time the program is run, I just put this comment here
        #     : as i didn't find another place where it seemed fit.
        WINDOW_WIDTH: int = 930
        WINDOW_HEIGHT: int = 660

        ASPECT_RATIO: float = 11/5                                                      # ? Tie-breaker for window size snapping


class STYLE:
    # * Defaults
    BACKGROUND: str = "#3C3C3C"
    
    class Label:
        class SelectedHero:
            BACKGROUND: str = "#4C4C4C"
        
        class Counter:
            BACKGROUND: str = "#444444"
    
    class ControlButton:
        # * Defaults
        COLOR: str = "SystemButtonFace"                                                 # SystemButtonFace: "#F0F0F0"
        
        class Active:
            COLOR: str = "Green"
    
    class HeroButton:
        # * Defaults
        COLOR: str = "#FFFFFF"                                                           
        WIDTH: int = 68
        HEIGHT: int = 68
        BORDERWIDTH: int = 0

        class Selected:    
            COLOR: str = "#0078D7"

        class Hovered:
            WIDTH: int = 72    
            HEIGHT: int = 72
        
        class Disabled:
            PORTRAIT_OPACITY: int =  65                                                 # ? Represented in %. 100->0, 100 being fully opaque
            GRAYSCALE_AMOUNT: int =  75                                                 # ? Represented in %. 100->0, 100 being pure grayscale
