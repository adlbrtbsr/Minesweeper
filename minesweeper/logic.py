from __future__ import annotations

import random
from typing import List, Tuple

from . import config as cfg

# Board state containers
MineGrid = List[List[bool]]
AdjacencyGrid = List[List[int]]
RevealedGrid = List[List[bool]]
FlagGrid = List[List[bool]]


def create_mine_grid(
    rows: int,
    columns: int,
    num_mines: int,
    exclude: set[tuple[int, int]] | None = None,
) -> MineGrid:
    all_positions = [(r, c) for r in range(rows) for c in range(columns)]
    available = [pos for pos in all_positions if not exclude or pos not in exclude]
    if num_mines > len(available):
        raise ValueError(
            "Number of mines exceeds available cells when applying exclusions"
        )
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


def reveal_cell(
    r: int,
    c: int,
    mine_grid: MineGrid,
    adjacency_grid: AdjacencyGrid,
    revealed: RevealedGrid,
    flagged: FlagGrid,
) -> Tuple[bool, int]:
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
                    if 0 <= nr < cfg.ROWS and 0 <= nc < cfg.COLUMNS and not revealed[nr][nc]:
                        if not mine_grid[nr][nc]:
                            stack.append((nr, nc))
                        else:
                            # Do not auto-open mines
                            continue

    return False, newly_revealed


def chord_reveal(
    r: int,
    c: int,
    mine_grid: MineGrid,
    adjacency_grid: AdjacencyGrid,
    revealed: RevealedGrid,
    flagged: FlagGrid,
) -> Tuple[bool, int]:
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
            if 0 <= nr < cfg.ROWS and 0 <= nc < cfg.COLUMNS:
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
