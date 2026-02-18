def solve(grid: list[list[int]], start: tuple[int, int],
          end: tuple[int, int]) -> str:
    """
    created a que that store and append the open cels near by
    """
    qued = [(start)]
    """
    visted store two valuable info to keep track ofthe solving path wich
    is first it store the current sell cords in the key section
    and store the cords of prev cels before reach this current cell
    """
    visted_cur_from = {start: (None, None, "")}
    """
    list of all possible moves in cell (up, down, left, right) represend
    by char key word to indicat wish direction next
    """
    moves = [(0, -1, "N", 1),
             (0, 1, "S", 4),
             (-1, 0, "W", 8),
             (1, 0, "E", 2)
             ]
    head = 0
    while head < len(qued):
        """
        here is the core of the algo
        first it take one cord (0, 0)
        and search for the next availbe cell that can take as nighber
        after it all reach the availble cells in the maze (grid)
        it chose the short path to end point
        """
        cur_x, cur_y = qued[head]
        head += 1

        if (cur_x, cur_y) == end:
            return path_investgater(visted_cur_from, end)

        for dx, dy, char, bit in moves:
            nx, ny = cur_x + dx, cur_y + dy
            if (0 <= nx < len(grid[0]) and 0 <= ny < len(grid)):
                if not (grid[cur_y][cur_x] & bit) and \
                        (nx, ny) not in visted_cur_from:
                    qued.append((nx, ny))
                    visted_cur_from[(nx, ny)] = (cur_x, cur_y, char)
    return "no path found"


def path_investgater(visited: dict, end: tuple[int, int]) -> str:
    """
    this function help to return the full path as
    a string ex :(NWNES)
    """
    path = []
    cur = end
    while visited[cur][0] is not None:
        px, py, char = visited[cur]
        path.append(char)
        cur = (px, py)
    return "".join(path[::-1])


def solve_to_coords(grid: list[list[int]], start: tuple, end: tuple) -> list[tuple]:
    """
    Returns the solution as a list of coordinates: [(0,0), (0,1), (1,1)...]
    Useful for animation.
    """
    path_str = solve(grid, start, end)

    if path_str == "no path found":
        return []

    # Convert "SSENE..." to [(x,y), (x,y)...]
    coords = [start]
    cx, cy = start

    moves = {
        'N': (0, -1),
        'S': (0, 1),
        'E': (1, 0),
        'W': (-1, 0)
    }

    for direction in path_str:
        if direction in moves:
            dx, dy = moves[direction]
            cx += dx
            cy += dy
            coords.append((cx, cy))

    return coords
