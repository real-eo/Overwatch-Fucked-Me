# Global imports
from dataclasses import dataclass
from typing import ClassVar

# Same level imports
try:                from common                 import ROLE_TANK, ROLE_DPS, ROLE_SUPPORT
except ImportError: from src.constants.common   import ROLE_TANK, ROLE_DPS, ROLE_SUPPORT 



@dataclass(frozen=True)
class LAYOUT:
    # * Constants
    # Macros
    X: int = 0
    Y: int = 1

    # Padding
    SMALL_PADDING: int = 2
    ROLE_FRAME_SEPERATOR_PADDING: int = 5
    WINDOW_PADDING: int = 10
    
    # Sizes
    HERO_BUTTON_SIZE: int = 75
    INPUT_FRAME_HEIGHT: int = 35
    ROLE_ICON_FRAME_HEIGHT: int = 35

    # Hero grid
    DEFAULT_RATIO: ClassVar[dict[str, float]] = {                                       # ? Tie-breaker for window size snapping
        "landscape": 11 / 5, 
        "portrait": 5 / 11
    }     

    # GRID: dict[str, dict[int, int]] = {                                             # Number of buttons in each row
    #     # Tank
    #     ROLE_TANK: {                                                               
    #         0: 3,                                                                       
    #         1: 3,
    #         2: 3,
    #         3: 3,
    #         4: 3
    #     },
    # 
    #     # DPS
    #     ROLE_DPS: {                                                                  
    #         0: 5,                                                                       
    #         1: 5,
    #         2: 5,
    #         3: 5,
    #         4: 3
    #     },
    # 
    #     # Support
    #     ROLE_SUPPORT: {
    #         0: 4,                                                                       
    #         1: 4,
    #         2: 4,
    #         3: 4,
    #     }
    # }

    # Selected hero & counters layout
    SELECTED_HERO_HEIGHT: int = 83                                           
    COUNTERS_AREA_HEIGHT: int = 125

    MAX_COUNTERS_PER_ROLE: int = 7                                                  # TODO: Update this so we can support more counters, and
                                                                                    #     : implement a solution which allows for infinite 
                                                                                    #     : counters to show while retaining the quick and clean
                                                                                    #     : overview the current implementation has

    # Switch- & icon layout constexprs 
    INPUT_FRAME_HEIGHT: int = 35
    ROLE_ICON_FRAME_HEIGHT: int = 35
    
    # * Constexprs
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

    # ! HANDLED BY src.layout.Layout() class
    # // Role button rows
    # TANK_BUTTON_ROWS: int = len(GRID[ROLE_TANK])
    # DPS_BUTTON_ROWS: int = len(GRID[ROLE_DPS])
    # SUPPORT_BUTTON_ROWS: int = len(GRID[ROLE_SUPPORT])

    # Role button columns
    # TANK_BUTTON_COLUMNS: int = max(GRID[ROLE_TANK].values())
    # DPS_BUTTON_COLUMNS: int = max(GRID[ROLE_DPS].values())
    # SUPPORT_BUTTON_COLUMNS: int = max(GRID[ROLE_SUPPORT].values())

    # ! HANDLED BY src.layout.Layout() class
    # // Max button rows
    # HERO_BUTTON_ROWS: int = max((
    #     TANK_BUTTON_ROWS,
    #     DPS_BUTTON_ROWS,
    #     SUPPORT_BUTTON_ROWS
    # ))

    # ! HANDLED BY src.layout.Layout() class
    # // Frame dimensions
    # TANK_FRAME_WIDTH: int = TANK_BUTTON_COLUMNS * HERO_BUTTON_SIZE                      # ? Amount of columns * size of one button
    # DPS_FRAME_WIDTH: int = DPS_BUTTON_COLUMNS * HERO_BUTTON_SIZE                        # ? Amount of columns * size of one button
    # SUPPORT_FRAME_WIDTH: int = SUPPORT_BUTTON_COLUMNS * HERO_BUTTON_SIZE                # ? Amount of columns * size of one button
    # 
    # ROLE_FRAMES_HEIGHT: int = HERO_BUTTON_ROWS * HERO_BUTTON_SIZE                       # ? Amount of rows * size of one button

    # ! HANDLED BY src.layout.Layout() class
    # * Globals
    # WINDOW_WIDTH: int = sum((
    #     WINDOW_PADDING,
    #     TANK_FRAME_WIDTH,
    #     ROLE_FRAME_SEPERATOR_PADDING,
    #     DPS_FRAME_WIDTH,
    #     ROLE_FRAME_SEPERATOR_PADDING,
    #     SUPPORT_FRAME_WIDTH,
    #     ROLE_FRAME_SEPERATOR_PADDING,                                               # ? I have ZERO clue why it is uneven like this, all I know is that it 
    # ))                                                                              # ? is supposed to be like this, as symmetrical looks terrible. My guess
                                                                                    # ? is that it is due to the button-expansion asymmetry in the role frames
    # WINDOW_HEIGHT: int = sum((
    #     SELECTED_HERO_HEIGHT, 
    #     COUNTERS_AREA_HEIGHT, 
    #     INPUT_FRAME_HEIGHT,
    #     SMALL_PADDING, 
    #     ROLE_ICON_FRAME_HEIGHT,
    #     ROLE_FRAMES_HEIGHT
    # ))    

    # VIEWPORT_WIDTH: int = WINDOW_WIDTH - (2 * WINDOW_PADDING)
    # VIEWPORT_HEIGHT: int = WINDOW_HEIGHT - (2 * WINDOW_PADDING)

    # ! HANDLED BY src.layout.Layout() class
    # * Positions
    # Role frame positions
    # TANK_FRAME_X: int = 0 + WINDOW_PADDING                                                      # 0                     + window_padding
    # DPS_FRAME_X: int = (TANK_FRAME_X + TANK_FRAME_WIDTH) + ROLE_FRAME_SEPERATOR_PADDING         # 255 +   role_padding  + window_padding
    # SUPPORT_FRAME_X: int = (DPS_FRAME_X + DPS_FRAME_WIDTH) + ROLE_FRAME_SEPERATOR_PADDING       # 600 + 2*role_padding  + window_padding
    
    # ROLE_FRAMES_Y: int = WINDOW_HEIGHT - ROLE_FRAMES_HEIGHT

    # Switch- & icon positions
    # ROLE_ICON_Y: int = ROLE_FRAMES_Y - ROLE_ICON_FRAME_HEIGHT
    # INPUT_FRAME_Y: int = ROLE_ICON_Y - SMALL_PADDING - INPUT_FRAME_HEIGHT                       # ? Bottom-based layout (anchored to bottom)
    # // INPUT_FRAME_Y: int = SELECTED_HERO_HEIGHT + COUNTERS_AREA_HEIGHT                       # ? Top-based layout (anchored to top)

    class Default:
        # TODO: Implement storing of the window size between sessions so 
        #     : the program doesn't just start with the default window size.
        #     : These default values still have to be here regardless for the
        #     : first time the program is run, I just put this comment here
        #     : as i didn't find another place where it seemed fit.
        WINDOW_WIDTH: int = 930
        WINDOW_HEIGHT: int = 660


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
