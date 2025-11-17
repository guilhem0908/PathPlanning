from pathlib import Path

from ui.process_pygame import process_pygame


TRACKS = ["small_track.csv", "hairpins_increasing_difficulty.csv", "peanut.csv"]


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"

    print("Choose a track:")
    print("1 - small_track")
    print("2 - hairpins_increasing_difficulty")
    print("3 - peanut")
    track_choice = int(input("Your choice (1/2/3): ").strip())

    process_pygame(data_dir / TRACKS[track_choice - 1])
