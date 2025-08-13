import sys
import argparse
import pygame

from minesweeper import config as cfg
from minesweeper.utils import log_exception_to_file, show_error_screen, log_event
from minesweeper.menu import run_menu, get_quit_confirm_rects, draw_quit_confirm
from minesweeper.logic import create_mine_grid, calc_adjacency, reveal_cell, chord_reveal
from minesweeper.render import draw_board, pixel_to_cell


def main() -> None:
    parser = argparse.ArgumentParser(description="Minesweeper (Python + Pygame)")
    parser.add_argument("--rows", type=int, default=cfg.ROWS, help="Number of rows (default: 8)")
    parser.add_argument("--cols", type=int, default=cfg.COLUMNS, help="Number of columns (default: 6)")
    parser.add_argument("--mines", type=int, default=cfg.NUM_MINES, help="Number of mines (default: 7)")
    parser.add_argument("--tile-size", type=int, default=cfg.TILE_SIZE, help="Tile size in pixels (default: 48)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging to run.log")
    args = parser.parse_args()

    # Apply CLI options into shared config
    cfg.ROWS = max(cfg.MIN_ROWS, min(cfg.MAX_ROWS, args.rows))
    cfg.COLUMNS = max(cfg.MIN_COLS, min(cfg.MAX_COLS, args.cols))
    cfg.TILE_SIZE = max(12, args.tile_size)
    cfg.NUM_MINES = max(1, min(args.mines, cfg.ROWS * cfg.COLUMNS - 1))
    cfg.DEBUG = bool(args.debug)

    # Compute dimensions
    cfg.WINDOW_WIDTH, cfg.WINDOW_HEIGHT = cfg.compute_window_dimensions()

    pygame.init()

    # Optional pre-game menu if launching with defaults
    if (args.rows == 8 and args.cols == 6 and args.mines == 7 and args.tile_size == 48):
        menu_result = run_menu(cfg.ROWS, cfg.COLUMNS, cfg.NUM_MINES, cfg.TILE_SIZE)
        if menu_result is None:
            pygame.quit()
            sys.exit(0)
        cfg.ROWS, cfg.COLUMNS, cfg.NUM_MINES, cfg.TILE_SIZE = menu_result
        cfg.WINDOW_WIDTH, cfg.WINDOW_HEIGHT = cfg.compute_window_dimensions()

    pygame.display.set_caption(f"Minesweeper ({cfg.COLUMNS}x{cfg.ROWS}, {cfg.NUM_MINES} mines)")
    screen = pygame.display.set_mode((cfg.WINDOW_WIDTH, cfg.WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    def reset():
        mine_grid_local = create_mine_grid(cfg.ROWS, cfg.COLUMNS, cfg.NUM_MINES)
        adjacency_local = calc_adjacency(mine_grid_local)
        revealed_local = [[False for _ in range(cfg.COLUMNS)] for _ in range(cfg.ROWS)]
        flagged_local = [[False for _ in range(cfg.COLUMNS)] for _ in range(cfg.ROWS)]
        game_state_local = "running"
        remaining_safe_local = cfg.ROWS * cfg.COLUMNS - cfg.NUM_MINES
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

    (
        mine_grid,
        adjacency_grid,
        revealed,
        flagged,
        game_state,
        remaining_safe,
        is_first_click,
        start_ticks,
        end_ticks,
    ) = reset()

    while True:
        clock.tick(cfg.FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                log_event("QUIT event received")
                # Ask for confirmation
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
                    draw_board(
                        screen,
                        font,
                        mine_grid,
                        adjacency_grid,
                        revealed,
                        flagged,
                        game_state,
                        remaining_safe,
                        0,
                    )
                    draw_quit_confirm(screen, font)
                    pygame.display.flip()
                    clock.tick(30)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                log_event("Key R pressed: reset")
                (
                    mine_grid,
                    adjacency_grid,
                    revealed,
                    flagged,
                    game_state,
                    remaining_safe,
                    is_first_click,
                    start_ticks,
                    end_ticks,
                ) = reset()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                log_event("Key M pressed: open menu")
                menu_result = run_menu(cfg.ROWS, cfg.COLUMNS, cfg.NUM_MINES, cfg.TILE_SIZE)
                if menu_result is None:
                    log_event("Menu returned None (Quit)")
                    pygame.quit()
                    return
                cfg.ROWS, cfg.COLUMNS, cfg.NUM_MINES, cfg.TILE_SIZE = menu_result
                cfg.WINDOW_WIDTH, cfg.WINDOW_HEIGHT = cfg.compute_window_dimensions()
                screen = pygame.display.set_mode((cfg.WINDOW_WIDTH, cfg.WINDOW_HEIGHT))
                pygame.display.set_caption(
                    f"Minesweeper ({cfg.COLUMNS}x{cfg.ROWS}, {cfg.NUM_MINES} mines)"
                )
                (
                    mine_grid,
                    adjacency_grid,
                    revealed,
                    flagged,
                    game_state,
                    remaining_safe,
                    is_first_click,
                    start_ticks,
                    end_ticks,
                ) = reset()
            if game_state == "running" and event.type == pygame.MOUSEBUTTONDOWN:
                cell = pixel_to_cell(*event.pos)
                if cell is None:
                    continue
                r, c = cell
                log_event(f"Mouse button {event.button} on cell ({r},{c})")
                if event.button == 2:
                    hit_mine, opened = chord_reveal(
                        r, c, mine_grid, adjacency_grid, revealed, flagged
                    )
                    if opened > 0 and start_ticks is None:
                        start_ticks = pygame.time.get_ticks()
                    if hit_mine:
                        game_state = "lost"
                        if start_ticks is not None and end_ticks is None:
                            end_ticks = pygame.time.get_ticks()
                        for rr in range(cfg.ROWS):
                            for cc in range(cfg.COLUMNS):
                                if mine_grid[rr][cc]:
                                    revealed[rr][cc] = True
                    else:
                        remaining_safe -= opened
                        if remaining_safe == 0:
                            game_state = "won"
                            if start_ticks is not None and end_ticks is None:
                                end_ticks = pygame.time.get_ticks()
                elif event.button == 1:
                    pressed = pygame.mouse.get_pressed(3)
                    if pressed[2] and revealed[r][c] and adjacency_grid[r][c] > 0:
                        hit_mine, opened = chord_reveal(
                            r, c, mine_grid, adjacency_grid, revealed, flagged
                        )
                        if opened > 0 and start_ticks is None:
                            start_ticks = pygame.time.get_ticks()
                        if hit_mine:
                            game_state = "lost"
                            if start_ticks is not None and end_ticks is None:
                                end_ticks = pygame.time.get_ticks()
                            for rr in range(cfg.ROWS):
                                for cc in range(cfg.COLUMNS):
                                    if mine_grid[rr][cc]:
                                        revealed[rr][cc] = True
                        else:
                            remaining_safe -= opened
                            if remaining_safe == 0:
                                game_state = "won"
                                if start_ticks is not None and end_ticks is None:
                                    end_ticks = pygame.time.get_ticks()
                        continue
                    if is_first_click and not revealed[r][c]:
                        is_first_click = False
                        mine_grid = create_mine_grid(
                            cfg.ROWS, cfg.COLUMNS, cfg.NUM_MINES, exclude={(r, c)}
                        )
                        adjacency_grid = calc_adjacency(mine_grid)
                        if start_ticks is None:
                            start_ticks = pygame.time.get_ticks()
                    elif start_ticks is None and not revealed[r][c]:
                        start_ticks = pygame.time.get_ticks()

                    hit_mine, opened = reveal_cell(
                        r, c, mine_grid, adjacency_grid, revealed, flagged
                    )
                    if hit_mine:
                        game_state = "lost"
                        if start_ticks is not None and end_ticks is None:
                            end_ticks = pygame.time.get_ticks()
                        for rr in range(cfg.ROWS):
                            for cc in range(cfg.COLUMNS):
                                if mine_grid[rr][cc]:
                                    revealed[rr][cc] = True
                    else:
                        remaining_safe -= opened
                        if remaining_safe == 0:
                            game_state = "won"
                            if start_ticks is not None and end_ticks is None:
                                end_ticks = pygame.time.get_ticks()
                elif event.button == 3:
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

        draw_board(
            screen,
            font,
            mine_grid,
            adjacency_grid,
            revealed,
            flagged,
            game_state,
            remaining_safe,
            elapsed_seconds,
        )
        pygame.display.flip()


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:
        summary = log_exception_to_file(exc)
        show_error_screen(str(exc))
