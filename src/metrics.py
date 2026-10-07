"""
metrics.py

Measurements of a planned path against the cone map it was planned on.
"""

from __future__ import annotations

from typing import Sequence, Tuple

import numpy as np
from scipy.spatial import cKDTree

Point2D = Tuple[float, float]


def _closed(path: Sequence[Point2D]) -> np.ndarray:
    points = np.asarray(path, dtype=float).reshape(-1, 2)
    if len(points) and not np.allclose(points[0], points[-1]):
        points = np.vstack((points, points[:1]))
    return points


def path_length(path: Sequence[Point2D]) -> float:
    """Length of the path taken as a closed loop."""
    points = _closed(path)
    if len(points) < 2:
        return 0.0
    steps = np.diff(points, axis=0)
    return float(np.hypot(steps[:, 0], steps[:, 1]).sum())


def densify(path: Sequence[Point2D], step: float = 0.1) -> np.ndarray:
    """
    Points every ``step`` metres along the closed path.

    Planners return paths of very different densities; measuring on a constant
    spacing makes their numbers comparable.
    """
    points = _closed(path)
    if len(points) < 2:
        return points
    seg = np.hypot(*np.diff(points, axis=0).T)
    s = np.concatenate(([0.0], np.cumsum(seg)))
    if s[-1] <= 0.0:
        return points[:1]
    targets = np.arange(0.0, s[-1], step)
    return np.column_stack(
        (np.interp(targets, s, points[:, 0]), np.interp(targets, s, points[:, 1]))
    )


def min_clearance(
    path: Sequence[Point2D], cones: Sequence[Point2D], step: float = 0.1
) -> float:
    """
    Smallest distance between the path and the centre of any cone.

    Args:
        path: Planned path (closed loop).
        cones: Positions of the cones to stay clear of.
        step: Spacing at which the path is sampled.
    """
    samples = densify(path, step)
    if len(samples) == 0 or len(cones) == 0:
        return float("inf")
    distances, _ = cKDTree(np.asarray(cones, dtype=float)).query(samples)
    return float(distances.min())


def share_between_rows(
    path: Sequence[Point2D],
    blue: Sequence[Point2D],
    yellow: Sequence[Point2D],
    step: float = 0.1,
) -> float:
    """
    Share of the path that runs between the two rows of cones.

    A sample counts as between the rows when its nearest blue cone and its
    nearest yellow cone lie on opposite sides of it (the angle between the two
    directions is above 90 degrees). A path that cuts across the infield or
    leaves the track has both nearest cones on the same side.

    Returns:
        A value between 0 and 1.
    """
    samples = densify(path, step)
    if len(samples) == 0 or len(blue) == 0 or len(yellow) == 0:
        return 0.0
    blue_xy = np.asarray(blue, dtype=float)
    yellow_xy = np.asarray(yellow, dtype=float)
    _, bi = cKDTree(blue_xy).query(samples)
    _, yi = cKDTree(yellow_xy).query(samples)
    to_blue = blue_xy[bi] - samples
    to_yellow = yellow_xy[yi] - samples
    opposite = (to_blue * to_yellow).sum(axis=1) < 0.0
    return float(opposite.mean())
