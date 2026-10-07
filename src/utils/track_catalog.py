"""
utils/track_catalog.py

Find the cone maps bundled in ``data/``.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

# The three tracks of the original menu keep their numbers 1 to 3.
FIRST_TRACKS = ["small_track", "hairpins_increasing_difficulty", "peanut"]


def list_tracks() -> List[str]:
    """
    Names (file names without ``.csv``) of every bundled track.

    The three tracks of the original menu come first, the others follow in
    alphabetical order.
    """
    found = sorted((p.stem for p in DATA_DIR.glob("*.csv")), key=str.lower)
    first = [name for name in FIRST_TRACKS if name in found]
    return first + [name for name in found if name not in first]


def resolve_track(name: str) -> Path:
    """
    Path of a track given its name, its file name or a path to a CSV file.

    A name is matched without regard to case and the ``_cones`` suffix of the
    circuit-shaped maps may be left out, so ``spa`` finds ``Spa_cones.csv``.

    Raises:
        FileNotFoundError: If nothing matches.
    """
    direct = Path(name)
    if direct.suffix.lower() == ".csv" and direct.is_file():
        return direct

    wanted = direct.stem.lower()
    for track in list_tracks():
        if wanted in (track.lower(), track.lower().removesuffix("_cones")):
            return DATA_DIR / f"{track}.csv"
    raise FileNotFoundError(
        f"Unknown track {name!r}. Run with --list to see the bundled tracks."
    )
