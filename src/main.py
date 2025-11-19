from pathlib import Path
from ui.process_pygame import process_pygame
from core.process_path import generate_dummy_path

TRACKS = ["small_track.csv", "hairpins_increasing_difficulty.csv", "peanut.csv"]


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

            my_path = generate_dummy_path()

            process_pygame(selected_track, path=my_path)
        else:
            print("Invalid choice.")
    except ValueError:
        print("Please enter a number.")
