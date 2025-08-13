# Minesweeper (Python + Pygame)

A compact Minesweeper built with Python and Pygame, featuring a setup menu, first-click safety, chording, and configurable grid sizes.

## Features

- **Configurable grid**: Choose rows, columns, mines, and tile size from an in-game setup menu.
- **Presets**: Beginner (9x9, 10), Intermediate (16x16, 40), Expert (16x30, 99).
- **First-click safety**: Your first reveal is guaranteed not to hit a mine.
- **Chording**: Middle-click, or press left+right on a revealed number, to auto-open neighbors when flags match the number.
- **Status and timer**: Shows remaining mines, elapsed time, and remaining safe tiles.
- **Quit confirmation**: Closing the window prompts for confirmation.
- **Debug logging**: Optional runtime log to `run.log` with `--debug`.
- **Error handling**: Unhandled errors are logged to `error.log` and a simple error screen is shown.
- **Default configuration**: 6 columns × 8 rows with 7 mines and 48px tiles (overridable via menu/CLI).

## Getting Started

### 1) Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Run the game

```bash
python main.py
```

- If you launch with default settings, the setup menu opens first. Start from presets or fine-tune rows, cols, mines, and tile size.
- If you pass CLI options (see below), the game starts directly with those values.

## Command-line options

```bash
python main.py \
  --rows 16 \
  --cols 16 \
  --mines 40 \
  --tile-size 48 \
  --debug
```

- `--rows`: Number of rows (min 6, max 16)
- `--cols`: Number of columns (min 6, max 20)
- `--mines`: Number of mines (clamped to at most rows*cols - 1)
- `--tile-size`: Tile size in pixels (>= 12; menu allows 16–96)
- `--debug`: Enable logging to `run.log`

Values are clamped to supported ranges by the game.

## Controls

- **Left mouse button**: Reveal tile
- **Right mouse button**: Toggle flag (flags are shown as watermelons)
- **Middle click or Left+Right**: Chord on a revealed number to open neighbors when flagged count matches
- **R**: Restart current configuration
- **M**: Open setup menu (reconfigure grid/mines/tile size)
- **Y / N / Esc**: Respond to quit confirmation when closing the window

## Project structure

- `main.py`: Game entry point and logic (rendering, input, board state)
- `requirements.txt`: Python dependencies
- Logs: `run.log` (when `--debug`), `error.log` (created on unhandled errors)
- `README.md`: This file

## Notes

- The setup menu appears on startup when you use default CLI values. Providing any CLI option skips the initial menu and starts immediately.
- In headless environments (e.g., CI), Pygame may require a dummy video driver.
