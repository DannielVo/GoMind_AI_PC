# GoMind AI – Go Game with Minimax & Alpha-Beta Pruning

## 1. Project Overview

**GoMind AI** is a Python desktop application for playing **9×9 Go**, built with **Pygame**. It supports **Player vs Player** and **Player vs AI** modes. The AI uses depth-limited **Minimax Search with Alpha-Beta Pruning** and a custom heuristic evaluation function to select moves.

The project separates Go rules and game state management, AI decision-making, and the graphical interface into independent modules. Its interactive UI includes board themes, game controls, visual feedback, sound effects, and a bilingual rules guide.

## 2. Demo

**Gameplay video:** [Add demo video link]

## 3. Project Highlights

- **Custom Go engine:** Implements stone placement, connected groups and liberties, captures, suicide prevention, and a simple Ko check.
- **Adversarial-search AI:** Combines Minimax, Alpha-Beta Pruning, heuristic board evaluation, and prioritized candidate moves.
- **Game-state history:** Stores snapshots to support Undo and Redo.
- **Modular design:** Separates `core/` game rules, `bots/` AI logic, and `ui/` Pygame screens.
- **Interactive desktop experience:** Provides two board styles, move previews, last-move highlighting, animations, sound effects, and a bilingual guide.

## 4. Tech Stack

- **Language:** Python
- **Desktop UI / Graphics:** Pygame (pygame-ce)
- **Architecture:** Object-Oriented Programming (OOP), modular Python packages
- **Standard library:** `enum`, `dataclasses`, `math`, `random`, and other built-in modules

## 5. Key Features

### Game Modes and Setup

- **Player vs Player:** Two people take turns placing stones on the same board.
- **Player vs AI:** Play against the heuristic Minimax bot.
- **9×9 board:** Fixed board size in the current setup screen.
- **Stone color selection:** Choose Black or White in Player vs AI mode. Black moves first, so the AI opens when the human chooses White.
- **Board styles:** Choose **Ironwood** or **Marble Stone**, with a preview in Game Setup. The game falls back to a drawn board if a board image cannot be loaded.

### Go Rules and Gameplay

- Place stones on empty intersections and alternate turns, starting with Black.
- Capture opposing groups when they have no remaining liberties.
- Prevent suicidal moves and immediate board-position repetition through a simple Ko check.
- **Pass** a turn or **Resign** from a game; two consecutive passes end the game.
- Use **Undo** and **Redo** to navigate saved game states one snapshot at a time.
- Calculate a final score from enclosed empty territory, captured stones, and **6.5 komi for White**.
- View the game result in an overlay showing the winner and final scores.

### Interface and Controls

- Click an intersection to place a stone; preview a translucent **ghost stone** while hovering over an empty intersection.
- See the latest move highlighted and view the current turn, capture counts, hovered coordinate, and last move in the side panel.
- Use **Undo**, **Redo**, **Pass**, **Resign**, and **Back** buttons. Keyboard shortcuts: **P** for Pass and **R** for Resign.
- Enjoy background music controls, move/click sound effects, and a game-end sound effect when the corresponding audio assets are available.
- Explore an animated Home Screen with a parallax background and interactive floating stones.
- Read a scrollable **Go rules guide in Vietnamese or English**, with a collapsible panel.

> **Scoring scope:** Territory is determined from empty regions bordered by one color. The current implementation does not perform full dead-stone adjudication or handle complex situations such as seki.

## 6. AI Algorithms

### Minimax Search with Alpha-Beta Pruning

The `HeuristicMinimaxBot` explores candidate moves by simulating future board positions. It uses **Minimax** to maximize its own evaluation score while assuming the opponent chooses moves that minimize that score. **Alpha-Beta Pruning** skips branches that cannot improve the current decision.

- **Default search depth:** `2` (configurable in code).
- **Move ordering:** Prioritizes tactical opportunities involving opposing groups with few liberties, with a small center preference.
- **Candidate limit:** Considers at most **15 generated candidate moves per search node** to control search cost.
- **Tie-breaking:** Randomly chooses among equally rated best moves.
- **Resignation threshold:** The bot can return `RESIGN` when its best evaluated score is below the configured threshold (`-30.0`).

### Custom Heuristic Evaluation

The evaluation combines four components:

```text
score = 1.5 × stone_difference
      + 0.6 × approximate_territory_difference
      + capture_opportunity_bonus
      - vulnerable_group_penalty
```

- **Stone difference:** Compares the number of stones on the board.
- **Approximate territory:** Counts empty intersections adjacent to stones of only one color as a local territory estimate.
- **Capture opportunity bonus:** Rewards positions where an opponent group has only one liberty.
- **Vulnerable group penalty:** Penalizes positions where one of the bot's groups has only one liberty.

This heuristic is a lightweight estimate for search, **not** the same as the final territory-scoring procedure. The bot uses a restricted set of candidate moves rather than searching every possible Go continuation.

## 7. Project Structure

```text
GoMind_AI_PC/
├── assets/                  # Board images, backgrounds, and audio assets
├── bots/
│   └── minimax_bot.py       # Minimax, Alpha-Beta Pruning, heuristic evaluation
├── core/
│   ├── board.py             # Board state, groups, liberties, captures
│   └── game.py              # Turns, game modes, Ko, history, scoring
├── ui/
│   ├── game_screen.py       # Gameplay board, controls, and result overlay
│   ├── guide_screen.py      # Bilingual rules guide
│   ├── home_screen.py       # Animated home screen
│   ├── setup_screen.py      # Mode, color, and board-style selection
│   └── widgets.py           # Reusable Button and OptionButton components
├── __init__.py
├── .gitignore
├── config.py                # Display settings, FPS, and colors
├── main.py                  # Application entry point and Pygame event loop
└── README.md
```

## 8. Getting Started

### Prerequisites

- Python **3.10+ recommended**
- A desktop environment capable of opening a Pygame window

### Install dependencies

From the project directory, install Pygame CE:

```bash
python -m pip install pygame-ce
```

### Run the application

```bash
python main.py
```

The application opens on the **Home Screen**. Select **Start** to configure a game, **Guide** to read the rules, or **Quit** to exit.

> **Assets:** Keep the repository's `assets/` directory alongside the source files. Some backgrounds and board previews require their image files; audio effects are used when their files can be loaded.

## 9. Current Development

**GoMind AI Web** is an ongoing effort to bring the desktop Go game to the browser while reusing and improving the Python game engine and AI logic.

- **Frontend:** Next.js, TypeScript, Tailwind CSS — [link fe]
- **Backend:** FastAPI, Python — [link be]
- **Planned engine work:** Improve legal-move handling during AI search, heuristic evaluation, search performance, and automated tests.

The web application is **in development**; the features documented above describe the current Python desktop implementation.
