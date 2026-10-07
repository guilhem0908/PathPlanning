"""Command line: track and planner are chosen by arguments, not by editing imports."""

from __future__ import annotations

import main as cli


def test_list_prints_every_track_and_planner(capsys):
    assert cli.main(["--list"]) == 0
    out = capsys.readouterr().out
    assert "Spa_cones" in out and "small_track" in out
    for planner in ("midpoint", "rrt", "rrt-lsq"):
        assert planner in out


def test_a_planner_runs_without_a_window_and_prints_its_figures(capsys):
    assert cli.main(["--track", "small_track", "--planner", "midpoint", "--no-window"]) == 0
    out = capsys.readouterr().out
    assert "midpoint:" in out and "closest cone" in out


def test_the_original_menu_numbers_still_select_the_original_tracks(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _prompt: "3")
    assert cli.main(["--planner", "midpoint", "--no-window"]) == 0
    assert "peanut.csv" in capsys.readouterr().out


def test_an_invalid_menu_choice_exits_with_an_error(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _prompt: "99")
    assert cli.main(["--no-window"]) == 2
    assert "Invalid choice" in capsys.readouterr().out


def test_an_unknown_planner_exits_with_an_error(capsys):
    assert cli.main(["--track", "peanut", "--planner", "dijkstra", "--no-window"]) == 2
    assert "Unknown planner" in capsys.readouterr().out


def test_an_unknown_track_exits_with_an_error(capsys):
    assert cli.main(["--track", "nowhere", "--no-window"]) == 2
    assert "Unknown track" in capsys.readouterr().out
