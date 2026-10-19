# Global imports
from pathlib import Path
from math import ceil
import sys

# Same level imports
try:                from constants.common       import HERO_COUNTS
except ImportError: from src.constants.common   import HERO_COUNTS

# Super level imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path: sys.path.insert(0, str(PROJECT_ROOT))




def bestLayout(columns: int, A: tuple[int, int, int] = HERO_COUNTS.values()):
    """Choose column widths for three hero groups so their grids come out
    as short and as equal in height as possible.

    Background
    ----------
    Each hero role (tank, damage, support) is shown as a block of square
    icons that wraps like text: a group that is `w` icons wide and has `n`
    icons needs ceil(n / w) rows. The last row may be partly filled.
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


def minColumnsForRows(H: int, A: tuple[int, int, int] = HERO_COUNTS.values()):
    """Smallest layout in which every group is at most H rows tall.

    A group with n icons and width w needs ceil(n / w) rows, so it fits
    in H rows exactly when w >= ceil(n / H). Using that minimum width for
    each group gives the fewest columns that can reach height H.

    Returns
    -------
    tuple[int, tuple[int, int, int], list[int]]
        (columns_needed, widths, heights). Heights are <= H; a group can
        come out shorter than H when its width is rounded up.
    """
    widths = tuple(ceil(n / H) for n in A)
    heights = [ceil(n / w) for n, w in zip(A, widths)]
    return sum(widths), widths, heights



# ! NEWEST VERSION:

from math import ceil, log

TILE = 75
DEFAULT_RATIO = {"landscape": 11 / 5, "portrait": 5 / 11}   # tie-breaker only


def _allLayouts(A):
    """Every exact-fit layout for icon counts A, in both orientations.

    landscape: groups side by side; one layout per row count H, from
               minColumnsForRows(H). Its box is (sum of widths, tallest group).
    portrait:  groups stacked, each as wide as the window; one layout per
               width C, with rows = sum(ceil(n / C)).

    A layout is dropped if another layout of the same mode is no wider
    and no taller (it can never be the better choice).
    """
    found = {}
    for H in range(1, max(A) + 1):
        cols, widths, heights = minColumnsForRows(H, A)
        found.setdefault(("landscape", cols, max(heights)), dict(
            mode="landscape", columns=cols, rows=max(heights),
            widths=widths, heights=heights))
    for C in range(1, max(A) + 1):
        heights = [ceil(n / C) for n in A]
        found.setdefault(("portrait", C, sum(heights)), dict(
            mode="portrait", columns=C, rows=sum(heights),
            widths=(C, C, C), heights=heights))
    layouts = list(found.values())
    return [L for L in layouts if not any(
        o["mode"] == L["mode"] and o is not L
        and o["columns"] <= L["columns"] and o["rows"] <= L["rows"]
        for o in layouts)]


def snapWindow(avail_w, avail_h, screen_w, screen_h, A=None):
    """Pick the tightest-packing layout for a dragged window size.

    All pixel arguments are for the tiling area only (gaps/UI already
    subtracted; add them back when sizing the real window).

    Parameters
    ----------
    avail_w, avail_h : int   Tiling area the user dragged to, in px.
    screen_w, screen_h : int Largest tiling area the screen allows, in px.
    A : tuple[int, int, int] | None
        Icons per group (tank, damage, support). Defaults to HERO_COUNTS.

    Returns
    -------
    dict: mode ("landscape" or "portrait"), columns, rows, widths,
          heights, pixels (width, height of the exact-fit window).

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
    if A is None:
        A = tuple(HERO_COUNTS.values())

    c0 = max(1, avail_w // TILE)     # whole tiles the drag gives us
    r0 = max(1, avail_h // TILE)
    layouts = _allLayouts(A)

    def key(L):
        growth = max(0, L["columns"] - c0) + max(0, L["rows"] - r0)
        area = L["columns"] * L["rows"]
        ratio = abs(log(L["columns"] / L["rows"]) - log(DEFAULT_RATIO[L["mode"]]))
        return (growth, area, ratio)

    def fitsScreen(L):
        return L["columns"] * TILE <= screen_w and L["rows"] * TILE <= screen_h

    best = min((L for L in layouts if L["mode"] == "landscape"), key=key)
    if not fitsScreen(best):
        pool = [L for L in layouts if L["mode"] == "portrait" and fitsScreen(L)]
        if pool:
            best = min(pool, key=key)

    return dict(best, pixels=(best["columns"] * TILE, best["rows"] * TILE))