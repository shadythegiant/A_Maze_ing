from typing import List


class ASCIIVisualizer:
    """
    Handles converting the bitmask grid into string representations.
    """

    def render(self, grid: List[List[int]]) -> str:
        """
        Parses the grid and RETURNS the standard ASCII representation string.
        """
        NORTH, SOUTH, WEST = 1, 4, 8
        height = len(grid)
        width = len(grid[0]) if height > 0 else 0

        output_lines = []

        for y in range(height):
            line_roof = ""
            line_body = ""

            for x in range(width):
                cell = grid[y][x]

                # Roof
                line_roof += "+"
                line_roof += "---" if (cell & NORTH) else "   "

                # Body
                if cell & WEST:
                    line_body += "|"
                else:
                    line_body += " "
                line_body += "   "

            # Close the row on the right
            line_roof += "+"
            if grid[y][width - 1] & 2:  # Check East
                line_body += "|"
            else:
                line_body += " "

            output_lines.append(line_roof)
            output_lines.append(line_body)

        # Bottom Closure
        bottom_line = ""
        for x in range(width):
            bottom_line += "+"
            bottom_line += "---" if (grid[height - 1][x] & SOUTH) else "   "
        bottom_line += "+"
        output_lines.append(bottom_line)
        return "\n".join(output_lines)

    def render_thick(
        self,
        grid: List[List[int]],
        pattern_coords: set = None,
        solution_path: set = None,
        entry: tuple = None,
        exit: tuple = None
    ) -> str:

        if pattern_coords is None:
            pattern_coords = set()
        if solution_path is None:
            solution_path = set()

        NORTH, SOUTH, WEST = 1, 4, 8
        height = len(grid)
        width = len(grid[0]) if height > 0 else 0

        output_lines = []

        # CHARACTERS
        BLOCK = '█'      # Wall
        SPACE = ' '      # Empty
        P42 = '▒'        # 42 Pattern
        PATH_CHAR = '▓'  # Path Block

        BODY_WIDTH = 3

        # Markers
        ENTRY_MARKER = '●'.center(BODY_WIDTH)
        EXIT_MARKER = '◉'.center(BODY_WIDTH)

        for y in range(height):
            line_top = ""
            line_bot = ""

            for x in range(width):
                cell = grid[y][x]

                # --- Booleans for checks ---
                is_42 = (x, y) in pattern_coords
                is_path = (x, y) in solution_path

                # Check Neighbors for Path Connectivity
                # We connect North if: I am path, neighbor above is path, and no wall exists
                path_north = is_path and (
                    (x, y - 1) in solution_path) and not (cell & NORTH)

                # We connect West if: I am path, neighbor left is path, and no wall exists
                path_west = is_path and (
                    (x - 1, y) in solution_path) and not (cell & WEST)

                # --- CENTER CONTENT ---
                if (x, y) == entry:
                    center_char = ENTRY_MARKER
                elif (x, y) == exit:
                    center_char = EXIT_MARKER
                elif is_path:
                    # DRAW SOLID BLOCK!
                    center_char = PATH_CHAR * BODY_WIDTH
                else:
                    center_char = SPACE * BODY_WIDTH

                wall_brush = P42 if is_42 else BLOCK

                # --- TOP HALF (North Wall Area) ---
                line_top += wall_brush  # Corner is always a wall block

                if is_42:
                    line_top += wall_brush * BODY_WIDTH
                elif path_north:
                    # CONNECT PATH NORTH
                    line_top += PATH_CHAR * BODY_WIDTH
                elif cell & NORTH:
                    line_top += BLOCK * BODY_WIDTH
                else:
                    line_top += SPACE * BODY_WIDTH

                # --- BOTTOM HALF (West Wall Area + Center) ---

                # 1. The West Wall Slot
                if is_42:
                    line_bot += wall_brush
                elif path_west:
                    # CONNECT PATH WEST
                    line_bot += PATH_CHAR
                elif cell & WEST:
                    line_bot += BLOCK
                else:
                    line_bot += SPACE

                # 2. The Center Slot
                if is_42:
                    line_bot += wall_brush * BODY_WIDTH
                else:
                    line_bot += center_char

            # --- CLOSE RIGHT EDGE ---
            line_top += BLOCK

            # Check if Right Wall needs 42 styling
            if is_42 and (width-1, y) in pattern_coords:
                line_bot += P42
            else:
                # Standard Right Wall
                line_bot += BLOCK if (grid[y][width - 1] & 2) else SPACE

            output_lines.append(line_top)
            output_lines.append(line_bot)

        # --- BOTTOM CLOSURE ---
        bottom_line = ""
        for x in range(width):
            bottom_line += BLOCK
            cell = grid[height - 1][x]
            is_42 = (x, height - 1) in pattern_coords

            if is_42:
                bottom_line += P42 * BODY_WIDTH
            else:
                if cell & SOUTH:
                    bottom_line += BLOCK * BODY_WIDTH
                else:
                    bottom_line += SPACE * BODY_WIDTH

        bottom_line += BLOCK
        output_lines.append(bottom_line)

        return "\n".join(output_lines)
