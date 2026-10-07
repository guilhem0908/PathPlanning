"""Bundled tracks, name resolution and the CSV loader."""

from __future__ import annotations

from collections import Counter

import pytest

from utils.track_catalog import FIRST_TRACKS, list_tracks, resolve_track
from utils.track_utils import compute_world_bounds, get_start_pos, load_track


def test_all_26_bundled_tracks_are_listed_with_the_original_three_first():
    tracks = list_tracks()
    assert len(tracks) == 26
    assert tracks[:3] == FIRST_TRACKS
    assert len(set(tracks)) == 26


def test_a_circuit_name_resolves_without_case_or_suffix():
    assert resolve_track("spa").name == "Spa_cones.csv"
    assert resolve_track("Spa_cones").name == "Spa_cones.csv"
    assert resolve_track("PEANUT").name == "peanut.csv"


def test_a_csv_path_is_used_as_it_is(tmp_path):
    path = tmp_path / "mine.csv"
    path.write_text("tag,x,y\nblue,0,0\n", encoding="utf-8")
    assert resolve_track(str(path)) == path


def test_an_unknown_track_raises_and_points_to_the_list():
    with pytest.raises(FileNotFoundError, match="--list"):
        resolve_track("nowhere")


def test_small_track_has_the_cones_recorded_in_the_file():
    cones = load_track(resolve_track("small_track"))
    assert Counter(c["tag"] for c in cones) == {
        "blue": 37,
        "yellow": 30,
        "big_orange": 4,
        "car_start": 1,
    }


def test_loading_a_missing_file_raises_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_track(tmp_path / "absent.csv")


def test_start_position_comes_from_the_car_start_row_or_defaults_to_the_origin():
    cones = [{"tag": "blue", "x": 1.0, "y": 2.0}, {"tag": "car_start", "x": 5.0, "y": 6.0}]
    assert get_start_pos(cones) == (5.0, 6.0)
    assert get_start_pos(cones[:1]) == (0.0, 0.0)


def test_world_bounds_add_the_margin_on_every_side():
    cones = [{"tag": "blue", "x": 0.0, "y": 1.0}, {"tag": "blue", "x": 4.0, "y": 3.0}]
    assert compute_world_bounds(cones, margin=1.0) == (-1.0, 5.0, 0.0, 4.0)
