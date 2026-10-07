"""
main.py

Plan a path around a cone track and show it.

    python src/main.py                                   # menu of tracks, RRT* planner
    python src/main.py --track peanut --planner midpoint
    python src/main.py --track spa --planner rrt-lsq --seed 0 --no-window
    python src/main.py --list
"""

import argparse
import sys

from metrics import min_clearance, path_length
from planners import DEFAULT_PLANNER, PLANNERS, plan, planner_info, split_cones
from utils.track_catalog import list_tracks, resolve_track
from utils.track_utils import compute_world_bounds, get_start_pos, load_track


def build_parser():
    """Command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="python src/main.py",
        description="Plan a closed path around a cone track and animate a car along it.",
    )
    parser.add_argument(
        "--track",
        help="track name (see --list) or path to a CSV file; a menu is shown if omitted",
    )
    parser.add_argument(
        "--planner",
        default=DEFAULT_PLANNER,
        help="one of: %s (default: %s)" % (", ".join(PLANNERS), DEFAULT_PLANNER),
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="seed of the random generator used by RRT* (default: not seeded)",
    )
    parser.add_argument(
        "--no-window", action="store_true", help="plan and print the figures without the viewer"
    )
    parser.add_argument(
        "--list", action="store_true", help="list the bundled tracks and the planners, then exit"
    )
    return parser


def print_catalog():
    """Print the bundled tracks and the planners."""
    print("Tracks:")
    for number, name in enumerate(list_tracks(), start=1):
        print(f"  {number:2d} - {name}")
    print("Planners:")
    for info in PLANNERS.values():
        print(f"  {info.key:9s} {info.summary} ({info.author})")


def choose_track():
    """Ask for a track number on the console. Returns None on invalid input."""
    tracks = list_tracks()
    print("Choose a track:")
    for number, name in enumerate(tracks, start=1):
        print(f"{number} - {name}")
    try:
        choice = int(input(f"Your choice (1-{len(tracks)}): ").strip())
    except (ValueError, EOFError):
        print("Please enter a valid number.")
        return None
    if not 1 <= choice <= len(tracks):
        print("Invalid choice.")
        return None
    return tracks[choice - 1]


def main(argv=None):
    """Entry point. Returns the process exit code."""
    args = build_parser().parse_args(argv)
    if args.list:
        print_catalog()
        return 0

    try:
        info = planner_info(args.planner)
    except KeyError as error:
        print(error.args[0])
        return 2

    track_name = args.track or choose_track()
    if track_name is None:
        return 2
    try:
        track_file = resolve_track(track_name)
    except FileNotFoundError as error:
        print(error)
        return 2

    print(f"Loading {track_file.name}...")
    cones = load_track(track_file)
    start_pos = get_start_pos(cones)

    print(f"Planning with '{info.key}': {info.summary}.")
    result = plan(info.key, cones, start_pos, seed=args.seed)
    if not result.path:
        print("Error: could not compute a valid path.")
        return 1

    yellow, blue = split_cones(cones)
    summary = (
        f"{info.key}: {len(result.path)} points, {path_length(result.path):.1f} m, "
        f"{result.planning_time_s * 1000:.0f} ms, "
        f"closest cone at {min_clearance(result.path, yellow + blue):.2f} m"
    )
    if result.rrt_segments:
        summary += f", RRT* solved {result.rrt_solved}/{result.rrt_segments} segments"
    print(summary)

    if args.no_window:
        return 0

    # Imported here so that planning without a window does not need a display.
    from ui.process_pygame import process_pygame

    process_pygame(
        track_file, cones, compute_world_bounds(cones), path=result.path, info=summary
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
