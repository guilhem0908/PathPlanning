from pathlib import Path
from utils.track_utils import load_track, get_start_pos, compute_world_bounds
from ui.process_pygame import process_pygame
from core.process_path import PathProcessor

TRACKS = ["small_track.csv", "hairpins_increasing_difficulty.csv", "peanut.csv"]

if __name__ == "__main__":
    # Setup paths
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"

    print("Choose a track:")
    print("1 - small_track")
    print("2 - hairpins_increasing_difficulty")
    print("3 - peanut")

    try:
        choice_str = input("Your choice (1/2/3): ").strip()
        track_choice = int(choice_str)

        if 1 <= track_choice <= 3:
            selected_track = data_dir / TRACKS[track_choice - 1]

            # 1. Load Data
            print(f"Loading {selected_track}...")
            cones = load_track(selected_track)
            start_pos = get_start_pos(cones)

            if not start_pos:
                start_pos = (0, 0)

            # Separate cones by color for the algorithm
            yellow_cones = [(c['x'], c['y']) for c in cones if c['tag'] == 'yellow']
            blue_cones = [(c['x'], c['y']) for c in cones if c['tag'] == 'blue']

            # 2. Compute Path (Centerline + Smoothing)
            print("Computing centerline...")
            processor = PathProcessor()
            world_bounds = compute_world_bounds(cones)

            raw_path = processor.compute_track_centerline(yellow_cones, blue_cones, start_pos)

            if not raw_path:
                print("Error: Could not compute a valid path.")
            else:
                print(f"Raw path found: {len(raw_path)} points.")

                print("Smoothing path...")
                final_path = processor.smooth_path(raw_path)
                print(f"Final smooth path: {len(final_path)} points.")

                # 3. Launch Visualization
                # We pass the path to process_pygame which handles the car simulation
                process_pygame(selected_track, cones, world_bounds, path=final_path)

        else:
            print("Invalid choice.")

    except ValueError:
        print("Please enter a valid number.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
