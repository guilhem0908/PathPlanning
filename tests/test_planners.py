"""The three planners, driven through the common entry point."""

from __future__ import annotations

import math

import pytest

from metrics import min_clearance, path_length
from planners import ALIASES, PLANNERS, plan, planner_info, split_cones
from utils.track_catalog import resolve_track
from utils.track_utils import get_start_pos, load_track

from tests.conftest import RING_CENTRE_RADIUS_M, make_ring


@pytest.fixture(scope="module")
def small_track():
    cones = load_track(resolve_track("small_track"))
    return cones, get_start_pos(cones)


def test_every_alias_points_to_a_registered_planner():
    assert set(ALIASES.values()) <= set(PLANNERS)


def test_planner_lookup_accepts_aliases_and_is_case_insensitive():
    assert planner_info("QP").key == "rrt-lsq"
    assert planner_info("MiddlePoints").key == "midpoint"
    assert planner_info("rrt").key == "rrt"


def test_unknown_planner_lists_the_valid_names():
    with pytest.raises(KeyError, match="midpoint"):
        planner_info("dijkstra")


def test_split_cones_keeps_only_blue_and_yellow():
    cones = [
        {"tag": "yellow", "x": 1.0, "y": 2.0},
        {"tag": "blue", "x": 3.0, "y": 4.0},
        {"tag": "big_orange", "x": 5.0, "y": 6.0},
    ]
    assert split_cones(cones) == ([(1.0, 2.0)], [(3.0, 4.0)])


def test_midpoint_planner_follows_the_middle_of_a_ring(ring_cones):
    result = plan("midpoint", ring_cones, get_start_pos(ring_cones))
    # The midpoints of facing cones lie exactly on the centre circle.
    for x, y in result.raw_path:
        assert math.hypot(x, y) == pytest.approx(RING_CENTRE_RADIUS_M, abs=1e-9)
    # The smoothing spline (smoothing factor 0.5) may move the line off the midpoints:
    # 0.21 m at most on this ring.
    radii = [math.hypot(x, y) for x, y in result.path]
    assert min(radii) > RING_CENTRE_RADIUS_M - 0.25
    assert max(radii) < RING_CENTRE_RADIUS_M + 0.25
    circumference = 2.0 * math.pi * RING_CENTRE_RADIUS_M
    assert path_length(result.path) == pytest.approx(circumference, rel=0.02)


def test_midpoint_planner_keeps_clear_of_the_cones_on_a_ring(ring_cones):
    result = plan("midpoint", ring_cones, get_start_pos(ring_cones))
    cones = [c for row in split_cones(ring_cones) for c in row]
    assert min_clearance(result.path, cones) > 1.5


def test_midpoint_planner_returns_an_empty_path_without_both_colours():
    only_blue = [{"tag": "blue", "x": float(i), "y": 0.0} for i in range(5)]
    result = plan("midpoint", only_blue, (0.0, 0.0))
    assert result.path == []
    assert result.rrt_segments is None


def test_midpoint_planner_makes_no_rrt_searches(small_track):
    cones, start = small_track
    result = plan("midpoint", cones, start)
    assert result.rrt_segments is None and result.rrt_solved is None
    assert result.planning_time_s == pytest.approx(
        result.centerline_time_s + result.smoothing_time_s
    )


@pytest.mark.parametrize("name", ["rrt", "rrt-lsq"])
def test_rrt_planners_are_reproducible_with_a_seed(name, small_track):
    cones, start = small_track
    first = plan(name, cones, start, seed=3)
    second = plan(name, cones, start, seed=3)
    assert first.path == second.path
    assert first.rrt_solved == second.rrt_solved


@pytest.mark.parametrize("name", ["rrt", "rrt-lsq"])
def test_rrt_planners_report_their_searches_and_stay_near_the_loop(name, small_track):
    cones, start = small_track
    result = plan(name, cones, start, seed=0)
    assert result.rrt_segments is not None and result.rrt_segments > 0
    assert 0 <= result.rrt_solved <= result.rrt_segments
    midpoint = plan("midpoint", cones, start)
    assert path_length(result.path) == pytest.approx(path_length(midpoint.path), rel=0.15)


def test_planning_restores_the_rrt_class_it_instruments(small_track):
    from core import process_path_rrt

    cones, start = small_track
    original = process_path_rrt.RRTStar.plan
    plan("rrt", cones, start, seed=0)
    assert process_path_rrt.RRTStar.plan is original


def test_planning_is_quiet_by_default(small_track, capsys):
    cones, start = small_track
    plan("rrt", cones, start, seed=0)
    assert capsys.readouterr().out == ""


# core/process_path_rrt.py treats every cone as a disc of this radius.
RRT_CONE_RADIUS_M = 1.2


def test_rrt_solves_every_segment_when_gates_are_wider_than_two_cone_discs():
    gate_width = 2.0 * RRT_CONE_RADIUS_M + 0.2
    cones = make_ring(half_width_m=gate_width / 2.0)
    result = plan("rrt", cones, get_start_pos(cones), seed=0)
    assert result.rrt_solved == result.rrt_segments > 0


def test_rrt_solves_no_segment_when_gates_are_narrower_than_two_cone_discs():
    # The middle of a gate then lies inside the discs of its own two cones, so the
    # goal of every segment is in collision and the search cannot end.
    gate_width = 2.0 * RRT_CONE_RADIUS_M - 0.2
    cones = make_ring(half_width_m=gate_width / 2.0)
    result = plan("rrt", cones, get_start_pos(cones), seed=0)
    assert result.rrt_solved == 0 and result.rrt_segments > 0
