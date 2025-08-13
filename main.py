import sys
import random
import argparse
import pygame
import traceback
from datetime import datetime
from typing import List, Tuple

# --- Configuration ---
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

# Window dimensions computed at runtime from current settings

# Colors
COLOR_BG = (20, 20, 20)
COLOR_GRID = (50, 50, 50)
COLOR_TILE_HIDDEN = (110, 110, 110)
COLOR_TILE_REVEALED = (190, 190, 190)
COLOR_TILE_MINE = (220, 60, 60)
COLOR_FLAG = (230, 60, 90)
COLOR_TEXT = (20, 20, 20)
COLOR_STATUS = (220, 220, 220)
COLOR_WIN = (70, 200, 120)
COLOR_LOSE = (220, 70, 70)

NUMBER_COLORS = {
    1: (25, 118, 210),   # blue
    2: (56, 142, 60),    # green
    3: (211, 47, 47),    # red
    4: (123, 31, 162),   # purple
    5: (255, 143, 0),    # orange
    6: (0, 151, 167),    # teal
    7: (97, 97, 97),     # gray
    8: (0, 0, 0),        # black
}

# Board state containers
MineGrid = List[List[bool]]
AdjacencyGrid = List[List[int]]
RevealedGrid = List[List[bool]]
FlagGrid = List[List[bool]]


def log_exception_to_file(exc: BaseException) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    trace = traceback.format_exc()
    log_entry = f"\n[{timestamp}] Unhandled exception: {exc}\n{trace}\n"
    try:
        with open("error.log", "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception:
        # If logging fails, we cannot do much here
        pass
    return log_entry


def show_error_screen(summary: str) -> None:
    try:
        if not pygame.get_init():
            pygame.init()
        width, height = 720, 220
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Minesweeper - Error")
        font = pygame.font.SysFont(None, 24)
        small = pygame.font.SysFont(None, 20)

        lines = [
            "An unexpected error occurred.",
            "Details were written to error.log.",
            "Press ESC or click to exit.",
            f"Error: {summary[:100]}" if summary else "",
        ]

        clock = pygame.time.Clock()
        while True:
            clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                    pygame.quit()
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pygame.quit()
                    return

            screen.fill((30, 30, 30))
            y = 24
            for i, text in enumerate(lines):
                if not text:
                    continue
                render = (font if i < 3 else small).render(text, True, (230, 230, 230))
                screen.blit(render, (20, y))
                y += 30
            pygame.display.flip()
    except Exception:
        # Last resort: print to stderr
        print("Error screen could not be displayed.", file=sys.stderr)
        return


def log_event(message: str) -> None:
    if not DEBUG:
        return
    try:
        timestamp = datetime.now().strftime("%H:%M:%S")
        with open("run.log", "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass


def get_quit_confirm_rects() -> tuple[pygame.Rect, pygame.Rect, pygame.Rect]:
    overlay_width = min(420, WINDOW_WIDTH - 40)
    overlay_height = 150
    overlay_x = (WINDOW_WIDTH - overlay_width) // 2
    overlay_y = (WINDOW_HEIGHT - overlay_height) // 2
    overlay_rect = pygame.Rect(overlay_x, overlay_y, overlay_width, overlay_height)

    button_width = 100
    button_height = 36
    gap = 20
    yes_rect = pygame.Rect(
        overlay_rect.centerx - gap // 2 - button_width,
        overlay_rect.bottom - 56,
        button_width,
        button_height,
    )
    no_rect = pygame.Rect(
        overlay_rect.centerx + gap // 2,
        overlay_rect.bottom - 56,
        button_width,
        button_height,
    )
    return yes_rect, no_rect, overlay_rect


def draw_quit_confirm(screen: pygame.Surface, font: pygame.font.Font) -> None:
    yes_rect, no_rect, overlay_rect = get_quit_confirm_rects()
    # Dim background
    dim = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 140))
    screen.blit(dim, (0, 0))

    # Panel
    pygame.draw.rect(screen, (50, 50, 50), overlay_rect, border_radius=8)
    pygame.draw.rect(screen, (90, 90, 90), overlay_rect, width=2, border_radius=8)

    msg1 = font.render("Quit the game?", True, (230, 230, 230))
    msg2 = font.render("Y = Yes, N/Esc = No", True, (180, 180, 180))
    screen.blit(msg1, (overlay_rect.centerx - msg1.get_width() // 2, overlay_rect.top + 24))
    screen.blit(msg2, (overlay_rect.centerx - msg2.get_width() // 2, overlay_rect.top + 56))

    # Buttons
    def draw_btn(rect: pygame.Rect, label: str):
        pygame.draw.rect(screen, (70, 70, 70), rect, border_radius=6)
        t = font.render(label, True, (230, 230, 230))
        screen.blit(t, (rect.centerx - t.get_width() // 2, rect.centery - t.get_height() // 2))

    draw_btn(yes_rect, "Yes")
    draw_btn(no_rect, "No")

def run_menu(initial_rows: int, initial_cols: int, initial_mines: int) -> tuple[int, int, int] | None:
    menu_width = 520
    menu_height = 400
    pygame.display.set_caption("Minesweeper - Setup")
    screen = pygame.display.set_mode((menu_width, menu_height))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)

    rows = max(1, initial_rows)
    cols = max(1, initial_cols)
    mines = max(1, min(initial_mines, rows * cols - 1))

    def draw_button(rect: pygame.Rect, label: str, active: bool = True):
        color = (70, 70, 70) if active else (40, 40, 40)
        pygame.draw.rect(screen, color, rect, border_radius=6)
        text = font.render(label, True, (230, 230, 230))
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)

    while True:
        clock.tick(60)
        screen.fill(COLOR_BG)

        title = font.render("Choose grid and mines", True, COLOR_STATUS)
        screen.blit(title, (H_PADDING, V_PADDING))

        # Preset buttons
        preset_y = V_PADDING + 34
        preset_w, preset_h, preset_gap = 140, 36, 12
        beginner_rect = pygame.Rect(H_PADDING, preset_y, preset_w, preset_h)
        intermediate_rect = pygame.Rect(H_PADDING + (preset_w + preset_gap), preset_y, preset_w, preset_h)
        expert_rect = pygame.Rect(H_PADDING + 2 * (preset_w + preset_gap), preset_y, preset_w, preset_h)

        draw_button(beginner_rect, "Beginner")
        draw_button(intermediate_rect, "Intermediate")
        draw_button(expert_rect, "Expert")

        # Layout values and +/- buttons
        y0 = 100
        row_label = font.render(f"Rows: {rows}", True, COLOR_STATUS)
        col_label = font.render(f"Cols: {cols}", True, COLOR_STATUS)
        max_mines = max(1, rows * cols - 1)
        mines = min(mines, max_mines)
        mine_label = font.render(f"Mines: {mines} (max {max_mines})", True, COLOR_STATUS)

        screen.blit(row_label, (H_PADDING, y0))
        screen.blit(col_label, (H_PADDING, y0 + 50))
        screen.blit(mine_label, (H_PADDING, y0 + 100))

        btn_w, btn_h = 40, 36
        gap_x = 10
        base_x = 300

        rows_minus = pygame.Rect(base_x, y0 - 6, btn_w, btn_h)
        rows_plus = pygame.Rect(base_x + btn_w + gap_x, y0 - 6, btn_w, btn_h)
        cols_minus = pygame.Rect(base_x, y0 + 44, btn_w, btn_h)
        cols_plus = pygame.Rect(base_x + btn_w + gap_x, y0 + 44, btn_w, btn_h)
        mines_minus = pygame.Rect(base_x, y0 + 94, btn_w, btn_h)
        mines_plus = pygame.Rect(base_x + btn_w + gap_x, y0 + 94, btn_w, btn_h)

        draw_button(rows_minus, "-")
        draw_button(rows_plus, "+")
        draw_button(cols_minus, "-")
        draw_button(cols_plus, "+")
        draw_button(mines_minus, "-")
        draw_button(mines_plus, "+")

        start_rect = pygame.Rect(H_PADDING, menu_height - 70, 140, 42)
        quit_rect = pygame.Rect(H_PADDING + 160, menu_height - 70, 140, 42)
        draw_button(start_rect, "Start")
        draw_button(quit_rect, "Quit")

        hint = font.render("Tip: adjust mines after grid", True, (150, 150, 150))
        screen.blit(hint, (H_PADDING, menu_height - 120))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                # Preset selections
                if beginner_rect.collidepoint(mx, my):
                    rows, cols, mines = 9, 9, 10
                    continue
                elif intermediate_rect.collidepoint(mx, my):
                    rows, cols, mines = 16, 16, 40
                    continue
                elif expert_rect.collidepoint(mx, my):
                    rows, cols, mines = 16, 30, 99
                    continue
                if rows_minus.collidepoint(mx, my):
                    rows = max(1, rows - 1)
                elif rows_plus.collidepoint(mx, my):
                    rows = rows + 1
                elif cols_minus.collidepoint(mx, my):
                    cols = max(1, cols - 1)
                elif cols_plus.collidepoint(mx, my):
                    cols = cols + 1
                elif mines_minus.collidepoint(mx, my):
                    mines = max(1, mines - 1)
                elif mines_plus.collidepoint(mx, my):
                    mines = min(rows * cols - 1, mines + 1)
                elif start_rect.collidepoint(mx, my):
                    mines = max(1, min(mines, rows * cols - 1))
                    return rows, cols, mines
                elif quit_rect.collidepoint(mx, my):
                    return None

def create_mine_grid(rows: int, columns: int, num_mines: int,
                     exclude: set[tuple[int, int]] | None = None) -> MineGrid:
    all_positions = [(r, c) for r in range(rows) for c in range(columns)]
    if exclude:
        available = [pos for pos in all_positions if pos not in exclude]
    else:
        available = all_positions
    if num_mines > len(available):
        raise ValueError("Number of mines exceeds available cells when applying exclusions")
    mine_positions = set(random.sample(available, num_mines))
    return [[(r, c) in mine_positions for c in range(columns)] for r in range(rows)]


def calc_adjacency(mine_grid: MineGrid) -> AdjacencyGrid:
    rows = len(mine_grid)
    columns = len(mine_grid[0])

    def neighbors(r: int, c: int):
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < columns:
                    yield nr, nc

    adjacency: AdjacencyGrid = [[0 for _ in range(columns)] for _ in range(rows)]
    for r in range(rows):
        for c in range(columns):
            if mine_grid[r][c]:
                adjacency[r][c] = -1  # sentinel for mine
            else:
                count = 0
                for nr, nc in neighbors(r, c):
                    if mine_grid[nr][nc]:
                        count += 1
                adjacency[r][c] = count
    return adjacency


def pixel_to_cell(x: int, y: int) -> Tuple[int, int] | None:
    # Adjust for margins and status bar
    grid_top = V_PADDING + STATUS_BAR_HEIGHT
    if y < grid_top:
        return None

    grid_x = x - H_PADDING
    grid_y = y - grid_top

    if grid_x < 0 or grid_y < 0:
        return None

    c = grid_x // TILE_SIZE
    r = grid_y // TILE_SIZE

    if 0 <= r < ROWS and 0 <= c < COLUMNS:
        return (r, c)
    return None


def draw_bomb_icon(screen: pygame.Surface, rect: pygame.Rect) -> None:
    radius = max(6, min(rect.width, rect.height) // 3)
    center_x, center_y = rect.center
    # Body
    pygame.draw.circle(screen, (25, 25, 25), (center_x, center_y), radius)
    # Highlight
    highlight_radius = max(2, radius // 3)
    pygame.draw.circle(screen, (80, 80, 80), (center_x - radius // 3, center_y - radius // 3), highlight_radius)
    # Neck
    neck_w = max(2, radius // 3)
    neck_h = max(3, radius // 2)
    neck_rect = pygame.Rect(0, 0, neck_w, neck_h)
    neck_rect.centerx = center_x + radius // 2
    neck_rect.bottom = center_y - radius // 2
    pygame.draw.rect(screen, (90, 90, 90), neck_rect, border_radius=2)
    # Fuse
    fuse_start = (neck_rect.centerx, neck_rect.top)
    fuse_len = max(6, radius // 2)
    fuse_end = (fuse_start[0] + fuse_len, fuse_start[1] - fuse_len)
    pygame.draw.line(screen, (170, 140, 100), fuse_start, fuse_end, width=max(2, radius // 6))
    # Spark
    spark_r = max(3, radius // 3)
    cx, cy = fuse_end
    for angle in range(0, 360, 45):
        vec = pygame.math.Vector2(1, 0).rotate(angle)
        dx = int(vec.x * spark_r * 1.6)
        dy = int(vec.y * spark_r * 1.6)
        pygame.draw.line(screen, (255, 190, 60), (cx, cy), (cx + dx, cy + dy), width=2)
    pygame.draw.circle(screen, (255, 230, 140), (cx, cy), spark_r)


def draw_watermelon_icon(screen: pygame.Surface, rect: pygame.Rect) -> None:
    center_x, center_y = rect.center
    radius = max(6, min(rect.width, rect.height) // 3)
    rind_thickness = max(2, radius // 5)
    # Outer rind
    pygame.draw.circle(screen, (24, 120, 44), (center_x, center_y), radius)
    # Inner rind
    pygame.draw.circle(screen, (140, 210, 140), (center_x, center_y), radius - rind_thickness)
    # Flesh
    flesh_r = max(2, radius - rind_thickness * 2)
    pygame.draw.circle(screen, (230, 70, 90), (center_x, center_y), flesh_r)
    # Seeds
    seed_count = max(5, radius)
    for i in range(seed_count):
        vec = pygame.math.Vector2(1, 0).rotate(i * (360 / seed_count))
        sx = int(center_x + vec.x * (flesh_r * 0.6))
        sy = int(center_y + vec.y * (flesh_r * 0.6))
        pygame.draw.circle(screen, (15, 15, 15), (sx, sy), max(1, radius // 8))


def draw_board(screen: pygame.Surface, font: pygame.font.Font, mine_grid: MineGrid,
               adjacency_grid: AdjacencyGrid, revealed: RevealedGrid, flagged: FlagGrid,
               game_state: str, remaining_safe: int, elapsed_seconds: int) -> None:
    screen.fill(COLOR_BG)

    # Status text
    if game_state == "running":
        # Remaining mines: total mines minus placed flags
        flags_placed = sum(1 for r in range(ROWS) for c in range(COLUMNS) if flagged[r][c])
        remaining_mines = max(0, NUM_MINES - flags_placed)
        status_text = f"Mines: {remaining_mines}    L: reveal   R: flag   Mid: chord   M: menu"
    else:
        status_text = "L: reveal   R: flag"
    if game_state == "lost":
        status_text = "You hit a mine. Press R to restart, M for menu."
    elif game_state == "won":
        status_text = "You won! Press R to restart, M for menu."

    # Render status text with dynamic downscaling to fit narrow windows
    available_width = max(50, (globals().get("WINDOW_WIDTH", 0) or screen.get_width()) - 2 * H_PADDING)
    status_font = font
    status_surface = status_font.render(status_text, True, COLOR_STATUS)
    if status_surface.get_width() > available_width:
        # Estimate a smaller size based on width ratio
        base_size = max(10, status_font.get_height())
        target_size = max(12, int(base_size * available_width / max(1, status_surface.get_width())))
        # Re-render with a smaller font
        status_font = pygame.font.SysFont(None, target_size)
        status_surface = status_font.render(status_text, True, COLOR_STATUS)
    screen.blit(status_surface, (H_PADDING, V_PADDING))

    grid_top = V_PADDING + STATUS_BAR_HEIGHT
    for r in range(ROWS):
        for c in range(COLUMNS):
            rect = pygame.Rect(
                H_PADDING + c * TILE_SIZE,
                grid_top + r * TILE_SIZE,
                TILE_SIZE - GRID_LINE,
                TILE_SIZE - GRID_LINE,
            )

            if revealed[r][c]:
                if mine_grid[r][c]:
                    pygame.draw.rect(screen, COLOR_TILE_MINE, rect)
                    draw_bomb_icon(screen, rect)
                else:
                    pygame.draw.rect(screen, COLOR_TILE_REVEALED, rect)
                    adj = adjacency_grid[r][c]
                    if adj > 0:
                        color = NUMBER_COLORS.get(adj, COLOR_TEXT)
                        text_surface = font.render(str(adj), True, color)
                        text_rect = text_surface.get_rect(center=rect.center)
                        screen.blit(text_surface, text_rect)
            else:
                pygame.draw.rect(screen, COLOR_TILE_HIDDEN, rect)
                if flagged[r][c]:
                    draw_watermelon_icon(screen, rect)

    # Border around grid
    grid_rect = pygame.Rect(H_PADDING, grid_top, COLUMNS * TILE_SIZE, ROWS * TILE_SIZE)
    pygame.draw.rect(screen, COLOR_GRID, grid_rect, width=2)

    # Footer info
    def format_time(total_seconds: int) -> str:
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:02d}"

    footer_text = f"Time: {format_time(elapsed_seconds)}    Safe: {remaining_safe}"
    if game_state == "won":
        footer_color = COLOR_WIN
    elif game_state == "lost":
        footer_color = COLOR_LOSE
    else:
        footer_color = COLOR_STATUS
    footer_surface = font.render(footer_text, True, footer_color)
    footer_y = WINDOW_HEIGHT - V_PADDING - FOOTER_BAR_HEIGHT + 6
    screen.blit(footer_surface, (H_PADDING, footer_y))


def reveal_cell(r: int, c: int, mine_grid: MineGrid, adjacency_grid: AdjacencyGrid,
                revealed: RevealedGrid, flagged: FlagGrid) -> Tuple[bool, int]:
    """
    Reveals the cell at (r, c). Returns (hit_mine, num_newly_revealed).
    """
    if revealed[r][c] or flagged[r][c]:
        return False, 0

    newly_revealed = 0
    stack = [(r, c)]
    while stack:
        cr, cc = stack.pop()
        if revealed[cr][cc] or flagged[cr][cc]:
            continue

        revealed[cr][cc] = True
        newly_revealed += 1

        if mine_grid[cr][cc]:
            # If we popped into a mine due to direct click, signal mine. We still mark it revealed.
            return True, newly_revealed

        if adjacency_grid[cr][cc] == 0:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < ROWS and 0 <= nc < COLUMNS and not revealed[nr][nc]:
                        if not mine_grid[nr][nc]:
                            stack.append((nr, nc))
                        else:
                            # Do not auto-open mines
                            continue

    return False, newly_revealed


def chord_reveal(r: int, c: int, mine_grid: MineGrid, adjacency_grid: AdjacencyGrid,
                 revealed: RevealedGrid, flagged: FlagGrid) -> Tuple[bool, int]:
    """
    If the number of flagged neighbors equals the number on a revealed numbered tile,
    reveal all unflagged, unrevealed neighbors. Returns (hit_mine, total_opened).
    """
    if not revealed[r][c]:
        return False, 0
    number_on_tile = adjacency_grid[r][c]
    if number_on_tile <= 0:
        return False, 0

    # Count flags around
    flagged_count = 0
    neighbors_coords: list[tuple[int, int]] = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if 0 <= nr < ROWS and 0 <= nc < COLUMNS:
                neighbors_coords.append((nr, nc))
                if flagged[nr][nc]:
                    flagged_count += 1

    if flagged_count != number_on_tile:
        return False, 0

    total_opened = 0
    for nr, nc in neighbors_coords:
        if not flagged[nr][nc] and not revealed[nr][nc]:
            hit_mine, opened = reveal_cell(nr, nc, mine_grid, adjacency_grid, revealed, flagged)
            total_opened += opened
            if hit_mine:
                return True, total_opened

    return False, total_opened


def main() -> None:
    # Declare globals first since we both read and assign them below
    global ROWS, COLUMNS, NUM_MINES, TILE_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT

    parser = argparse.ArgumentParser(description="Minesweeper (Python + Pygame)")
    parser.add_argument("--rows", type=int, default=ROWS, help="Number of rows (default: 8)")
    parser.add_argument("--cols", type=int, default=COLUMNS, help="Number of columns (default: 6)")
    parser.add_argument("--mines", type=int, default=NUM_MINES, help="Number of mines (default: 7)")
    parser.add_argument("--tile-size", type=int, default=TILE_SIZE, help="Tile size in pixels (default: 48)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging to run.log")
    args = parser.parse_args()

    # Update globals from CLI
    ROWS = max(1, args.rows)
    COLUMNS = max(1, args.cols)
    TILE_SIZE = max(12, args.tile_size)
    max_mines = ROWS * COLUMNS - 1
    NUM_MINES = max(1, min(args.mines, max_mines))
    global DEBUG
    DEBUG = bool(args.debug)

    # Compute window dimensions at runtime and expose as globals for rendering helpers
    global WINDOW_WIDTH, WINDOW_HEIGHT
    WINDOW_WIDTH = H_PADDING * 2 + COLUMNS * TILE_SIZE + GRID_LINE
    WINDOW_HEIGHT = (
        V_PADDING * 2
        + STATUS_BAR_HEIGHT
        + FOOTER_BAR_HEIGHT
        + ROWS * TILE_SIZE
        + GRID_LINE
    )

    pygame.init()

    # Optional pre-game menu if no CLI overrides were provided
    if (args.rows == 8 and args.cols == 6 and args.mines == 7 and args.tile_size == 48):
        menu_result = run_menu(ROWS, COLUMNS, NUM_MINES)
        if menu_result is None:
            pygame.quit()
            sys.exit(0)
        ROWS, COLUMNS, NUM_MINES = menu_result

        # Recompute dimensions with new selections
        WINDOW_WIDTH = H_PADDING * 2 + COLUMNS * TILE_SIZE + GRID_LINE
        WINDOW_HEIGHT = (
            V_PADDING * 2
            + STATUS_BAR_HEIGHT
            + FOOTER_BAR_HEIGHT
            + ROWS * TILE_SIZE
            + GRID_LINE
        )

    pygame.display.set_caption(f"Minesweeper ({COLUMNS}x{ROWS}, {NUM_MINES} mines)")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    def reset() -> tuple[MineGrid, AdjacencyGrid, RevealedGrid, FlagGrid, str, int, bool, int | None, int | None]:
        mine_grid_local = create_mine_grid(ROWS, COLUMNS, NUM_MINES)
        adjacency_local = calc_adjacency(mine_grid_local)
        revealed_local = [[False for _ in range(COLUMNS)] for _ in range(ROWS)]
        flagged_local = [[False for _ in range(COLUMNS)] for _ in range(ROWS)]
        game_state_local = "running"  # running | won | lost
        remaining_safe_local = ROWS * COLUMNS - NUM_MINES
        is_first_click_local = True
        start_ticks_local: int | None = None
        end_ticks_local: int | None = None
        return (
            mine_grid_local,
            adjacency_local,
            revealed_local,
            flagged_local,
            game_state_local,
            remaining_safe_local,
            is_first_click_local,
            start_ticks_local,
            end_ticks_local,
        )

    mine_grid, adjacency_grid, revealed, flagged, game_state, remaining_safe, is_first_click, start_ticks, end_ticks = reset()

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                log_event("QUIT event received")
                # Ask for confirmation if enabled
                confirming = True
                while confirming:
                    for ev in pygame.event.get():
                        if ev.type == pygame.QUIT:
                            confirming = False
                            pygame.quit()
                            return
                        if ev.type == pygame.KEYDOWN:
                            if ev.key in (pygame.K_ESCAPE, pygame.K_n):
                                confirming = False
                            elif ev.key in (pygame.K_y, pygame.K_RETURN):
                                pygame.quit()
                                return
                        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                            mx, my = ev.pos
                            yes_rect, no_rect, _ = get_quit_confirm_rects()
                            if yes_rect.collidepoint(mx, my):
                                pygame.quit()
                                return
                            if no_rect.collidepoint(mx, my):
                                confirming = False
                    # Draw confirmation overlay
                    draw_board(screen, font, mine_grid, adjacency_grid, revealed, flagged, game_state, remaining_safe, elapsed_seconds)
                    draw_quit_confirm(screen, font)
                    pygame.display.flip()
                    clock.tick(30)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                log_event("Key R pressed: reset")
                mine_grid, adjacency_grid, revealed, flagged, game_state, remaining_safe, is_first_click, start_ticks, end_ticks = reset()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                # Return to menu, reconfigure grid, then reset game state
                log_event("Key M pressed: open menu")
                menu_result = run_menu(ROWS, COLUMNS, NUM_MINES)
                if menu_result is None:
                    log_event("Menu returned None (Quit)")
                    pygame.quit()
                    return
                ROWS, COLUMNS, NUM_MINES = menu_result
                WINDOW_WIDTH = H_PADDING * 2 + COLUMNS * TILE_SIZE + GRID_LINE
                WINDOW_HEIGHT = (
                    V_PADDING * 2
                    + STATUS_BAR_HEIGHT
                    + FOOTER_BAR_HEIGHT
                    + ROWS * TILE_SIZE
                    + GRID_LINE
                )
                screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
                pygame.display.set_caption(f"Minesweeper ({COLUMNS}x{ROWS}, {NUM_MINES} mines)")
                mine_grid, adjacency_grid, revealed, flagged, game_state, remaining_safe, is_first_click, start_ticks, end_ticks = reset()
            if game_state == "running" and event.type == pygame.MOUSEBUTTONDOWN:
                cell = pixel_to_cell(*event.pos)
                if cell is None:
                    continue
                r, c = cell
                log_event(f"Mouse button {event.button} on cell ({r},{c})")
                # Middle click (button 2) or chord (left+right) to auto-reveal neighbors
                if event.button == 2:
                    # Chording should not start the timer unless it reveals something
                    hit_mine, opened = chord_reveal(r, c, mine_grid, adjacency_grid, revealed, flagged)
                    if opened > 0 and start_ticks is None:
                        start_ticks = pygame.time.get_ticks()
                    if hit_mine:
                        game_state = "lost"
                        if start_ticks is not None and end_ticks is None:
                            end_ticks = pygame.time.get_ticks()
                        for rr in range(ROWS):
                            for cc in range(COLUMNS):
                                if mine_grid[rr][cc]:
                                    revealed[rr][cc] = True
                    else:
                        remaining_safe -= opened
                        if remaining_safe == 0:
                            game_state = "won"
                            if start_ticks is not None and end_ticks is None:
                                end_ticks = pygame.time.get_ticks()
                elif event.button == 1:  # left click to reveal or chord if right also held
                    # If both buttons are pressed and clicking a revealed number, treat as chord
                    pressed = pygame.mouse.get_pressed(3)
                    if pressed[2] and revealed[r][c] and adjacency_grid[r][c] > 0:
                        hit_mine, opened = chord_reveal(r, c, mine_grid, adjacency_grid, revealed, flagged)
                        if opened > 0 and start_ticks is None:
                            start_ticks = pygame.time.get_ticks()
                        if hit_mine:
                            game_state = "lost"
                            if start_ticks is not None and end_ticks is None:
                                end_ticks = pygame.time.get_ticks()
                            for rr in range(ROWS):
                                for cc in range(COLUMNS):
                                    if mine_grid[rr][cc]:
                                        revealed[rr][cc] = True
                        else:
                            remaining_safe -= opened
                            if remaining_safe == 0:
                                game_state = "won"
                                if start_ticks is not None and end_ticks is None:
                                    end_ticks = pygame.time.get_ticks()
                        continue
                    # First-click safety: ensure the first revealed cell is safe
                    # First-click safety: ensure the first revealed cell is safe
                    if is_first_click and not revealed[r][c]:
                        is_first_click = False
                        mine_grid = create_mine_grid(ROWS, COLUMNS, NUM_MINES, exclude={(r, c)})
                        adjacency_grid = calc_adjacency(mine_grid)
                        if start_ticks is None:
                            start_ticks = pygame.time.get_ticks()
                    elif start_ticks is None and not revealed[r][c]:
                        # Start timer on the first actual reveal even if first-click already passed (edge cases)
                        start_ticks = pygame.time.get_ticks()

                    hit_mine, opened = reveal_cell(r, c, mine_grid, adjacency_grid, revealed, flagged)
                    if hit_mine:
                        game_state = "lost"
                        if start_ticks is not None and end_ticks is None:
                            end_ticks = pygame.time.get_ticks()
                        # Reveal all mines for feedback
                        for rr in range(ROWS):
                            for cc in range(COLUMNS):
                                if mine_grid[rr][cc]:
                                    revealed[rr][cc] = True
                    else:
                        remaining_safe -= opened
                        if remaining_safe == 0:
                            game_state = "won"
                            if start_ticks is not None and end_ticks is None:
                                end_ticks = pygame.time.get_ticks()
                elif event.button == 3:  # right click to toggle flag
                    if not revealed[r][c]:
                        flagged[r][c] = not flagged[r][c]

        # Compute elapsed time in seconds; freeze when game is over
        if start_ticks is None:
            elapsed_seconds = 0
        else:
            now_ticks = pygame.time.get_ticks()
            if game_state == "running" or end_ticks is None:
                elapsed_seconds = max(0, (now_ticks - start_ticks) // 1000)
            else:
                elapsed_seconds = max(0, (end_ticks - start_ticks) // 1000)

        draw_board(screen, font, mine_grid, adjacency_grid, revealed, flagged, game_state, remaining_safe, elapsed_seconds)
        pygame.display.flip()


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        # Allow normal exits (e.g., window close) without error screen
        raise
    except Exception as exc:
        # Log and show a minimal error screen instead of abrupt exit
        summary = log_exception_to_file(exc)
        show_error_screen(str(exc))
