import random
from typing import List, Tuple, Optional, Set


class MazeGenerator:
    """
    Core logic for generating perfect mazes using bitmask representation.
    Supports multiple algorithms (DFS, Prims).
    """

    NORTH: int = 1
    EAST: int = 2
    SOUTH: int = 4
    WEST: int = 8
    ALL_WALLS: int = 15

    def __init__(
            self,
            width: int,
            height: int,
            seed: Optional[int] = None) -> None:

        if width < 3 or height < 3:
            raise ValueError("Maze dimensions must be at least 3x3.")

        self.width = width
        self.height = height
        self._rng = random.Random(seed)

        # Initialize grid with 15
        self.grid: List[List[int]] = [
            [self.ALL_WALLS for _ in range(width)] for _ in range(height)
        ]
        # history list for the animation logic in visuals/tui.py
        self.history: List[List[Tuple[int, int, int]]] = []
        # set for the 42 pattern coords
        self.pattern_42_coords: Set[Tuple[int, int]] = set()
        self.pattern_42_failed = False

        # ALGORITHM REGISTRY
        # Maps string names to the actual internal methods
        self.algos = {
            "DFS": self._generate_dfs,
            "Prims": self._generate_prims
        }

    def _reset(self) -> None:
        """Helper to clear grid and history before any generation."""
        self.grid = [
            [self.ALL_WALLS for _ in range(self.width)]
            for _ in range(self.height)
        ]
        self.history = []
        self.pattern_42_coords = set()
        self.pattern_42_failed = False

    def generate(self, algo: str = "DFS", perfect: bool = True) -> None:
        """
        Master generation method.
        1. Resets the grid.
        2. Embeds the '42' pattern.
        3. Dispatches the chosen algorithm (DFS or Prims).
        4. Applies imperfection if requested.
        """
        # Fallback if algo name is wrong
        if algo not in self.algos:
            print(f"Warning: Algo '{algo}' not found. Defaulting to DFS.")
            algo = "DFS"

        # 1. Reset
        self._reset()

        # 2. Setup Visited & Embed 42
        # We start with a fresh visited set.
        # _embed_42 will mark the '42' cells as visited so algos don't break
        # them.
        visited: Set[Tuple[int, int]] = set()
        self._embed_42(visited)

        # 3. Run the selected algorithm
        # We pass 'visited' so the algo knows about the 42 pattern walls.
        self.algos[algo](visited)

        # 4. Handle Imperfect
        if not perfect:
            self.make_imperfect()

    def _generate_dfs(self, visited: Set[Tuple[int, int]]) -> None:
        """
        Implementation of Recursive Backtracker (DFS).
        """
        start_x, start_y = 0, 0

        # If start is inside 42 pattern (rare), find a valid start
        if (start_x, start_y) in visited:
            # Just a fallback, though (0,0) is usually safe
            pass

        visited.add((start_x, start_y))
        stack = [(start_x, start_y)]

        while stack:
            current_x, current_y = stack[-1]
            unvisited_neighbors = self._get_unvisited_neighbors(
                current_x, current_y, visited)

            if unvisited_neighbors:
                nx, ny, direction = self._rng.choice(unvisited_neighbors)
                self._remove_wall(current_x, current_y, nx, ny, direction)
                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()

    def _generate_prims(self, visited: Set[Tuple[int, int]]) -> None:
        """
        Implementation of Randomized Prim's Algorithm.
        """
        start_x, start_y = 0, 0
        visited.add((start_x, start_y))

        # Frontier stores tuples: (target_x, target_y, source_x, source_y,
        # direction)
        frontier = []

        def add_frontier(cx: int, cy: int) -> None:
            moves = [
                (0, -1, self.NORTH), (0, 1, self.SOUTH),
                (1, 0, self.EAST), (-1, 0, self.WEST)
            ]
            for dx, dy, direction in moves:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if (nx, ny) not in visited:
                        frontier.append((nx, ny, cx, cy, direction))

        # Initialize frontier around start
        add_frontier(start_x, start_y)

        while frontier:
            # Pop a random edge from the frontier
            idx = self._rng.randint(0, len(frontier) - 1)
            tx, ty, sx, sy, direction = frontier.pop(idx)

            if (tx, ty) not in visited:
                visited.add((tx, ty))
                # Carve path from Source to Target
                self._remove_wall(sx, sy, tx, ty, direction)
                # Add new neighbors to frontier
                add_frontier(tx, ty)

    def set_entry_exit(
            self,
            entry: Tuple[int, int],
            exit: Tuple[int, int]) -> None:
        self._validate_border_point(entry, "Entry")
        self._validate_border_point(exit, "Exit")

        if entry == exit:
            raise ValueError("Entry and Exit cannot be the same coordinate.")

    def get_grid(self) -> List[List[int]]:
        return self.grid

    # --- Internal Helper Methods ---

    def _get_unvisited_neighbors(
            self,
            x: int,
            y: int,
            visited: Set[Tuple[int, int]]) -> List[Tuple[int, int, int]]:
        neighbors = []
        if y > 0 and (x, y - 1) not in visited:
            neighbors.append((x, y - 1, self.NORTH))
        if y < self.height - 1 and (x, y + 1) not in visited:
            neighbors.append((x, y + 1, self.SOUTH))
        if x < self.width - 1 and (x + 1, y) not in visited:
            neighbors.append((x + 1, y, self.EAST))
        if x > 0 and (x - 1, y) not in visited:
            neighbors.append((x - 1, y, self.WEST))
        return neighbors

    def _remove_wall(
            self,
            x1: int,
            y1: int,
            x2: int,
            y2: int,
            direction: int,
            record_history: bool = True) -> None:
        self.grid[y1][x1] &= ~direction

        opposite_direction = 0
        if direction == self.NORTH:
            opposite_direction = self.SOUTH
        elif direction == self.SOUTH:
            opposite_direction = self.NORTH
        elif direction == self.EAST:
            opposite_direction = self.WEST
        elif direction == self.WEST:
            opposite_direction = self.EAST

        self.grid[y2][x2] &= ~opposite_direction

        if record_history:
            self.history.append([
                (x1, y1, self.grid[y1][x1]),
                (x2, y2, self.grid[y2][x2])
            ])

    def _validate_border_point(
            self,
            point: Tuple[int, int],
            name: str) -> None:
        x, y = point
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise ValueError(f"{name} {point} is outside maze bounds.")
        is_on_border = (x == 0 or x == self.width - 1 or
                        y == 0 or y == self.height - 1)
        if not is_on_border:
            raise ValueError(f"{name} {point} must be on the maze border.")

    def _embed_42(self, visited: Set[Tuple[int, int]]) -> None:
        """
        Embeds a COMPACT '42' pattern (3x5 pixels).
        Total Size: 7 wide x 5 high.
        """
        pat_4 = {
            (0, 0), (2, 0),
            (0, 1), (2, 1),
            (0, 2), (1, 2), (2, 2),
            (2, 3),
            (2, 4)
        }

        pat_2 = {
            (0, 0), (1, 0), (2, 0),
            (2, 1),
            (0, 2), (1, 2), (2, 2),
            (0, 3),
            (0, 4), (1, 4), (2, 4)
        }

        # Dimensions
        pat_width = 7
        pat_height = 5

        # Safety Check
        if self.width < pat_width + 2 or self.height < pat_height + 2:
            print("Error: Maze size too small for '42' pattern.")
            self.pattern_42_failed = True
            return

        # Center logic
        offset_x = (self.width - pat_width) // 2
        offset_y = (self.height - pat_height) // 2

        # Apply '4'
        for (dx, dy) in pat_4:
            px, py = offset_x + dx, offset_y + dy
            visited.add((px, py))
            self.pattern_42_coords.add((px, py))

        # Apply '2' (Shifted by 4 spaces: 3 width + 1 gap)
        for (dx, dy) in pat_2:
            px, py = offset_x + dx + 4, offset_y + dy
            visited.add((px, py))
            self.pattern_42_coords.add((px, py))

    def make_imperfect(self) -> None:
        """
        Randomly breaks a few internal walls to create loops.
        """
        walls_to_break = max(
            1, int((self.width * self.height) * 0.03))
        count = 0
        max_attempts = 500
        attempts = 0

        while count < walls_to_break and attempts < max_attempts:
            attempts += 1

            x = self._rng.randint(0, self.width - 1)
            y = self._rng.randint(0, self.height - 1)

            if (x, y) in self.pattern_42_coords:
                continue

            valid_walls = []
            if y > 0 and (self.grid[y][x] & self.NORTH):
                valid_walls.append((x, y - 1, self.NORTH))
            if y < self.height - 1 and (self.grid[y][x] & self.SOUTH):
                valid_walls.append((x, y + 1, self.SOUTH))
            if x < self.width - 1 and (self.grid[y][x] & self.EAST):
                valid_walls.append((x + 1, y, self.EAST))
            if x > 0 and (self.grid[y][x] & self.WEST):
                valid_walls.append((x - 1, y, self.WEST))

            if not valid_walls:
                continue

            nx, ny, direction = self._rng.choice(valid_walls)

            if (nx, ny) in self.pattern_42_coords:
                continue

            self._remove_wall(x, y, nx, ny, direction, record_history=False)
            self.history.append([
                (x, y, self.grid[y][x]),
                (nx, ny, self.grid[ny][nx])
            ])
            count += 1
