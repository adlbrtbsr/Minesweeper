from __future__ import annotations

import pygame

from . import config as cfg


def get_quit_confirm_rects() -> tuple[pygame.Rect, pygame.Rect, pygame.Rect]:
    overlay_width = min(420, (cfg.WINDOW_WIDTH or 0) - 40)
    overlay_height = 150
    overlay_x = ((cfg.WINDOW_WIDTH or 0) - overlay_width) // 2
    overlay_y = ((cfg.WINDOW_HEIGHT or 0) - overlay_height) // 2
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
    dim = pygame.Surface(((cfg.WINDOW_WIDTH or 0), (cfg.WINDOW_HEIGHT or 0)), pygame.SRCALPHA)
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


def run_menu(
    initial_rows: int, initial_cols: int, initial_mines: int, initial_tile: int
) -> tuple[int, int, int, int] | None:
    menu_width = 520
    menu_height = 440
    pygame.display.set_caption("Minesweeper - Setup")
    screen = pygame.display.set_mode((menu_width, menu_height))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)

    rows = max(cfg.MIN_ROWS, min(cfg.MAX_ROWS, initial_rows))
    cols = max(cfg.MIN_COLS, min(cfg.MAX_COLS, initial_cols))
    mines = max(1, min(initial_mines, rows * cols - 1))
    tile = max(16, min(96, int(initial_tile)))

    def draw_button(rect: pygame.Rect, label: str, active: bool = True):
        color = (70, 70, 70) if active else (40, 40, 40)
        pygame.draw.rect(screen, color, rect, border_radius=6)
        text = font.render(label, True, (230, 230, 230))
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)

    while True:
        clock.tick(60)
        screen.fill(cfg.COLOR_BG)

        title = font.render("Choose grid and mines", True, cfg.COLOR_STATUS)
        screen.blit(title, (cfg.H_PADDING, cfg.V_PADDING))

        # Preset buttons
        preset_y = cfg.V_PADDING + 34
        preset_w, preset_h, preset_gap = 140, 36, 12
        beginner_rect = pygame.Rect(cfg.H_PADDING, preset_y, preset_w, preset_h)
        intermediate_rect = pygame.Rect(
            cfg.H_PADDING + (preset_w + preset_gap), preset_y, preset_w, preset_h
        )
        expert_rect = pygame.Rect(
            cfg.H_PADDING + 2 * (preset_w + preset_gap), preset_y, preset_w, preset_h
        )

        draw_button(beginner_rect, "Beginner")
        draw_button(intermediate_rect, "Intermediate")
        draw_button(expert_rect, "Expert")

        # Layout values and +/- buttons
        y0 = 100
        row_label = font.render(f"Rows: {rows}", True, cfg.COLOR_STATUS)
        col_label = font.render(f"Cols: {cols}", True, cfg.COLOR_STATUS)
        max_mines = max(1, rows * cols - 1)
        mines = min(mines, max_mines)
        mine_label = font.render(
            f"Mines: {mines} (max {max_mines})", True, cfg.COLOR_STATUS
        )
        tile_label = font.render(f"Tile size: {tile}px", True, cfg.COLOR_STATUS)

        screen.blit(row_label, (cfg.H_PADDING, y0))
        screen.blit(col_label, (cfg.H_PADDING, y0 + 50))
        screen.blit(mine_label, (cfg.H_PADDING, y0 + 100))
        screen.blit(tile_label, (cfg.H_PADDING, y0 + 150))

        btn_w, btn_h = 40, 36
        gap_x = 10
        base_x = 300

        rows_minus = pygame.Rect(base_x, y0 - 6, btn_w, btn_h)
        rows_plus = pygame.Rect(base_x + btn_w + gap_x, y0 - 6, btn_w, btn_h)
        cols_minus = pygame.Rect(base_x, y0 + 44, btn_w, btn_h)
        cols_plus = pygame.Rect(base_x + btn_w + gap_x, y0 + 44, btn_w, btn_h)
        mines_minus = pygame.Rect(base_x, y0 + 94, btn_w, btn_h)
        mines_plus = pygame.Rect(base_x + btn_w + gap_x, y0 + 94, btn_w, btn_h)
        tile_minus = pygame.Rect(base_x, y0 + 144, btn_w, btn_h)
        tile_plus = pygame.Rect(base_x + btn_w + gap_x, y0 + 144, btn_w, btn_h)

        draw_button(rows_minus, "-")
        draw_button(rows_plus, "+")
        draw_button(cols_minus, "-")
        draw_button(cols_plus, "+")
        draw_button(mines_minus, "-")
        draw_button(mines_plus, "+")
        draw_button(tile_minus, "-")
        draw_button(tile_plus, "+")

        start_rect = pygame.Rect(cfg.H_PADDING, menu_height - 70, 140, 42)
        quit_rect = pygame.Rect(cfg.H_PADDING + 160, menu_height - 70, 140, 42)
        draw_button(start_rect, "Start")
        draw_button(quit_rect, "Quit")

        hint = font.render("Tip: adjust mines after grid", True, (150, 150, 150))
        screen.blit(hint, (cfg.H_PADDING, menu_height - 120))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                # Preset selections
                if beginner_rect.collidepoint(mx, my):
                    rows, cols, mines = 9, 9, 10
                    rows = max(cfg.MIN_ROWS, min(cfg.MAX_ROWS, rows))
                    cols = max(cfg.MIN_COLS, min(cfg.MAX_COLS, cols))
                    mines = min(mines, max(1, rows * cols - 1))
                    continue
                elif intermediate_rect.collidepoint(mx, my):
                    rows, cols, mines = 16, 16, 40
                    rows = max(cfg.MIN_ROWS, min(cfg.MAX_ROWS, rows))
                    cols = max(cfg.MIN_COLS, min(cfg.MAX_COLS, cols))
                    mines = min(mines, max(1, rows * cols - 1))
                    continue
                elif expert_rect.collidepoint(mx, my):
                    rows, cols, mines = 16, 30, 99
                    rows = max(cfg.MIN_ROWS, min(cfg.MAX_ROWS, rows))
                    cols = max(cfg.MIN_COLS, min(cfg.MAX_COLS, cols))
                    mines = min(mines, max(1, rows * cols - 1))
                    continue
                if rows_minus.collidepoint(mx, my):
                    rows = max(cfg.MIN_ROWS, rows - 1)
                elif rows_plus.collidepoint(mx, my):
                    rows = min(cfg.MAX_ROWS, rows + 1)
                elif cols_minus.collidepoint(mx, my):
                    cols = max(cfg.MIN_COLS, cols - 1)
                elif cols_plus.collidepoint(mx, my):
                    cols = min(cfg.MAX_COLS, cols + 1)
                elif mines_minus.collidepoint(mx, my):
                    mines = max(1, mines - 1)
                elif mines_plus.collidepoint(mx, my):
                    mines = min(rows * cols - 1, mines + 1)
                elif tile_minus.collidepoint(mx, my):
                    tile = max(16, tile - 4)
                elif tile_plus.collidepoint(mx, my):
                    tile = min(96, tile + 4)
                elif start_rect.collidepoint(mx, my):
                    # Clamp before returning
                    rows = max(cfg.MIN_ROWS, min(cfg.MAX_ROWS, rows))
                    cols = max(cfg.MIN_COLS, min(cfg.MAX_COLS, cols))
                    mines = max(1, min(mines, rows * cols - 1))
                    return rows, cols, mines, tile
                elif quit_rect.collidepoint(mx, my):
                    return None
