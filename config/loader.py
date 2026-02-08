import sys
from typing import Dict, Tuple, Any

# Define the set of keys that must be present in the config file
MANDATORY_KEYS = {
    "WIDTH", "HEIGHT", "ENTRY", "EXIT", "PERFECT", "OUTPUT_FILE"
}


def load_config(filepath: str) -> Dict[str, Any]:
    """
    Parses and validates the maze generation configuration file.

    Reads key-value pairs from the file, ignores comments, converts types,
    and performs strict validation on maze constraints (dimensions and borders).

    Args:
        filepath: The path to the configuration file (e.g., "config.txt").

    Returns:
        A dictionary containing the validated configuration with correct types:
        - WIDTH (int)
        - HEIGHT (int)
        - ENTRY (tuple[int, int])
        - EXIT (tuple[int, int])
        - PERFECT (bool)
        - OUTPUT_FILE (str)

    Raises:
        SystemExit: If the file is missing, syntax is invalid, or values
                    violate constraints (exits with status 1).
    """
    raw_config = _read_and_parse_raw_file(filepath)
    validated_config = _validate_and_convert(raw_config)
    return validated_config


def _read_and_parse_raw_file(filepath: str) -> Dict[str, str]:
    """
    Step 1: Reads the file and extracts raw KEY=VALUE strings.
    Handles file I/O errors and basic syntax checking.
    """
    raw_config = {}

    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Configuration file '{filepath}' not found.")
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied reading '{filepath}'.")
        sys.exit(1)

    for line_num, line in enumerate(lines, 1):
        # Remove comments (everything after #) and whitespace
        clean_line = line.split('#', 1)[0].strip()

        # Skip empty lines
        if not clean_line:
            continue

        # Check for valid KEY=VALUE syntax
        if '=' not in clean_line:
            print(f"Error: Syntax error on line {line_num} in '{filepath}'.")
            print(f"       Expected 'KEY=VALUE', found: '{clean_line}'")
            sys.exit(1)

        # Split only on the first '=' to allow '=' in values (unlikely but safe)
        key, value = clean_line.split('=', 1)
        key = key.strip()
        value = value.strip()

        if not key:
            print(f"Error: Missing key on line {line_num}.")
            sys.exit(1)

        raw_config[key] = value

    return raw_config


def _validate_and_convert(raw_config: Dict[str, str]) -> Dict[str, Any]:
    """
    Step 2: Converts strings to proper types and enforces maze rules.
    """
    config: Dict[str, Any] = {}

    # 1. Check for missing keys
    missing_keys = MANDATORY_KEYS - raw_config.keys()
    if missing_keys:
        print(f"Error: Missing mandatory configuration keys: {missing_keys}")
        sys.exit(1)

    # 2. Convert and Validate WIDTH / HEIGHT
    try:
        width = int(raw_config['WIDTH'])
        height = int(raw_config['HEIGHT'])

        if width < 3 or height < 3:
            print("Error: WIDTH and HEIGHT must be at least 3.")
            sys.exit(1)

        config['WIDTH'] = width
        config['HEIGHT'] = height
    except ValueError:
        print("Error: WIDTH and HEIGHT must be valid integers.")
        print(f"       Found: WIDTH={raw_config.get('WIDTH')}, "
              f"HEIGHT={raw_config.get('HEIGHT')}")
        sys.exit(1)

    # 3. Convert and Validate PERFECT flag
    config['PERFECT'] = _parse_bool(raw_config['PERFECT'])

    # 4. Validate OUTPUT_FILE
    output_file = raw_config['OUTPUT_FILE']
    if not output_file:
        print("Error: OUTPUT_FILE cannot be empty.")
        sys.exit(1)
    config['OUTPUT_FILE'] = output_file

    # 5. Convert and Validate ENTRY / EXIT Coordinates
    # We pass width/height to validate boundaries immediately
    config['ENTRY'] = _parse_coord(
        raw_config['ENTRY'], "ENTRY", width, height
    )
    config['EXIT'] = _parse_coord(
        raw_config['EXIT'], "EXIT", width, height
    )

    if config['ENTRY'] == config['EXIT']:
        print("Error: ENTRY and EXIT cannot be the same coordinate.")
        sys.exit(1)

    return config


def _parse_bool(value: str) -> bool:
    """
    Robust boolean parsing.
    Accepts: 'true', '1', 'yes', 'on' (case insensitive).
    """
    true_values = {'true', '1', 'yes', 'on'}
    false_values = {'false', '0', 'no', 'off'}
    normalized = value.lower()

    if normalized in true_values:
        return True
    if normalized in false_values:
        return False

    print(f"Error: Invalid boolean value for PERFECT. Found: '{value}'")
    print("       Expected: True, False, 1, 0, yes, no.")
    sys.exit(1)


def _parse_coord(
    value: str, name: str, width: int, height: int
) -> Tuple[int, int]:
    """
    Parses "x,y" string into a tuple and checks bounds/border rules.
    """
    try:
        if ',' not in value:
            raise ValueError("Missing comma")

        parts = value.split(',')
        if len(parts) != 2:
            raise ValueError("Too many/few values")

        x = int(parts[0].strip())
        y = int(parts[1].strip())

    except ValueError:
        print(f"Error: {name} must be in format 'x,y'. Found: '{value}'")
        sys.exit(1)

    # Check bounds (inside grid)
    if not (0 <= x < width and 0 <= y < height):
        print(f"Error: {name} coordinates ({x},{y}) are out of maze bounds.")
        print(f"       Maze size is {width}x{height}.")
        sys.exit(1)

    # Check border rule (Must be on the edge)
    is_on_border = (x == 0 or x == width - 1 or y == 0 or y == height - 1)
    if not is_on_border:
        print(f"Error: {name} ({x},{y}) must be on the maze border/edge.")
        sys.exit(1)

    return (x, y)
