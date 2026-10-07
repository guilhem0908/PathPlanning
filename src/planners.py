"""
planners.py

One name per planning module of ``core/``, and a single function to run any
of them on a cone map.

The three modules expose the same ``PathProcessor`` class
(``compute_track_centerline`` then ``smooth_path``). Before this file existed
the planner was chosen by commenting an import in ``main.py``.
"""

from __future__ import annotations

import contextlib
import importlib
import io
import random
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

Point2D = Tuple[float, float]


@dataclass(frozen=True)
class PlannerInfo:
    """
    Description of a planner.

    Attributes:
        key: Name used on the command line.
        module: Module of ``core/`` that implements it.
        summary: What it does.
        author: Who wrote the module, by role (the names are in the commit history).
        uses_rrt: Whether it runs RRT* between waypoints.
    """

    key: str
    module: str
    summary: str
    author: str
    uses_rrt: bool


PLANNERS: Dict[str, PlannerInfo] = {
    "midpoint": PlannerInfo(
        key="midpoint",
        module="core.process_path",
        summary="midpoints of nearest blue/yellow cones, ordered greedily, "
        "smoothed by a periodic cubic B-spline",
        author="a teammate",
        uses_rrt=False,
    ),
    "rrt": PlannerInfo(
        key="rrt",
        module="core.process_path_rrt",
        summary="RRT* between consecutive midpoints with the cones as obstacles, "
        "then neighbour averaging and a periodic cubic B-spline",
        author="another teammate",
        uses_rrt=True,
    ),
    "rrt-lsq": PlannerInfo(
        key="rrt-lsq",
        module="core.process_path_rrt_qp",
        summary="same RRT* front end, then regularised least-squares smoothing "
        "(called 'QP' in the module) and a periodic cubic spline",
        author="another teammate",
        uses_rrt=True,
    ),
}

DEFAULT_PLANNER = "rrt"

# Other spellings accepted on the command line.
ALIASES: Dict[str, str] = {"rrt-qp": "rrt-lsq", "qp": "rrt-lsq", "middlepoints": "midpoint"}


@dataclass
class PlanResult:
    """
    Outcome of one planning run.

    Attributes:
        planner: Planner key.
        raw_path: Output of ``compute_track_centerline``.
        path: Output of ``smooth_path`` (the line shown in the viewer).
        centerline_time_s: Time spent in ``compute_track_centerline``.
        smoothing_time_s: Time spent in ``smooth_path``.
        rrt_segments: Number of RRT* searches started (None without RRT*).
        rrt_solved: Number of them that returned a path (None without RRT*).
    """

    planner: str
    raw_path: List[Point2D]
    path: List[Point2D]
    centerline_time_s: float
    smoothing_time_s: float
    rrt_segments: Optional[int] = None
    rrt_solved: Optional[int] = None

    @property
    def planning_time_s(self) -> float:
        """Total planning time."""
        return self.centerline_time_s + self.smoothing_time_s


def planner_info(name: str) -> PlannerInfo:
    """
    Look a planner up by name or alias.

    Raises:
        KeyError: If the name is unknown.
    """
    key = ALIASES.get(name.lower(), name.lower())
    if key not in PLANNERS:
        raise KeyError(f"Unknown planner {name!r}. Choose from: {', '.join(PLANNERS)}")
    return PLANNERS[key]


def split_cones(cones: Sequence[dict]) -> Tuple[List[Point2D], List[Point2D]]:
    """Yellow and blue cone positions of a track, in that order."""
    yellow = [(c["x"], c["y"]) for c in cones if c["tag"] == "yellow"]
    blue = [(c["x"], c["y"]) for c in cones if c["tag"] == "blue"]
    return yellow, blue


def _as_points(path) -> List[Point2D]:
    return [(float(p[0]), float(p[1])) for p in path]


def plan(
    name: str,
    cones: Sequence[dict],
    start_pos: Point2D,
    seed: Optional[int] = None,
    quiet: bool = True,
) -> PlanResult:
    """
    Run a planner on a cone map.

    Args:
        name: Planner name or alias.
        cones: Track cones as returned by ``utils.track_utils.load_track``.
        start_pos: Starting position of the car.
        seed: Seed of Python's ``random`` module, which RRT* samples from.
            None leaves the generator as it is.
        quiet: Swallow what the planning modules print.

    Returns:
        The raw and smoothed paths with timings and, for the RRT* planners,
        how many of the searches between waypoints succeeded.
    """
    info = planner_info(name)
    module = importlib.import_module(info.module)
    yellow, blue = split_cones(cones)
    if seed is not None:
        random.seed(seed)

    # Count RRT* searches without touching the planning module: wrap
    # RRTStar.plan for the duration of this call.
    counts = {"segments": 0, "solved": 0}
    rrt_class = getattr(module, "RRTStar", None)
    original_plan = getattr(rrt_class, "plan", None)

    def counted_plan(self):
        result = original_plan(self)
        counts["segments"] += 1
        counts["solved"] += result is not None
        return result

    sink = io.StringIO() if quiet else None
    try:
        if rrt_class is not None:
            rrt_class.plan = counted_plan
        with contextlib.redirect_stdout(sink) if quiet else contextlib.nullcontext():
            processor = module.PathProcessor()
            started = time.perf_counter()
            raw = processor.compute_track_centerline(yellow, blue, start_pos)
            centerline_time = time.perf_counter() - started
            started = time.perf_counter()
            smooth = processor.smooth_path(raw) if raw else []
            smoothing_time = time.perf_counter() - started
    finally:
        if rrt_class is not None:
            rrt_class.plan = original_plan

    return PlanResult(
        planner=info.key,
        raw_path=_as_points(raw),
        path=_as_points(smooth),
        centerline_time_s=centerline_time,
        smoothing_time_s=smoothing_time,
        rrt_segments=counts["segments"] if info.uses_rrt else None,
        rrt_solved=counts["solved"] if info.uses_rrt else None,
    )
