try:                from common                 import ROLE_TANK, ROLE_DPS, ROLE_SUPPORT
except ImportError: from src.constants.common   import ROLE_TANK, ROLE_DPS, ROLE_SUPPORT 


class Layout:
    # * Constants
    # Padding
    SMALL_PADDING: int = 2
    ROLE_FRAME_SEPERATOR_PADDING: int = 5
    WINDOW_PADDING: int = 10
    
    # Sizes
    CHARACTER_BUTTON_SIZE: int = 75

    # Character grid
    GRID: dict[str, dict[int, int]] = {                                             # Number of buttons in each row
        # Tank
        ROLE_TANK: {                                                               
            0: 3,                                                                       
            1: 3,
            2: 3,
            3: 3,
            4: 3
        },

        # DPS
        ROLE_DPS: {                                                                  
            0: 5,                                                                       
            1: 5,
            2: 5,
            3: 5,
            4: 3
        },

        # Support
        ROLE_SUPPORT: {
            0: 4,                                                                       
            1: 4,
            2: 4,
            3: 4,
        }
    }

    # * Selected hero & counters layout constexprs
    SELECTED_HERO_HEIGHT: int = 83                                           
    COUNTERS_AREA_HEIGHT: int = 125

    MAX_COUNTERS_PER_ROLE: int = 7                                                  # TODO: Update this so we can support more counters, and
                                                                                    #     : implement a solution which allows for infinite 
                                                                                    #     : counters to show while retaining the quick and clean
                                                                                    #     : overview the current implementation has

    # * Switch- & icon layout constexprs 
    INPUT_FRAME_HEIGHT: int = 35
    ROLE_ICON_FRAME_HEIGHT: int = 35
    
    # * Hero selection layout constexprs
    # Role button rows
    TANK_BUTTON_ROWS: int = len(GRID[ROLE_TANK])
    DPS_BUTTON_ROWS: int = len(GRID[ROLE_DPS])
    SUPPORT_BUTTON_ROWS: int = len(GRID[ROLE_SUPPORT])

    # Role button columns
    TANK_BUTTON_COLUMNS: int = max(GRID[ROLE_TANK].values())
    DPS_BUTTON_COLUMNS: int = max(GRID[ROLE_DPS].values())
    SUPPORT_BUTTON_COLUMNS: int = max(GRID[ROLE_SUPPORT].values())

    # Max button rows
    CHARACTER_BUTTON_ROWS: int = max((
        TANK_BUTTON_ROWS,
        DPS_BUTTON_ROWS,
        SUPPORT_BUTTON_ROWS
    ))

    # Frame dimensions
    TANK_FRAME_WIDTH: int = TANK_BUTTON_COLUMNS * CHARACTER_BUTTON_SIZE             # ? Amount of columns * size of one button
    DPS_FRAME_WIDTH: int = DPS_BUTTON_COLUMNS * CHARACTER_BUTTON_SIZE               # ? Amount of columns * size of one button
    SUPPORT_FRAME_WIDTH: int = SUPPORT_BUTTON_COLUMNS * CHARACTER_BUTTON_SIZE       # ? Amount of columns * size of one button

    ROLE_FRAMES_HEIGHT: int = CHARACTER_BUTTON_ROWS * CHARACTER_BUTTON_SIZE         # ? Amount of rows * size of one button

    # * Globals
    WINDOW_WIDTH: int = sum((
        WINDOW_PADDING,
        TANK_FRAME_WIDTH,
        ROLE_FRAME_SEPERATOR_PADDING,
        DPS_FRAME_WIDTH,
        ROLE_FRAME_SEPERATOR_PADDING,
        SUPPORT_FRAME_WIDTH,
        ROLE_FRAME_SEPERATOR_PADDING,                                               # ? I have ZERO clue why it is uneven like this, all I know is that it 
    ))                                                                              # ? is supposed to be like this, as symmetrical looks terrible. My guess
                                                                                    # ? is that it is due to the button-expansion asymmetry in the role frames
    WINDOW_HEIGHT: int = sum((
        SELECTED_HERO_HEIGHT, 
        COUNTERS_AREA_HEIGHT, 
        INPUT_FRAME_HEIGHT,
        SMALL_PADDING, 
        ROLE_ICON_FRAME_HEIGHT,
        ROLE_FRAMES_HEIGHT
    ))

    VIEWPORT_WIDTH: int = WINDOW_WIDTH - (2 * WINDOW_PADDING)
    VIEWPORT_HEIGHT: int = WINDOW_HEIGHT - (2 * WINDOW_PADDING)

    # * Positions
    # Role frame positions
    TANK_FRAME_X: int = 0 + WINDOW_PADDING                                                      # 0                     + window_padding
    DPS_FRAME_X: int = (TANK_FRAME_X + TANK_FRAME_WIDTH) + ROLE_FRAME_SEPERATOR_PADDING         # 255 +   role_padding  + window_padding
    SUPPORT_FRAME_X: int = (DPS_FRAME_X + DPS_FRAME_WIDTH) + ROLE_FRAME_SEPERATOR_PADDING       # 600 + 2*role_padding  + window_padding
    
    ROLE_FRAMES_Y: int = WINDOW_HEIGHT - ROLE_FRAMES_HEIGHT

    # Switch- & icon positions
    ROLE_ICON_Y: int = ROLE_FRAMES_Y - ROLE_ICON_FRAME_HEIGHT
    INPUT_FRAME_Y: int = ROLE_ICON_Y - SMALL_PADDING - INPUT_FRAME_HEIGHT                       # ? Bottom-based layout (anchored to bottom)
    # // INPUT_FRAME_Y: int = SELECTED_HERO_HEIGHT + COUNTERS_AREA_HEIGHT                       # ? Top-based layout (anchored to top)

class Style:
    # * Defaults
    BACKGROUND = "#3C3C3C"
    
    class Label:
        class SelectedHero:
            BACKGROUND = "#4C4C4C"

        class Counter:
            BACKGROUND = "#444444"


    class ControlButton:
        # * Defaults
        COLOR = "SystemButtonFace"                                                  # SystemButtonFace: "#F0F0F0"

        class Active:
            COLOR = "Green"

    class HeroButton:
        # * Defaults
        COLOR = "#FFFFFF"                                                           
        WIDTH = 68
        HEIGHT = 68
        BORDERWIDTH = 0

        class Selected:    
            COLOR = "#0078D7"

        class Hovered:
            WIDTH = 72    
            HEIGHT = 72

        class Disabled:
            PORTRAIT_OPACITY =  65                                                  # ? Represented in %. 100->0, 100 being fully opaque
            GRAYSCALE_AMOUNT =  75                                                  # ? Represented in %. 100->0, 100 being pure grayscale
