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

    def render_thick(self, grid: List[List[int]], pattern_coords: set = None, entry: tuple = None, exit: tuple = None) -> str:
        if pattern_coords is None:
            pattern_coords = set()

        NORTH, SOUTH, WEST = 1, 4, 8
        height = len(grid)
        width = len(grid[0]) if height > 0 else 0

        output_lines = []

        BLOCK = '█'
        SPACE = ' '
        P42 = '▒'
        BODY_WIDTH = 5

        # Centered markers for 5-space width
        ENTRY_MARKER = '  ●  '
        EXIT_MARKER = '  ◉  '

        for y in range(height):
            line_top = ""
            line_bot = ""

            for x in range(width):
                cell = grid[y][x]
                is_42 = (x, y) in pattern_coords

                # --- Determine Center Content ---
                if (x, y) == entry:
                    center_char = ENTRY_MARKER
                elif (x, y) == exit:
                    center_char = EXIT_MARKER
                else:
                    center_char = SPACE * BODY_WIDTH

                wall_brush = P42 if is_42 else BLOCK

                # --- Top Half ---
                line_top += wall_brush  # Corner (1 char)

                if is_42:
                    line_top += wall_brush * BODY_WIDTH
                else:
                    # North Wall or Open Space
                    line_top += (BLOCK * BODY_WIDTH) if (cell &
                                                         NORTH) else (SPACE * BODY_WIDTH)

                # --- Bottom Half ---
                # West Wall (1 char)
                if is_42:
                    line_bot += wall_brush
                else:
                    line_bot += BLOCK if (cell & WEST) else SPACE

                # Center Body (5 chars)
                if is_42:
                    line_bot += wall_brush * BODY_WIDTH
                else:
                    line_bot += center_char

            # Close Right Edge
            line_top += BLOCK
            if is_42 and (width-1, y) in pattern_coords:
                line_bot += P42
            else:
                line_bot += BLOCK if (grid[y][width - 1] & 2) else SPACE

            output_lines.append(line_top)
            output_lines.append(line_bot)

        # --- Dynamic Bottom Closure ---
        bottom_line = ""
        for x in range(width):
            bottom_line += BLOCK  # Corner

            cell = grid[height - 1][x]
            is_42 = (x, height - 1) in pattern_coords

            if is_42:
                bottom_line += P42 * BODY_WIDTH
            else:
                bottom_line += (BLOCK * BODY_WIDTH) if (cell &
                                                        SOUTH) else (SPACE * BODY_WIDTH)

        bottom_line += BLOCK  # Final Corner
        output_lines.append(bottom_line)

        return "\n".join(output_lines)
