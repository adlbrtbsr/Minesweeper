from __future__ import annotations

import pygame

from . import config as cfg


def pixel_to_cell(x: int, y: int) -> tuple[int, int] | None:
    # Adjust for margins and status bar
    grid_top = cfg.V_PADDING + cfg.STATUS_BAR_HEIGHT
    if y < grid_top:
        return None

    grid_x = x - cfg.H_PADDING
    grid_y = y - grid_top

    if grid_x < 0 or grid_y < 0:
        return None

    c = grid_x // cfg.TILE_SIZE
    r = grid_y // cfg.TILE_SIZE

    if 0 <= r < cfg.ROWS and 0 <= c < cfg.COLUMNS:
        return (r, c)
    return None


def draw_bomb_icon(screen: pygame.Surface, rect: pygame.Rect) -> None:
    radius = max(6, min(rect.width, rect.height) // 3)
    center_x, center_y = rect.center
    # Body
    pygame.draw.circle(screen, (25, 25, 25), (center_x, center_y), radius)
    # Highlight
    highlight_radius = max(2, radius // 3)
    pygame.draw.circle(
        screen,
        (80, 80, 80),
        (center_x - radius // 3, center_y - radius // 3),
        highlight_radius,
    )
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
    pygame.draw.line(
        screen, (170, 140, 100), fuse_start, fuse_end, width=max(2, radius // 6)
    )
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
    pygame.draw.circle(
        screen, (140, 210, 140), (center_x, center_y), radius - rind_thickness
    )
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


def draw_board(
    screen: pygame.Surface,
    font: pygame.font.Font,
    mine_grid,
    adjacency_grid,
    revealed,
    flagged,
    game_state: str,
    remaining_safe: int,
    elapsed_seconds: int,
) -> None:
    screen.fill(cfg.COLOR_BG)

    # Status text
    if game_state == "running":
        # Remaining mines: total mines minus placed flags
        flags_placed = sum(
            1 for r in range(cfg.ROWS) for c in range(cfg.COLUMNS) if flagged[r][c]
        )
        remaining_mines = max(0, cfg.NUM_MINES - flags_placed)
        status_text = (
            f"Mines: {remaining_mines}    L: reveal   R: flag   Mid: chord   M: menu"
        )
    else:
        status_text = "L: reveal   R: flag"
    if game_state == "lost":
        status_text = "You hit a mine. Press R to restart, M for menu."
    elif game_state == "won":
        status_text = "You won! Press R to restart, M for menu."

    # Render status text with dynamic downscaling to fit narrow windows
    available_width = max(
        50, (cfg.WINDOW_WIDTH or screen.get_width()) - 2 * cfg.H_PADDING
    )
    status_font = pygame.font.SysFont(None, cfg.STATUS_FONT_BASE)
    status_surface = status_font.render(status_text, True, cfg.COLOR_STATUS)
    if status_surface.get_width() > available_width:
        # Estimate a smaller size based on width ratio
        base_size = max(12, status_font.get_height())
        target_size = max(
            16, int(base_size * available_width / max(1, status_surface.get_width()))
        )
        # Re-render with a smaller font
        status_font = pygame.font.SysFont(None, target_size)
        status_surface = status_font.render(status_text, True, cfg.COLOR_STATUS)
    screen.blit(status_surface, (cfg.H_PADDING, cfg.V_PADDING))

    grid_top = cfg.V_PADDING + cfg.STATUS_BAR_HEIGHT
    for r in range(cfg.ROWS):
        for c in range(cfg.COLUMNS):
            rect = pygame.Rect(
                cfg.H_PADDING + c * cfg.TILE_SIZE,
                grid_top + r * cfg.TILE_SIZE,
                cfg.TILE_SIZE - cfg.GRID_LINE,
                cfg.TILE_SIZE - cfg.GRID_LINE,
            )

            if revealed[r][c]:
                if mine_grid[r][c]:
                    pygame.draw.rect(screen, cfg.COLOR_TILE_MINE, rect)
                    draw_bomb_icon(screen, rect)
                else:
                    pygame.draw.rect(screen, cfg.COLOR_TILE_REVEALED, rect)
                    adj = adjacency_grid[r][c]
                    if adj > 0:
                        color = cfg.NUMBER_COLORS.get(adj, cfg.COLOR_TEXT)
                        text_surface = font.render(str(adj), True, color)
                        text_rect = text_surface.get_rect(center=rect.center)
                        screen.blit(text_surface, text_rect)
            else:
                pygame.draw.rect(screen, cfg.COLOR_TILE_HIDDEN, rect)
                if flagged[r][c]:
                    draw_watermelon_icon(screen, rect)

    # Border around grid
    grid_rect = pygame.Rect(
        cfg.H_PADDING, grid_top, cfg.COLUMNS * cfg.TILE_SIZE, cfg.ROWS * cfg.TILE_SIZE
    )
    pygame.draw.rect(screen, cfg.COLOR_GRID, grid_rect, width=2)

    # Footer info
    def format_time(total_seconds: int) -> str:
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:02d}"

    footer_text = f"Time: {format_time(elapsed_seconds)}    Safe: {remaining_safe}"
    if game_state == "won":
        footer_color = cfg.COLOR_WIN
    elif game_state == "lost":
        footer_color = cfg.COLOR_LOSE
    else:
        footer_color = cfg.COLOR_STATUS
    footer_surface = font.render(footer_text, True, footer_color)
    footer_y = (cfg.WINDOW_HEIGHT or screen.get_height()) - cfg.V_PADDING - cfg.FOOTER_BAR_HEIGHT + 6
    screen.blit(footer_surface, (cfg.H_PADDING, footer_y))
