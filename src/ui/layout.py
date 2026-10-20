# Global imports
from dataclasses import dataclass
from math import ceil, log
from typing import Literal
from pathlib import Path
import typing
import sys

# Same level imports
try:                from constants.common       import ROLE, HERO_COUNTS
except ImportError: from src.constants.common   import ROLE, HERO_COUNTS

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
    
    mode: Literal["landscape", "portrait"]
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
    """
    found = {}

    for rows in range(1, max(A) + 1):
        cols, widths, heights = minColumnsForRows(rows, A)
        found.setdefault(("landscape", cols, max(heights)), dict(
            mode="landscape", columns=cols, rows=max(heights),
            widths=widths, heights=heights))

    for C in range(1, max(A) + 1):
        heights = [ceil(n / C) for n in A]
        found.setdefault(("portrait", C, sum(heights)), dict(
            mode="portrait", columns=C, rows=sum(heights),
            widths=(C, C, C), heights=heights))

    layouts = list(found.values())

    return [
        L 
        for L in layouts if not any(
            o["mode"] == L["mode"] 
            and o is not L
            and o["columns"] <= L["columns"] 
            and o["rows"] <= L["rows"]
            for o in layouts
        )
    ]


def calculateOptimalHeroLayout(
    availableWidth: int, 
    availableHeight: int, 
    screenWidth: int, 
    screenHeight: int, 
    A: tuple[int, int, int] = HERO_COUNTS.values()
) -> HeroLayout:
    """Pick the tightest-packing layout for a dragged window size.

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
    """
    c0 = max(1, availableWidth // LAYOUT.HERO_BUTTON_SIZE)                              # whole tiles the drag gives us
    r0 = max(1, availableHeight // LAYOUT.HERO_BUTTON_SIZE)
    layouts = _allLayouts(A)

    def key(L):
        growth = max(0, L["columns"] - c0) + max(0, L["rows"] - r0)
        area = L["columns"] * L["rows"]
        ratio = abs(log(L["columns"] / L["rows"]) - log(LAYOUT.DEFAULT_RATIO[L["mode"]]))
        return (growth, area, ratio)

    def fitsScreen(L):
        return L["columns"] * LAYOUT.HERO_BUTTON_SIZE <= screenWidth and L["rows"] * LAYOUT.HERO_BUTTON_SIZE <= screenHeight

    best = min((L for L in layouts if L["mode"] == "landscape"), key=key)
    if not fitsScreen(best):
        pool = [L for L in layouts if L["mode"] == "portrait" and fitsScreen(L)]

        if pool: best = min(pool, key=key)

    return HeroLayout(
        **best, 
        pixels=(best["columns"] * LAYOUT.HERO_BUTTON_SIZE, best["rows"] * LAYOUT.HERO_BUTTON_SIZE))


# This function is currently superceeded by the above window sizing logic
@DeprecationWarning
def layoutFromColumns(columns: int, A: tuple[int, int, int] = HERO_COUNTS.values()):
    """Choose column widths for three hero groups so their grids come out
    as short and as equal in height as possible.

    Background
    ----------
    Each hero role (tank, damage, support) is shown as a block of square
    icons that wraps like text: a group that is `w` icons wide and has `n`
    icons needs `ceil(n / w)` rows. The last row may be partly filled.
    The three blocks sit side by side, so together they can use at most
    `columns` columns. This function brute-forces every way of splitting those
    columns into three widths and returns the best split.

    Parameters
    ----------
    columns : int
        Total number of icon columns available for all three groups
        combined. Compute it from the window size as
            columns = floor((window_width - gaps_between_groups) / icon_size)
        so any horizontal gaps are already subtracted. Must be >= 3,
        because each group needs at least one column.
    A : tuple[int, int, int]
        Number of icons in each group, e.g. (tanks, damage, supports).
        The order is kept: widths and heights are returned in this order.

    Returns
    -------
    tuple | None
        (score, widths, heights), or None if columns < 3 (no valid layout).

        score   : (tallest, spread, unused_columns, empty_cells)
                  The four numbers the layouts were ranked by. Only useful
                  for debugging; ignore it when rendering.
        widths  : (w1, w2, w3) columns given to each group.
        heights : [h1, h2, h3] rows each group needs at that width.

    How layouts are ranked
    ----------------------
    Python compares tuples left to right, so a later criterion only matters
    when all earlier ones tie. Lower is better for every entry:

        1. tallest  = max(heights)
           Prefer the layout whose tallest group is shortest. This ranks
           first on purpose. If spread ranked first, the search would pick
           tall, narrow layouts that leave columns unused just to make the
           three heights match exactly (e.g. 8/8/8 rows in 7 of 11 columns).
        2. spread   = max(heights) - min(heights)
           Among equally tall layouts, prefer the most even heights.
        3. unused   = columns - sum(widths)
           Prefer layouts that use all the available width.
        4. empty    = total empty cells in the partly filled last rows
           Final tie-breaker: prefer the tidiest last rows.

        If two layouts tie on all four, the first one found wins
        (the loops try narrow w1 first).

    Complexity
    ----------
    About columns^3 / 6 combinations, so a few hundred at most for realistic
    window widths. Cheap enough to rerun on every resize event, and the
    result can be cached per value of columns.

    Example
    -------
    >>> A = (15, 23, 16)             # tanks, damage, supports
    >>> score, widths, heights = bestLayout(12, A)
    >>> widths
    (3, 5, 4)
    >>> heights
    [5, 5, 4]

    Then make the tank container 3 icons wide, damage 5, supports 4, and
    let the icons wrap inside each container.

    Known limits
    ------------
    - Hard-coded for exactly three groups.
    - Very small columns gives very tall layouts (columns = 9 already needs 8 rows
      for these group sizes). Below some threshold you probably want to
      stack the groups vertically instead; that decision is not made here.
    - Nothing penalizes how much the layout changes between columns and columns - 1,
      so widths can jump noticeably as the window is resized.
    """
    best = None

    # Each group needs at least 1 column, so leave room for the others:
    # w1 can be at most columns - 2, w2 at most columns - w1 - 1, w3 takes what is left
    # (or less). Together this enumerates every (w1, w2, w3) with all
    # widths >= 1 and w1 + w2 + w3 <= columns.
    for w1 in range(1, columns - 1):
        for w2 in range(1, columns - w1):
            for w3 in range(1, columns - w1 - w2 + 1):
                w = (w1, w2, w3)

                # Rows needed per group: icons divided by width, rounded up.
                h = [ceil(ai / wi) for ai, wi in zip(A, w)]

                score = (
                    max(h),                                   # 1. tallest
                    max(h) - min(h),                          # 2. spread
                    columns - sum(w),                         # 3. unused cols
                    # 4. empty cells: each group has w*h slots but only
                    #    `ai` icons, so the difference is the gaps.
                    sum(wi * hi - ai for ai, wi, hi in zip(A, w, h)),
                )

                # Strict "<" keeps the first layout found on exact ties.
                if best is None or score < best[0]:
                    best = (score, w, h)

    return best  # (score, widths, heights)



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

    # Rectangles
    @property
    def roleFrameRects(self) -> tuple[Rect, Rect, Rect]:
        rectangles = []

        if self.heroLayout.mode == "landscape":
            x = LAYOUT.WINDOW_PADDING
            y = self.roleFramesY

            for width in self.heroLayout.widths:
                pixelWidth = width * LAYOUT.HERO_BUTTON_SIZE
                rectangles.append(
                    Rect(
                        x=x,
                        y=y,
                        width=pixelWidth,
                        height=self.heroLayout.heights[0] * LAYOUT.HERO_BUTTON_SIZE,
                    )
                )
                x += pixelWidth + LAYOUT.ROLE_FRAME_SEPERATOR_PADDING

        else:
            y = self.roleFramesY

            for height in self.heroLayout.heights:
                pixelHeight = height * LAYOUT.HERO_BUTTON_SIZE
                rectangles.append(
                    Rect(
                        x=LAYOUT.WINDOW_PADDING,
                        y=y,
                        width=self.heroLayout.widths[0] * LAYOUT.HERO_BUTTON_SIZE,
                        height=pixelHeight,
                    )
                )
                y += pixelHeight + LAYOUT.ROLE_FRAME_SEPERATOR_PADDING

        return tuple(rectangles)


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
    