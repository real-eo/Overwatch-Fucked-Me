# Global imports
from dataclasses import dataclass
from math import ceil, log
from pathlib import Path
import typing
import sys

# Same level imports
try:                from constants.common       import ROLE, HERO_COUNTS, TOTAL_SLOTS_ALL
except ImportError: from src.constants.common   import ROLE, HERO_COUNTS, TOTAL_SLOTS_ALL

try:                from constants.ui           import LAYOUT
except ImportError: from src.constants.ui       import LAYOUT

# Super level imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path: sys.path.insert(0, str(PROJECT_ROOT))


# * Dataclasses & typedefs
@dataclass(frozen=True, slots=True)
class Resolution:
    """
    Represents a monitor's resolution.
    """
    width: int
    height: int


@dataclass(frozen=True, slots=True)
class WindowGeometry:
    """
    Represents the geometry of a window.

    Attributes:
        width (int): The width of the window.
        height (int): The height of the window.
    """

    width: int
    height: int

    def __str__(self) -> str: return f"{self.width}x{self.height}"


@dataclass(frozen=True)
class HeroLayout:
    """
    Represents the layout of heroes in the UI.
    """
    columns: int
    rows: int
    widths: tuple[int, int, int]
    heights: tuple[int, int, int]
    pixels: tuple[int, int]


@dataclass(frozen=True, slots=True)
class Rect:
    x: int
    y: int
    width: int
    height: int


RequiresResizing = bool


# * Layout calculation functions
def minColumnsForRows(rows: int, A: tuple[int, int, int] = HERO_COUNTS.values()):
    """Smallest layout in which every group is at most `rows` rows tall.

    A group with n icons and width `w` needs `ceil(n / w)` rows, so it fits
    in `rows` rows exactly when `w >= ceil(n / rows)`. Using that minimum width for
    each group gives the fewest columns that can reach height `rows`.

    Returns
    -------
    tuple[int, tuple[int, int, int], list[int]]
        (columns_needed, widths, heights). Heights are <= `rows`; a group can
        come out shorter than `rows` when its width is rounded up.
    """
    widths = tuple(ceil(n / rows) for n in A)
    heights = [ceil(n / w) for n, w in zip(A, widths)]
    return sum(widths), widths, heights


def _allLayouts(A: tuple[int, int, int]):
    """Every exact-fit layout for icon counts `A`, in both orientations.

    landscape: groups side by side; one layout per row count `rows`, from
               `minColumnsForRows(rows)`. Its box is (sum of widths, tallest group).
    portrait:  groups stacked, each as wide as the window; one layout per
               width `C`, with `rows = sum(ceil(n / C))`.

    A layout is dropped if another layout of the same mode is no wider
    and no taller (it can never be the better choice).
    """                                                                                 # ! <-- NEEDS REWRITE 
    found = {}

    for rows in range(1, max(A) + 1):
        columns, widths, heights = minColumnsForRows(rows, A)

        found.setdefault(
            (columns, max(heights)),
            {
                "columns": columns,
                "rows": max(heights),
                "widths": widths,
                "heights": tuple(heights),
            },
        )

    return list(found.values())

def calculateOptimalHeroLayout(
    availableWidth: int, 
    availableHeight: int, 
    screenWidth: int, 
    screenHeight: int, 
    A: tuple[int, int, int] = HERO_COUNTS.values()
) -> HeroLayout:
    """
    Pick the tightest-packing layout for a dragged window size.

    All pixel arguments are for the tiling area only (gaps/UI already
    subtracted; add them back when sizing the real window).

    Parameters
    ----------
    availableWidth, availableHeight : int   Tiling area the user dragged to, in px.
    screenWidth, screenHeight : int Largest tiling area the screen allows, in px.
    A : tuple[int, int, int] | None
        Icons per group (tank, damage, support). Defaults to HERO_COUNTS.

    Returns
    -------
    HeroLayout: mode ("landscape" or "portrait"), columns, rows, widths, heights, pixels (width, height of the exact-fit window).

    Rule
    ----
    1. Landscape first. Sort layouts by (tiles to grow, window area,
       closeness to 11:5) and take the best. Layouts that fit the dragged
       size cost no growth, so among those the smallest area (tightest
       packing) wins.
    2. If that overruns the screen, take the best portrait layout that
       fits the screen (same sort, ratio target 5:11).
    3. If no portrait layout fits either, keep the landscape one.
    """                                                                                 # ! <-- NEEDS REWRITE 
    requestedColumns = max(1, availableWidth // LAYOUT.HERO_BUTTON_SIZE)                # whole tiles the drag gives us
    requestedRows = max(1, availableHeight // LAYOUT.HERO_BUTTON_SIZE)
    layouts = _allLayouts(A)

    def key(layout):
        sizeError = (abs(layout["columns"] - requestedColumns) + abs(layout["rows"] - requestedRows))
        ratioError = abs((layout["columns"] / layout["rows"]) - LAYOUT.Default.ASPECT_RATIO)
        return sizeError, ratioError

    best = min(layouts, key=key)
    return HeroLayout(
        **best, 
        pixels=(best["columns"] * LAYOUT.HERO_BUTTON_SIZE, best["rows"] * LAYOUT.HERO_BUTTON_SIZE))


# * Layout class
class Layout:
    def __init__(self, screen: Resolution):
        self.__screen: Resolution = screen

        self.__geometry: WindowGeometry                                                 # ? Placeholder. Assigned: self.__updateGeometry()
        self.__heroLayout: HeroLayout                                                   # ? Placeholder. Assigned: self.recalculate()

        # External state
        self.__activeResizeJob: typing.Optional[str] = None                             # ? Store the ID of the scheduled recalculation job
        self.__isWindowResizing: bool = False                                           # ? Prevent recursive calls to self.recalculate() when resizing the window

        # Calculate layout
        # NOTE: Safe to call here as we only use it when initializing the application   # TODO: Implement storing of the window size between sessions so 
        self.recalculate(LAYOUT.Default.WINDOW_WIDTH, LAYOUT.Default.WINDOW_HEIGHT)     #     : the program doesn't just start with the default window size.

    # * State
    def __updateGeometry(self):
        """
        Calculate the window geometry
        """
        self.__geometry = WindowGeometry(
            width  = self.__heroLayout.pixels[LAYOUT.X] + LAYOUT.NON_HERO_BUTTON_WIDTH,
            height = self.__heroLayout.pixels[LAYOUT.Y] + LAYOUT.NON_HERO_BUTTON_HEIGHT
        )

    def __updateHeroLayout(self, windowWidth: int, windowHeight: int):
        """
        Calculate the hero layout
        """
        self.__heroLayout = calculateOptimalHeroLayout(
            availableWidth = windowWidth - LAYOUT.NON_HERO_BUTTON_WIDTH,
            availableHeight= windowHeight - LAYOUT.NON_HERO_BUTTON_HEIGHT,
            screenWidth = self.__screen.width,
            screenHeight= self.__screen.height
        )

    # * Calculation
    def recalculate(self, windowWidth: int, windowHeight: int):
        """
        Recalculate the layout based on new window size.

        Steps:
        1. Calculate the hero layout budget using the fixed sized UI elements, and finding the optimal hero layout   
        2. Calculate the non-const non-hero layout UI elements' sides based on the hero layout
        3. Recalculate and update the window geometry to reflect the new layout size

        NOTE: The caller is responsible for actually resizing the window and flexing the UI elements!

        Parameters
        ----------
        windowWidth : int
            The new width of the window in pixels.
        
        windowHeight : int
            The new height of the window in pixels.
        """

        # Calculate the hero layout budget using the fixed sized UI elements, and finding the optimal hero layout
        self.__updateHeroLayout(windowWidth, windowHeight)

        # Calculate the non-hero layout, non-const, UI elements based on the hero layout
        # TODO: Implement

        # Update the window geometry
        self.__updateGeometry()




    # * Getters
    # Actual attributes
    @property
    def screen(self) -> Resolution: return self.__screen
    @property
    def geometry(self) -> WindowGeometry: return self.__geometry
    @property
    def heroLayout(self) -> HeroLayout: return self.__heroLayout
    
    @property
    def activeResizeJob(self) -> typing.Optional[str]: return self.__activeResizeJob
    @property
    def isWindowResizing(self) -> bool: return self.__isWindowResizing

    # ? Derived attributes
    # Frame dimensions
    @property
    def tankFrameWidth(self) -> int: return self.__heroLayout.widths[ROLE.TANK] * LAYOUT.HERO_BUTTON_SIZE
    @property
    def dpsFrameWidth(self) -> int: return self.__heroLayout.widths[ROLE.DPS] * LAYOUT.HERO_BUTTON_SIZE
    # // @property
    # // def supportFrameWidth(self) -> int: return self.__heroLayout.widths[ROLE.SUPPORT] * LAYOUT.HERO_BUTTON_SIZE
    @property
    def roleFramesHeight(self) -> int: return self.__heroLayout.rows * LAYOUT.HERO_BUTTON_SIZE

    # Positions
    @property
    def tankFrameX(self) -> int: return 0 + LAYOUT.WINDOW_PADDING
    @property
    def dpsFrameX(self) -> int: return self.tankFrameX + self.tankFrameWidth + LAYOUT.ROLE_FRAME_SEPERATOR_PADDING
    # // @property
    # // def supportFrameX(self) -> int: return self.dpsFrameX + self.dpsFrameWidth + LAYOUT.ROLE_FRAME_SEPERATOR_PADDING
    @property
    def roleFramesY(self) -> int: return self.__geometry.height - self.roleFramesHeight

    # Switch- & icon positions
    @property
    def roleIconY(self) -> int: return self.roleFramesY - LAYOUT.ROLE_ICON_FRAME_HEIGHT
    @property
    def inputFrameY(self) -> int: return self.roleIconY - LAYOUT.SMALL_PADDING - LAYOUT.INPUT_FRAME_HEIGHT

    # Extras
    @property
    def roleFrameRectangles(self) -> tuple[Rect, Rect, Rect]:
        rectangles = []

        x = LAYOUT.WINDOW_PADDING
        y = self.roleFramesY

        for width, height in zip(self.heroLayout.widths, self.heroLayout.heights):
            pixelWidth = width * LAYOUT.HERO_BUTTON_SIZE
            pixelHeight = height * LAYOUT.HERO_BUTTON_SIZE

            rectangles.append(
                Rect(
                    x=x,
                    y=y,
                    width=pixelWidth,
                    height=pixelHeight,
                )
            )

            x += pixelWidth + LAYOUT.ROLE_FRAME_SEPERATOR_PADDING

        return tuple(rectangles)
    
    @property
    def recommendedHeroFrameWidth(self) -> int: 
        return (self.__geometry.width - (TOTAL_SLOTS_ALL - 1) * LAYOUT.SELECTED_HERO_COUNTERS_PADDING) / TOTAL_SLOTS_ALL


    # * Setters
    @activeResizeJob.setter
    def activeResizeJob(self, job: typing.Optional[str]): self.__activeResizeJob = job
    @isWindowResizing.setter
    def isWindowResizing(self, isResizing: bool): self.__isWindowResizing = isResizing

    def monitorResolutionChanged(self, screen: Resolution) -> RequiresResizing:
        """
        Only called when the screen size changes. This check must happen before this method is called

        ```
        if (width, height) != (self.layout.monitor.width, self.layout.monitor.height):
            self.layout(Resolution(width, height))
        ```
        """
        self.__screen = screen

        # ? Return True if the current window size is larger 
        # ? than the new screen size; otherwise, return False
        return (
            (self.__screen.width < self.__geometry.width) or
            (self.__screen.height < self.__geometry.height)
        )
    