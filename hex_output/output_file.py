def output_hex(
    file_name: str,
    grid: list[list[int]],
    entry: tuple[int, int],
    end: tuple[int, int],
    solver_str: str
) -> None:
    try:
        with open(file_name, 'w') as f:
            for row in grid:
                hex = ""
                for cell in row:
                    hex += format(cell, "X")
                f.write(hex + "\n")
            f.write("\n")
            f.write(f"{entry[0]},{entry[1]}\n")
            f.write(f"{end[0]},{end[1]}\n")
            f.write(solver_str + "\n")
    except Exception as e:
        print(f"error while creating the file: {e}")
