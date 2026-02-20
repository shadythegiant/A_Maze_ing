_This project has been created as part of the 42 curriculum by abendrio, zahidi._

# A-Maze-ing

## Description

A-Maze-ing is a highly robust Python-based maze generator, solver, and visualizer. The project's purpose is to demonstrate algorithmic problem-solving, strict Python typing, and terminal-based UI design. It generates both perfect and imperfect mazes, automatically embeds a custom "42" pattern into the walls, visualizes the generation and solving processes in a rich Textual User Interface (TUI), and exports the final grid data into a custom HEX output format.

Key Features:

- **Dual-Algorithm Generation:** Supports both Recursive Backtracker (DFS) and Prim's algorithm.
- **Pathfinding Solver:** Optimized breadth-first search logic to find and animate the shortest path from entry to exit.
- **Interactive TUI:** Built with the `Textual` library, featuring live generation animations, solution snake animations, and dynamic color toggling.
- **Strict Code Quality:** 100% compliant with PEP 8 (`flake8`) and strictly type-hinted (`mypy`).

---

## Instructions

### Prerequisites

- Python 3.10 or higher.
- `make` installed on your system.

### Installation & Execution

This project uses a `Makefile` to simplify the environment setup, packaging, and execution.

1. **Install and Build the Package:**

```bash
make install

```

_This command upgrades pip, builds the project as a `.tar.gz` Source Distribution, installs the required dependencies (`textual`, `flake8`, `mypy`), and installs the `mazegen` package in editable mode._ 2. **Run the Application:**

```bash
make run

```

_This executes the main program using the default `config.txt` file._ 3. **Code Quality Checks:**

```bash
make lint

```

_Runs `flake8` for style checking and `mypy` for strict static type checking._ 4. **Clean Workspace:**

```bash
make clean
make fclean

```

_Removes temporary build files, `.egg-info`, `__pycache__`, and the virtual environment._

### TUI Key Bindings

Once the application is running, use the following keys to interact:

- `r`: Regenerate the maze instantly.
- `a`: Animate the maze generation process.
- `s`: Show/Hide the solution path.
- `v`: Animate the solution pathfinding snake.
- `g`: Cycle between generation algorithms (DFS / Prims).
- `c`: Change the maze wall color.
- `p`: Change the "42" pattern color.
- `q`: Quit the application.

---

## Configuration File Structure

The project is driven by a case-insensitive `.txt` configuration file. The config parser is highly robust, ignoring comments `#` and handling variable spacing.

**Example `config.txt`:**

```ini
# Maze Dimensions (Minimum 3x3)
WIDTH=20
HEIGHT=10

# Entry and Exit Coordinates (Must be on the border/edges)
ENTRY=0,0
EXIT=19,9

# Boolean flag: True for perfect mazes, False to create loops
PERFECT=True

# Output file for the HEX dump
OUTPUT_FILE=output.txt

# Optional seed for reproducible mazes
SEED=42

```

---

## The Chosen Maze Algorithm & Reasoning

### Algorithm: Recursive Backtracker (Depth-First Search - DFS)

While the engine supports Prim's Algorithm as an alternative, **DFS** is our primary chosen algorithm.

### Reason for choosing DFS:

We chose DFS because it generates mazes with a high "river" factor—meaning it creates long, winding, and complex dead-ends. This makes the maze significantly more aesthetically pleasing and challenging for a human to solve visually compared to Prim's algorithm, which tends to create highly branched, short, and somewhat "spongy" dead-ends. DFS is also highly memory-efficient when implemented iteratively with a stack, ensuring our generator scales well for larger grid sizes without hitting recursion limits.

---

## Maze Generator Reusable Module (`mazegen`)

The `mazegen` directory is built as a fully standalone, reusable Python package. It handles all grid mathematics via bitmasking (using integers `1`, `2`, `4`, `8` to represent N, E, S, W walls) and separates the logic entirely from the visualization layer.

**How to use it in other projects:**

```python
from mazegen.generator import MazeGenerator
from mazegen.solver import solve, solve_to_coords

# 1. Initialize a 20x20 maze
generator = MazeGenerator(width=20, height=20, seed=None)

# 2. Generate using DFS
generator.generate(algo="DFS", perfect=True)

# 3. Set standard border entry/exit
generator.set_entry_exit(entry=(0, 0), exit=(19, 19))

# 4. Fetch the 2D bitmask grid
grid = generator.get_grid()

# 5. Solve it
solution_string = solve(grid, start=(0,0), end=(19,19))
# Returns "SSENE..." or "no path found"

```

---

## Team and Project Management

### Team Roles

- **azahidi:** Responsible for architecture design, configuration parsing (`config/loader.py`), robust error handling, and terminal interface integration/styling.
- **abendrio:** Responsible for the core mathematical algorithms (DFS/Prim's generation), the maze solver pathfinding logic, bitmask implementation, and the custom HEX output formatting.

### Anticipated Planning vs. Evolution

Initially, we planned to build a simple ASCII script that printed to the standard terminal. However, as the core generation logic (`mazegen`) was completed ahead of schedule, we pivoted to using the `Textual` library to create an interactive TUI. This required us to heavily refactor the generator to record a "history" of wall removals so that we could animate the process frame-by-frame in the UI.

### What Worked Well & What Could Be Improved

- **Worked Well:** Splitting the project into strictly typed, modular components (`config`, `mazegen`, `visuals`) allowed us to work in parallel without merge conflicts. Using a bitmask approach for the grid made the solver incredibly fast.
- **Could Be Improved:** The animation logic tightly couples the TUI timer with the generator's history list. In the future, implementing an asynchronous generator or an Event/Observer pattern would decouple the UI from the engine more cleanly.

### Tools Used

- **Make:** For automating the build, installation, and testing pipeline.
- **Mypy:** Enforced strict static typing, catching `NoneType` errors and assignment bugs early in development.
- **Flake8 / Autopep8:** Ensured strict adherence to PEP 8 styling conventions.
- **Textual / Rich:** Used for rendering the interactive terminal UI, handling keyboard events, and applying dynamic regex-based syntax highlighting to ASCII strings.
- **Build / Pip:** Used to package the module as a standard `sdist` (`.tar.gz`).

---

## Resources

- **Textual Documentation:** Used extensively to understand App composing, CSS styling, and handling `set_interval` timers for our generation and solving animations.
- **Python `typing` Module Docs:** Essential for understanding complex generic types (`Set`, `Tuple`, `Optional`, `Dict`) required to pass strict `mypy` checks without throwing implicit optional errors.
- **Ahmed Hashim's YouTube Channel:** Referenced for clear visual explanations of how Prim's and DFS algorithms operate on a grid, which helped us translate the theory into our Python implementation.
- **Python `random` Module:** Used for seeded random number generation to ensure reproducible mazes during grading.
