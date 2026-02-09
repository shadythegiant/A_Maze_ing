from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from .ascii_renderer import ASCIIVisualizer
from rich.text import Text


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
        ("a", "animate_gen", "Animate Gen")
    ]

    COLORS = [
        "#44cc44",  # Green
        "#00ffff",  # Cyan
        "#ff0055",  # Red
        "#aa00ff",  # Purple
        "#ffff00",  # Yellow
        "#ffffff",  # White
    ]

    def __init__(self, generator, entry, exit_point, is_perfect=True):
        super().__init__()
        self.generator = generator
        self.entry = entry
        self.exit_point = exit_point
        self.visualizer = ASCIIVisualizer()
        self.current_color_index = 0
        self.is_perfect = is_perfect

        # Animation State
        self.timer = None
        self.display_grid = []
        self.step_index = 0

    def compose(self) -> ComposeResult:
        yield Header()

        # Initial Rendering
        self.generator.generate(perfect=self.is_perfect)
        self.generator.set_entry_exit(self.entry, self.exit_point)

        if self.generator.pattern_42_failed:
            self.notify("Warning: Maze too small for '42' pattern!",
                        severity="warning", timeout=5)

        grid = self.generator.get_grid()
        self.display_grid = [row[:] for row in grid]

        maze_str = self.visualizer.render_thick(
            grid,
            self.generator.pattern_42_coords,
            entry=self.entry,
            exit=self.exit_point
        )

        current_color = self.COLORS[self.current_color_index]
        styled_maze = Text(maze_str, style=current_color)
        styled_maze.highlight_regex(
            r"▒+", "bold #FFD700")  # Gold color for 42\
        styled_maze.highlight_regex(r"●", "bold #00BFFF")
        styled_maze.highlight_regex(r"◉", "bold #FF4500")
        yield Static(styled_maze, classes="maze", id="maze_display")

        yield Footer()

    def action_regenerate(self) -> None:
        """Instant regeneration (no animation)."""
        self.generator.generate(perfect=self.is_perfect)
        self.generator.set_entry_exit(self.entry, self.exit_point)

        if self.generator.pattern_42_failed:
            self.notify("Warning: Maze too small for '42' pattern!",
                        severity="warning", timeout=5)

        grid = self.generator.get_grid()
        self.display_grid = [row[:] for row in grid]  # Sync display grid

        new_maze_str = self.visualizer.render_thick(
            grid,
            self.generator.pattern_42_coords,
            entry=self.entry,
            exit=self.exit_point
        )

        # Apply current color
        current_color = self.COLORS[self.current_color_index]
        styled_maze = Text(new_maze_str, style=current_color)
        # 42 embeded pattern color
        styled_maze.highlight_regex(r"▒+", "bold #FFD700")
        # entry dot color
        styled_maze.highlight_regex(r"●", "bold #00BFFF")
        # exit dot color
        styled_maze.highlight_regex(r"◉", "bold #FF4500")
        self.query_one("#maze_display", Static).update(styled_maze)

    def action_toggle_color(self) -> None:
        """Called when user presses 'c'."""
        self.current_color_index = (
            self.current_color_index + 1) % len(self.COLORS)
        new_color = self.COLORS[self.current_color_index]
        self.notify(f"Color: {new_color}")
        if not self.display_grid:
            self.display_grid = self.generator.get_grid()

        raw_maze_str = self.visualizer.render_thick(
            self.display_grid,
            self.generator.pattern_42_coords,
            entry=self.entry,
            exit=self.exit_point
        )

        styled_maze = Text(raw_maze_str, style=new_color)
        styled_maze.highlight_regex(r"▒+", "bold #FFD700")
        styled_maze.highlight_regex(r"●", "bold #00BFFF")
        styled_maze.highlight_regex(r"◉", "bold #FF4500")

        self.query_one("#maze_display", Static).update(styled_maze)

    def action_animate_gen(self) -> None:
        """Starts the animation process."""
        self.notify("Starting Animation...")

        # 1. Stop any existing timer
        if self.timer:
            self.timer.stop()
        # 2. Reset the Generator (Calculate the full path instantly)
        self.generator.generate(perfect=self.is_perfect)
        self.generator.set_entry_exit(self.entry, self.exit_point)
        # 3. Reset the Display Grid to 'Blank Canvas' (All Walls = 15)
        w, h = self.generator.width, self.generator.height
        self.display_grid = [[15 for _ in range(w)] for _ in range(h)]
        self.step_index = 0
        # 4. Start the Timer (Calls 'on_timer_tick' every 0.05 seconds)
        # Faster = 0.01, Slower = 0.1
        self.timer = self.set_interval(0.05, self.on_timer_tick)

    def on_timer_tick(self) -> None:
        """Called repeatedly by the timer to draw the next step."""
        history = self.generator.history
        # Check if complete
        if self.step_index >= len(history):
            self.timer.stop()
            self.timer = None
            self.notify("Animation Complete!")
            return
        # 1. Get the next update from history
        updates = history[self.step_index]
        # 2. Apply updates to our DISPLAY grid
        for (x, y, new_value) in updates:
            self.display_grid[y][x] = new_value
        # 3. Render
        # --- UPDATE 1: Pass coords ---
        maze_str = self.visualizer.render_thick(
            self.display_grid,
            self.generator.pattern_42_coords,
            entry=self.entry,
            exit=self.exit_point

        )
        # 4. Apply Color and Update
        current_color = self.COLORS[self.current_color_index]
        styled_maze = Text(maze_str, style=current_color)
        styled_maze.highlight_regex(r"▒+", "bold #FFD700")
        styled_maze.highlight_regex(r"●", "bold #00BFFF")
        styled_maze.highlight_regex(r"◉", "bold #FF4500")

        self.query_one("#maze_display", Static).update(styled_maze)
        # Move to next frame
        self.step_index += 1
