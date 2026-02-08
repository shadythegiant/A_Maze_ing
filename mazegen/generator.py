import random
from typing import List, Tuple, Optional


class MazeGenerator:
    """
    Core logic for generating perfect mazes using bitmask representation.
    """

    NORTH: int = 1
    EAST: int = 2
    SOUTH: int = 4
    WEST: int = 8
    ALL_WALLS: int = 15

    def __init__(self, width: int, height: int, seed: Optional[int] = None) -> None:
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
        self.history = []
        # set for the 42 pattern coords
        self.pattern_42_coords = set()
        self.pattern_42_failed = False

    def generate(self) -> None:
        """
        Executes the generation algorithm.
        """
        # Resetting the grid to closed walls cells
        self.grid = [[15 for _ in range(self.width)]
                     for _ in range(self.height)]

        self.history = []
        self.pattern_42_coords = set()
        self.pattern_42_failed = False

        start_x, start_y = 0, 0
        stack: List[Tuple[int, int]] = [(start_x, start_y)]
        visited = set()
        visited.add((start_x, start_y))

        # adding the 42 pattern coord to visited
        self._embed_42(visited)

        while stack:
            current_x, current_y = stack[-1]
            unvisited_neighbors = self._get_unvisited_neighbors(
                current_x, current_y, visited
            )

            if unvisited_neighbors:
                next_x, next_y, direction = self._rng.choice(
                    unvisited_neighbors)
                self._remove_wall(current_x, current_y,
                                  next_x, next_y, direction)
                visited.add((next_x, next_y))
                stack.append((next_x, next_y))
            else:
                stack.pop()

    def set_entry_exit(self, entry: Tuple[int, int], exit: Tuple[int, int]) -> None:
        self._validate_border_point(entry, "Entry")
        self._validate_border_point(exit, "Exit")

        if entry == exit:
            raise ValueError("Entry and Exit cannot be the same coordinate.")

    def get_grid(self) -> List[List[int]]:
        return self.grid

    # --- Internal Helper Methods ---

    def _get_unvisited_neighbors(self, x: int, y: int, visited: set) -> List[Tuple[int, int, int]]:
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

    def _remove_wall(self, x1: int, y1: int, x2: int, y2: int, direction: int) -> None:
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

        self.history.append([
            (x1, y1, self.grid[y1][x1]),
            (x2, y2, self.grid[y2][x2])
        ])

    def _validate_border_point(self, point: Tuple[int, int], name: str) -> None:
        x, y = point
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise ValueError(f"{name} {point} is outside maze bounds.")
        if not (x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1):
            raise ValueError(f"{name} {point} must be on the maze border.")

    def _embed_42(self, visited: set) -> None:
        """
        Marks '42' pattern cells as visited so they remain solid walls.
        """
        # Digit '4' coords
        pat_4 = {
            (0, 0), (0, 1), (0, 2), (3, 0), (3, 1), (3, 2),
            (0, 2), (1, 2), (2, 2), (3, 2),
            (3, 3), (3, 4)
        }
        # Digit '2' coords
        pat_2 = {
            (0, 0), (1, 0), (2, 0), (3, 0),
            (3, 1), (3, 2),
            (2, 2), (1, 2), (0, 2),
            (0, 3), (0, 4),
            (1, 4), (2, 4), (3, 4)
        }

        pat_width = 7
        pat_height = 6

        if self.width < pat_width + 4 or self.height < pat_height + 4:
            print("Error: Maze size too small for '42' pattern.")
            self.pattern_42_failed = True
            return

        offset_x = (self.width - pat_width) // 2
        offset_y = (self.height - pat_height) // 2

        # Apply '4'
        for (dx, dy) in pat_4:
            px, py = offset_x + dx, offset_y + dy
            visited.add((px, py))
            self.pattern_42_coords.add((px, py))

        # Apply '2' (Shifted by 5 spaces)
        for (dx, dy) in pat_2:
            px, py = offset_x + dx + 5, offset_y + dy
            visited.add((px, py))
            self.pattern_42_coords.add((px, py))
