from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from .ascii_renderer import ASCIIVisualizer
from rich.text import Text
from mazegen.solver import solve, solve_to_coords
from typing import Any, Tuple, List, Set, Optional


class MazeApp(App):
    CSS = """
    Screen {
        overflow: auto;
        align: center middle;
        background: #111;
    }
    .maze {
        width: auto;
        height: auto;
        border: heavy white;
        background: #000;
        color: #44cc44;
        padding: 1 2;
        text-wrap: nowrap;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "regenerate", "Regenerate"),
        ("c", "toggle_color", "Change Color"),
        ("p", "toggle_42_color", "Change 42 Color"),
        ("a", "animate_gen", "Animate Gen"),
        ("s", "toggle_solve", "Show/Hide Path"),
        ("v", "animate_solve", "Animate Solution"),
        ("g", "cycle_algo", "Switch Algo")
    ]

    COLORS = [
        "#44cc44",  # Green
        "#00ffff",  # Cyan
        "#ff0055",  # Red
        "#aa00ff",  # Purple
        "#ffff00",  # Yellow
        "#ffffff",  # White
    ]
    # 42 pattern colors:
    PATTERN_COLORS = [
        "#FFD700",
        "#FF0000",
        "#5B5B5D",
        "#FF00FF",
        "#00FF00",
        "#FFFFFF",
        "#FF1493",
    ]

    def __init__(
        self,
        generator: Any,
        entry: Tuple[int, int],
        exit_point: Tuple[int, int],
        is_perfect: bool = True
    ) -> None:
        super().__init__()
        self.generator = generator
        self.entry = entry
        self.exit_point = exit_point
        self.visualizer = ASCIIVisualizer()
        self.current_color_index = 0
        self.current_pattern_index = 0
        self.is_perfect = is_perfect
        self.animation_mode: Optional[str] = None   # 'GEN' or 'SOLVE'
        # Stores the full snake to draw
        self.full_solution_list: List[Tuple[int, int]] = []

        # Animation State
        self.timer: Optional[Any] = None
        self.display_grid: List[List[int]] = []
        self.step_index = 0

        # Solver State
        self.show_path = False
        self.solution_coords: Set[Tuple[int, int]] = set()

        # ALGO STATE
        # We get the list of keys ["DFS", "Prims"] from the generator
        self.available_algos = list(self.generator.algos.keys())
        self.current_algo_index = 0
        self.current_algo_name = self.available_algos[0]

    def compose(self) -> ComposeResult:
        yield Header()

        # Initial Generation
        self.generator.generate(
            algo=self.current_algo_name, perfect=self.is_perfect)
        self.generator.set_entry_exit(self.entry, self.exit_point)

        if self.generator.pattern_42_failed:
            self.notify("Warning: Maze too small for '42' pattern!",
                        severity="warning", timeout=5)

        # Sync grid
        grid = self.generator.get_grid()
        self.display_grid = [row[:] for row in grid]

        # Initial Render Placeholder
        yield Static("", classes="maze", id="maze_display")
        yield Footer()

    def on_mount(self) -> None:
        """Called immediately after compose to draw the first frame."""
        self._refresh_maze_view()
        self._update_title()

    def _refresh_maze_view(self) -> None:
        """
        The Master Render Function.
        Draws the maze based on current grid, color, and path settings.
        """
        # Decide if we pass the path or empty set
        path_to_draw = self.solution_coords if self.show_path else set()

        maze_str = self.visualizer.render_thick(
            self.display_grid,
            self.generator.pattern_42_coords,
            solution_path=path_to_draw,
            entry=self.entry,
            exit=self.exit_point
        )

        current_color = self.COLORS[self.current_color_index]
        pattern_color = self.PATTERN_COLORS[self.current_pattern_index]
        styled_maze = Text(maze_str, style=current_color)

        # Highlights
        styled_maze.highlight_regex(
            r"▒+", f"bold {pattern_color}")  # 42 Pattern
        styled_maze.highlight_regex(r"●", "bold #00BFFF")  # Entry
        styled_maze.highlight_regex(r"◉", "bold #FF4500")  # Exit

        # Highlight Path Dots (Bright White)
        if self.show_path:
            styled_maze.highlight_regex(r"▓", "bold #00ffff")

        # Update the widget
        try:
            self.query_one("#maze_display", Static).update(styled_maze)
        except Exception:
            pass  # Safety for initial load

    def action_regenerate(self) -> None:
        """Instant regeneration."""
        self.generator.generate(
            algo=self.current_algo_name, perfect=self.is_perfect)
        self.generator.set_entry_exit(self.entry, self.exit_point)

        if self.generator.pattern_42_failed:
            self.notify("Warning: Maze too small for '42' pattern!",
                        severity="warning")

        # Reset Grid & Solver
        grid = self.generator.get_grid()
        self.display_grid = [row[:] for row in grid]
        self.show_path = False
        self.solution_coords = set()

        self._refresh_maze_view()

    def action_toggle_color(self) -> None:
        """Cycle colors."""
        self.current_color_index = (
            self.current_color_index + 1) % len(self.COLORS)
        self._refresh_maze_view()

    def action_toggle_solve(self) -> None:
        """Show/Hide the solution path."""
        self.show_path = not self.show_path

        # If turning ON and missing coords, calculate them
        if self.show_path and not self.solution_coords:
            grid = self.generator.get_grid()
            path_str = solve(grid, self.entry, self.exit_point)

            if path_str == "no path found" or not path_str:
                self.notify("No solution found!", severity="error")
                self.show_path = False
            else:
                self._trace_path_coords(path_str)

        self._refresh_maze_view()

    def _trace_path_coords(self, path_str: str) -> None:
        """Converts 'SSENE...' string to coordinate set."""
        curr_x, curr_y = self.entry
        self.solution_coords = {(curr_x, curr_y)}

        moves = {'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0)}

        for char in path_str:
            if char in moves:
                dx, dy = moves[char]
                curr_x += dx
                curr_y += dy
                self.solution_coords.add((curr_x, curr_y))

    def action_animate_gen(self) -> None:
        """Starts animation."""
        if self.timer is not None:
            self.timer.stop()

        self.animation_mode = 'GEN'
        self.generator.generate(
            algo=self.current_algo_name, perfect=self.is_perfect)
        self.generator.set_entry_exit(self.entry, self.exit_point)

        # Reset Display to Walls
        w, h = self.generator.width, self.generator.height
        self.display_grid = [[15 for _ in range(w)] for _ in range(h)]
        self.step_index = 0

        # Hide path during animation
        self.show_path = False

        self.solution_coords = set()

        self.timer = self.set_interval(0.01, self.on_timer_tick)

    def action_animate_solve(self) -> None:
        """Starts SOLUTION SNAKE animation."""
        if self.timer is not None:
            self.timer.stop()

        # 1. Solve instantly to get the full path list
        grid = self.generator.get_grid()
        full_path = solve_to_coords(grid, self.entry, self.exit_point)

        if not full_path:
            self.notify("No path found!", severity="error")
            return

        # 2. Setup Animation State
        self.animation_mode = 'SOLVE'
        self.full_solution_list = full_path  # The list of coords to reveal
        self.step_index = 0

        # 3. Prepare Visuals
        self.show_path = True
        self.solution_coords = set()  # Start empty

        # 4. Start Timer
        self.timer = self.set_interval(0.01, self.on_timer_tick)

    def on_timer_tick(self) -> None:
        """Handles both Generation and Solution animations."""

        # --- CASE 1: Animating Maze Generation ---
        if self.animation_mode == 'GEN':
            history = self.generator.history
            if self.step_index >= len(history):
                if self.timer is not None:
                    self.timer.stop()
                self.animation_mode = None
                return

            updates = history[self.step_index]
            for (x, y, new_value) in updates:
                self.display_grid[y][x] = new_value
            self.step_index += 1

        # --- CASE 2: Animating Solution Snake ---
        elif self.animation_mode == 'SOLVE':
            if self.step_index >= len(self.full_solution_list):
                if self.timer is not None:
                    self.timer.stop()
                self.animation_mode = None
                return

            # Add ONE block to the path
            next_coord = self.full_solution_list[self.step_index]
            self.solution_coords.add(next_coord)
            self.step_index += 1

        # Update Screen
        self._refresh_maze_view()

    def _update_title(self) -> None:
        """Optional: Update window title to show current algo"""
        self.title = f"A-Maze-Ing | Algo: {self.current_algo_name}"

    def action_cycle_algo(self) -> None:
        """Switch between DFS, Prims, etc."""
        # 1. Cycle Index
        self.current_algo_index = (
            self.current_algo_index + 1) % len(self.available_algos)
        self.current_algo_name = self.available_algos[self.current_algo_index]

        # 2. Notify User
        self.notify(f"Switched Algorithm to: {self.current_algo_name}")
        self._update_title()

        # 3. Trigger Regenerate to show the new result immediately
        self.action_regenerate()

    def action_toggle_42_color(self) -> None:
        """Cycle colors for the 42 pattern."""
        self.current_pattern_index = (
            self.current_pattern_index + 1) % len(self.PATTERN_COLORS)
        self._refresh_maze_view()
