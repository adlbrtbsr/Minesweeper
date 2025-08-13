import sys
import random
import argparse
import pygame
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


def draw_board(screen: pygame.Surface, font: pygame.font.Font, mine_grid: MineGrid,
               adjacency_grid: AdjacencyGrid, revealed: RevealedGrid, flagged: FlagGrid,
               game_state: str, remaining_safe: int) -> None:
    screen.fill(COLOR_BG)

    # Status text
    if game_state == "running":
        # Remaining mines: total mines minus placed flags
        flags_placed = sum(1 for r in range(ROWS) for c in range(COLUMNS) if flagged[r][c])
        remaining_mines = max(0, NUM_MINES - flags_placed)
        status_text = f"Mines: {remaining_mines}    L: reveal   R: flag"
    else:
        status_text = "L: reveal   R: flag"
    if game_state == "lost":
        status_text = "You hit a mine. Press R to restart."
    elif game_state == "won":
        status_text = "You won! Press R to restart."

    status_surface = font.render(status_text, True, COLOR_STATUS)
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
                    # draw mine circle
                    center = rect.center
                    radius = min(rect.width, rect.height) // 4
                    pygame.draw.circle(screen, (30, 30, 30), center, radius)
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
                    # draw a simple flag triangle
                    p1 = (rect.left + rect.width // 3, rect.top + rect.height // 5)
                    p2 = (rect.left + rect.width // 3, rect.bottom - rect.height // 5)
                    p3 = (rect.right - rect.width // 5, rect.top + rect.height // 2)
                    pygame.draw.polygon(screen, COLOR_FLAG, [p1, p2, p3])

    # Border around grid
    grid_rect = pygame.Rect(H_PADDING, grid_top, COLUMNS * TILE_SIZE, ROWS * TILE_SIZE)
    pygame.draw.rect(screen, COLOR_GRID, grid_rect, width=2)

    # Footer info
    footer_text = f"Safe tiles remaining: {remaining_safe}"
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


def main() -> None:
    # Declare globals first since we both read and assign them below
    global ROWS, COLUMNS, NUM_MINES, TILE_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT

    parser = argparse.ArgumentParser(description="Minesweeper (Python + Pygame)")
    parser.add_argument("--rows", type=int, default=ROWS, help="Number of rows (default: 8)")
    parser.add_argument("--cols", type=int, default=COLUMNS, help="Number of columns (default: 6)")
    parser.add_argument("--mines", type=int, default=NUM_MINES, help="Number of mines (default: 7)")
    parser.add_argument("--tile-size", type=int, default=TILE_SIZE, help="Tile size in pixels (default: 48)")
    args = parser.parse_args()

    # Update globals from CLI
    ROWS = max(1, args.rows)
    COLUMNS = max(1, args.cols)
    TILE_SIZE = max(12, args.tile_size)
    max_mines = ROWS * COLUMNS - 1
    NUM_MINES = max(1, min(args.mines, max_mines))

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
    pygame.display.set_caption(f"Minesweeper ({COLUMNS}x{ROWS}, {NUM_MINES} mines)")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    def reset() -> tuple[MineGrid, AdjacencyGrid, RevealedGrid, FlagGrid, str, int, bool]:
        mine_grid_local = create_mine_grid(ROWS, COLUMNS, NUM_MINES)
        adjacency_local = calc_adjacency(mine_grid_local)
        revealed_local = [[False for _ in range(COLUMNS)] for _ in range(ROWS)]
        flagged_local = [[False for _ in range(COLUMNS)] for _ in range(ROWS)]
        game_state_local = "running"  # running | won | lost
        remaining_safe_local = ROWS * COLUMNS - NUM_MINES
        is_first_click_local = True
        return (
            mine_grid_local,
            adjacency_local,
            revealed_local,
            flagged_local,
            game_state_local,
            remaining_safe_local,
            is_first_click_local,
        )

    mine_grid, adjacency_grid, revealed, flagged, game_state, remaining_safe, is_first_click = reset()

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                mine_grid, adjacency_grid, revealed, flagged, game_state, remaining_safe, is_first_click = reset()
            if game_state == "running" and event.type == pygame.MOUSEBUTTONDOWN:
                cell = pixel_to_cell(*event.pos)
                if cell is None:
                    continue
                r, c = cell
                if event.button == 1:  # left click to reveal
                    # First-click safety: ensure the first revealed cell is safe
                    if is_first_click and not revealed[r][c]:
                        is_first_click = False
                        mine_grid = create_mine_grid(ROWS, COLUMNS, NUM_MINES, exclude={(r, c)})
                        adjacency_grid = calc_adjacency(mine_grid)

                    hit_mine, opened = reveal_cell(r, c, mine_grid, adjacency_grid, revealed, flagged)
                    if hit_mine:
                        game_state = "lost"
                        # Reveal all mines for feedback
                        for rr in range(ROWS):
                            for cc in range(COLUMNS):
                                if mine_grid[rr][cc]:
                                    revealed[rr][cc] = True
                    else:
                        remaining_safe -= opened
                        if remaining_safe == 0:
                            game_state = "won"
                elif event.button == 3:  # right click to toggle flag
                    if not revealed[r][c]:
                        flagged[r][c] = not flagged[r][c]

        draw_board(screen, font, mine_grid, adjacency_grid, revealed, flagged, game_state, remaining_safe)
        pygame.display.flip()


if __name__ == "__main__":
    main()
