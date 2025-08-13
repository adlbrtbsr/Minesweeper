from __future__ import annotations

import sys
import traceback
from datetime import datetime

import pygame

from . import config as cfg


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
    if not cfg.DEBUG:
        return
    try:
        timestamp = datetime.now().strftime("%H:%M:%S")
        with open("run.log", "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass
