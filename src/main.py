from pathlib import Path
from utils.track_utils import get_start_pos, get_goal_pos, get_obstacles, load_track, compute_world_bounds
from ui.process_pygame import process_pygame
from core.process_path import RRTStar, smooth_path

TRACKS = ["small_track.csv", "hairpins_increasing_difficulty.csv", "peanut.csv"]
EXPAND_DIS = 2.0
PATH_RESOLUTION = 0.5
MAX_ITER = 500

if __name__ == "__main__":
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

            cones = load_track(selected_track)
            bounds = compute_world_bounds(cones)
            start_pos = get_start_pos(cones)
            goal_pos = get_goal_pos(cones)
            obstacles = get_obstacles(cones, size=0.8)

            rrt = RRTStar(start=start_pos, goal=goal_pos, obstacle_list=obstacles,
                          rand_area=[bounds[0], bounds[1]], expand_dis=EXPAND_DIS,
                          max_iter=MAX_ITER, path_resolution=PATH_RESOLUTION)

            path = rrt.plan()
            final_path = smooth_path(path)

            process_pygame(selected_track, cones, bounds, path=final_path)
        else:
            print("Invalid choice.")
    except ValueError:
        print("Please enter a number.")
