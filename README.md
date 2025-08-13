# Minesweeper (Python + Pygame)

A minimal Minesweeper clone built with Python and Pygame.

## Features

- Fixed grid size: 6 columns x 8 rows
- 7 hidden mines
- Left-click to reveal tiles
- Right-click to place/remove flags
- Revealed tiles show the number of adjacent mines
- Auto-expands empty regions (0 adjacent mines)
- Win by revealing all non-mine tiles; lose on revealing a mine
- Press `R` to restart

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

## Controls

- Left mouse button: Reveal tile
- Right mouse button: Toggle flag
- `R`: Restart
- Window close button: Exit

## Project Structure

- `main.py`: Game entry point and all logic (rendering, input, board state)
- `requirements.txt`: Python dependencies
- `README.md`: This file

## Notes

- The grid and mine count are set in `main.py` via `ROWS`, `COLUMNS`, and `NUM_MINES`.
- Pygame uses the system display. If you run this headless (e.g., on CI), you may need a dummy video driver.
