from __future__ import annotations

# Global configuration and theming for Minesweeper

# --- Configuration (defaults) ---
COLUMNS: int = 6
ROWS: int = 8
NUM_MINES: int = 7
TILE_SIZE: int = 48
GRID_LINE: int = 2

# UI spacing
H_PADDING: int = 16
V_PADDING: int = 16
STATUS_BAR_HEIGHT: int = 28
FOOTER_BAR_HEIGHT: int = 28
FPS: int = 60
DEBUG: bool = False
STATUS_FONT_BASE: int = 28

# Grid constraints
MIN_ROWS: int = 6
MAX_ROWS: int = 16
MIN_COLS: int = 6
MAX_COLS: int = 20

# Window dimensions computed at runtime from current settings
WINDOW_WIDTH: int | None = None
WINDOW_HEIGHT: int | None = None

# Colors (green theme)
COLOR_BG = (12, 24, 16)            # deep green background
COLOR_GRID = (34, 60, 38)          # muted green grid
COLOR_TILE_HIDDEN = (56, 94, 66)   # dark green hidden tile
COLOR_TILE_REVEALED = (168, 210, 176)  # light mint revealed tile
COLOR_TILE_MINE = (200, 54, 54)    # keep danger red for mines
COLOR_FLAG = (230, 60, 90)         # legacy (not used with watermelon icon)
COLOR_TEXT = (18, 36, 24)          # dark greenish text fallback
COLOR_STATUS = (210, 235, 215)     # mint status text
COLOR_WIN = (70, 200, 120)         # green win
COLOR_LOSE = (220, 70, 70)         # red lose

NUMBER_COLORS = {
    1: (35, 180, 120),   # teal-green
    2: (26, 160, 90),    # green
    3: (220, 90, 90),    # soft red
    4: (80, 170, 120),   # jade
    5: (150, 210, 160),  # pale green
    6: (60, 140, 100),   # deep green
    7: (200, 220, 200),  # light gray-green
    8: (18, 36, 24),     # dark text
}


def compute_window_dimensions() -> tuple[int, int]:
    """Compute window width/height from current global settings."""
    width = H_PADDING * 2 + COLUMNS * TILE_SIZE + GRID_LINE
    height = (
        V_PADDING * 2
        + STATUS_BAR_HEIGHT
        + FOOTER_BAR_HEIGHT
        + ROWS * TILE_SIZE
        + GRID_LINE
    )
    return width, height
