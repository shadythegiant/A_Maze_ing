import sys
from config.loader import load_config
from mazegen.generator import MazeGenerator
from visuals.tui import MazeApp


def main():
    # 1. Argument Validation
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py <config_file>")
        sys.exit(1)

    config_file = sys.argv[1]

    # 2. Parse Configuration
    print(f"Loading configuration from '{config_file}'...")
    try:
        config = load_config(config_file)
    except Exception as e:
        print(f"Config Error: {e}")
        sys.exit(1)

    width = config['WIDTH']
    height = config['HEIGHT']
    entry = config['ENTRY']
    exit_point = config['EXIT']
    is_perfect = config.get('PERFECT', True)
    # 3. Initialize Generator Logic
    # We create the instance, but we don't run .generate() yet.
    # The App will handle that.
    print(f"Initializing {width}x{height} MazeGenerator...")
    try:
        maze_gen = MazeGenerator(width, height)
    except ValueError as e:
        print(f"Initialization Error: {e}")
        sys.exit(1)

    # 4. Launch the Visualization
    # The App takes ownership of the generator instance.
    app = MazeApp(maze_gen, entry, exit_point, is_perfect)
    app.run()


if __name__ == "__main__":
    main()
