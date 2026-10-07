"""Path measurements against exactly known geometry."""

from __future__ import annotations

import math

import numpy as np
import pytest

from metrics import densify, min_clearance, path_length, share_between_rows

SQUARE = [(0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0)]


def test_length_of_a_square_is_its_perimeter_even_when_left_open():
    assert path_length(SQUARE) == pytest.approx(16.0)


def test_length_is_the_same_when_the_loop_is_already_closed():
    assert path_length(SQUARE + [SQUARE[0]]) == pytest.approx(16.0)


def test_length_of_degenerate_paths_is_zero():
    assert path_length([]) == 0.0
    assert path_length([(1.0, 2.0)]) == 0.0


def test_densify_spaces_the_samples_evenly_along_the_loop():
    samples = densify(SQUARE, step=0.5)
    steps = np.hypot(*np.diff(np.vstack((samples, samples[:1])), axis=0).T)
    assert len(samples) == 32
    assert steps.max() == pytest.approx(0.5, abs=1e-9)
    assert steps.min() == pytest.approx(0.5, abs=1e-9)


def test_clearance_is_the_distance_to_the_nearest_cone_not_to_the_nearest_vertex():
    # The cone sits 1 m beside the middle of the first edge, 2 m from both vertices.
    clearance = min_clearance(SQUARE, [(2.0, -1.0)], step=0.05)
    assert clearance == pytest.approx(1.0, abs=1e-6)


def test_clearance_without_cones_is_infinite():
    assert min_clearance(SQUARE, []) == math.inf


def test_share_between_rows_is_one_for_a_path_in_the_middle_of_two_rows():
    blue = [(x, 1.0) for x in np.linspace(-5, 15, 41)]
    yellow = [(x, -1.0) for x in np.linspace(-5, 15, 41)]
    path = [(0.0, 0.0), (10.0, 0.0), (10.0, 0.1), (0.0, 0.1)]
    assert share_between_rows(path, blue, yellow) == pytest.approx(1.0)


def test_share_between_rows_drops_for_a_path_that_leaves_the_rows():
    blue = [(x, 1.0) for x in np.linspace(-5, 15, 41)]
    yellow = [(x, -1.0) for x in np.linspace(-5, 15, 41)]
    outside = [(0.0, 5.0), (10.0, 5.0), (10.0, 5.1), (0.0, 5.1)]
    assert share_between_rows(outside, blue, yellow) == pytest.approx(0.0, abs=0.05)
