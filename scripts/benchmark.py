"""
scripts/benchmark.py

Run every planner on every bundled track and write a results table.

For each (track, planner) pair, with Python's random generator seeded:
- planning time (centre line / RRT* stage plus smoothing);
- length of the planned loop;
- minimum clearance: smallest distance between the path, sampled every 0.1 m,
  and the centre of a blue or yellow cone;
- share of the path that runs between the two rows of cones;
- for the RRT* planners, how many of the searches between consecutive
  waypoints returned a path (the others fall back to a straight segment).

Outputs, in ``results/``: ``benchmark.json``, ``benchmark.csv`` and
``benchmark.md``. A full run also copies the tables into README.md, between
the two ``benchmark`` marker comments.

Usage (from the repository root):
    python scripts/benchmark.py                                # all 26 tracks
    python scripts/benchmark.py --quick --out-dir build/bench  # the three short tracks
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import statistics
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np  # noqa: E402
import scipy  # noqa: E402
from scipy.spatial import cKDTree  # noqa: E402

from metrics import min_clearance, path_length, share_between_rows  # noqa: E402
from planners import PLANNERS, plan, split_cones  # noqa: E402
from utils.track_catalog import FIRST_TRACKS, list_tracks, resolve_track  # noqa: E402
from utils.track_utils import get_start_pos, load_track  # noqa: E402

SEED = 0
# Half the width of a 1.4 m wide car: below this clearance such a car, centred
# on the path, would touch a cone. The width is an assumption.
TIGHT_CLEARANCE_M = 0.7

README = ROOT / "README.md"
README_BEGIN = "<!-- benchmark:begin (written by scripts/benchmark.py) -->"
README_END = "<!-- benchmark:end -->"


def describe_track(name: str) -> Dict[str, Any]:
    """Facts about a track computed from its cone map."""
    cones = load_track(resolve_track(name))
    yellow, blue = split_cones(cones)
    blue_xy = np.asarray(blue)
    yellow_xy = np.asarray(yellow)
    width, _ = cKDTree(yellow_xy).query(blue_xy)
    spacing, _ = cKDTree(blue_xy).query(blue_xy, k=2)
    return {
        "track": name,
        "blue_cones": len(blue),
        "yellow_cones": len(yellow),
        "width_median_m": round(float(np.median(width)), 2),
        "width_min_m": round(float(width.min()), 2),
        "blue_spacing_median_m": round(float(np.median(spacing[:, 1])), 2),
    }


def run_one(job: Dict[str, Any]) -> Dict[str, Any]:
    """Plan one track with one planner and measure the result."""
    cones = load_track(resolve_track(job["track"]))
    yellow, blue = split_cones(cones)
    result = plan(job["planner"], cones, get_start_pos(cones), seed=SEED)

    record: Dict[str, Any] = {
        "track": job["track"],
        "planner": job["planner"],
        "points": len(result.path),
        "planning_time_ms": round(result.planning_time_s * 1000.0, 1),
        "centerline_time_ms": round(result.centerline_time_s * 1000.0, 1),
        "smoothing_time_ms": round(result.smoothing_time_s * 1000.0, 1),
        "path_length_m": round(path_length(result.path), 1),
        "min_clearance_m": round(min_clearance(result.path, yellow + blue), 2),
        "between_rows_pct": round(100.0 * share_between_rows(result.path, blue, yellow), 1),
        "rrt_segments": result.rrt_segments,
        "rrt_solved": result.rrt_solved,
        "rrt_solved_pct": (
            round(100.0 * result.rrt_solved / result.rrt_segments, 1)
            if result.rrt_segments
            else None
        ),
    }
    return record


# -----------------------------
# Output
# -----------------------------
def _rrt(record: Dict[str, Any]) -> str:
    if record["rrt_segments"] is None:
        return "-"
    return f"{record['rrt_solved']} / {record['rrt_segments']} ({record['rrt_solved_pct']:.0f} %)"


def _time(ms: float) -> str:
    return f"{ms:.0f}" if ms >= 10 else f"{ms:.1f}"


def _detail_rows(records: List[Dict[str, Any]], widths: Dict[str, float]) -> List[str]:
    lines = [
        "| Track | Width (m) | Planner | Planning time (ms) | Path length (m) "
        "| Min clearance (m) | Between the rows (%) | RRT* segments solved |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in records:
        lines.append(
            f"| `{r['track']}` | {widths[r['track']]:.2f} | {r['planner']} "
            f"| {_time(r['planning_time_ms'])} | {r['path_length_m']:.1f} "
            f"| {r['min_clearance_m']:.2f} | {r['between_rows_pct']:.1f} | {_rrt(r)} |"
        )
    return lines


def render_markdown(data: Dict[str, Any]) -> str:
    """Tables for the README."""
    runs: List[Dict[str, Any]] = data["runs"]
    widths = {t["track"]: t["width_median_m"] for t in data["tracks"]}
    tracks = [t["track"] for t in data["tracks"]]
    lines: List[str] = []

    lines.append(f"#### Summary over {len(tracks)} tracks")
    lines.append("")
    lines.append(
        "| Planner | Median planning time (ms) | Slowest track (s) | Median min clearance (m) "
        f"| Worst min clearance (m) | Tracks with clearance below {TIGHT_CLEARANCE_M} m "
        "| Lowest share between the rows (%) | RRT* segments solved |"
    )
    lines.append("|---|---|---|---|---|---|---|---|")
    for planner in PLANNERS:
        mine = [r for r in runs if r["planner"] == planner]
        times = [r["planning_time_ms"] for r in mine]
        clear = [r["min_clearance_m"] for r in mine]
        tight = sum(1 for c in clear if c < TIGHT_CLEARANCE_M)
        segments = sum(r["rrt_segments"] or 0 for r in mine)
        solved = sum(r["rrt_solved"] or 0 for r in mine)
        rrt = f"{solved} / {segments} ({100.0 * solved / segments:.0f} %)" if segments else "-"
        lines.append(
            f"| {planner} | {_time(statistics.median(times))} | {max(times) / 1000.0:.1f} "
            f"| {statistics.median(clear):.2f} | {min(clear):.2f} | {tight} / {len(mine)} "
            f"| {min(r['between_rows_pct'] for r in mine):.1f} | {rrt} |"
        )

    first = [t for t in FIRST_TRACKS if t in tracks]
    if first and len(tracks) > len(first):
        lines.append("")
        lines.append("#### The three tracks of the original menu")
        lines.append("")
        lines.extend(_detail_rows([r for r in runs if r["track"] in first], widths))

    lines.append("")
    lines.append("<details>")
    lines.append(f"<summary>All {len(runs)} runs</summary>")
    lines.append("")
    lines.extend(_detail_rows(runs, widths))
    lines.append("")
    lines.append("</details>")

    env = data["environment"]
    lines.append("")
    lines.append(
        f"Seed {data['seed']} for every run. Width is the median distance from a blue cone to "
        f"the nearest yellow cone. Computing time: {data['runs_time_s']:.0f} s summed over the "
        f"runs, {data['wall_time_s']:.0f} s wall clock with {data['jobs']} processes "
        f"(Python {env['python']}, NumPy {env['numpy']}, SciPy {env['scipy']}, "
        f"{env['system']} {env['machine']}, {env['cpu_count']} logical CPUs, no GPU). The "
        "planning times were taken while the runs shared the machine, so they are indicative."
    )
    return "\n".join(lines) + "\n"


def write_outputs(data: Dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "benchmark.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

    columns = [
        "track", "planner", "points", "planning_time_ms", "centerline_time_ms",
        "smoothing_time_ms", "path_length_m", "min_clearance_m", "between_rows_pct",
        "rrt_segments", "rrt_solved", "rrt_solved_pct",
    ]
    with open(out_dir / "benchmark.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(data["runs"])

    with open(out_dir / "benchmark.md", "w", encoding="utf-8", newline="\n") as f:
        f.write(render_markdown(data))


def update_readme(markdown: str) -> bool:
    """Replace the benchmark block of README.md. Returns False if there is none."""
    if not README.is_file():
        return False
    text = README.read_text(encoding="utf-8")
    if README_BEGIN not in text or README_END not in text:
        return False
    head, rest = text.split(README_BEGIN, 1)
    _, tail = rest.split(README_END, 1)
    block = f"{README_BEGIN}\n\n{markdown.strip()}\n\n{README_END}"
    with open(README, "w", encoding="utf-8", newline="\n") as f:
        f.write(head + block + tail)
    return True


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--tracks", nargs="*", default=None, help="tracks to run (default: all)")
    parser.add_argument("--jobs", type=int, default=min(8, os.cpu_count() or 1))
    parser.add_argument("--out-dir", type=Path, default=ROOT / "results")
    parser.add_argument(
        "--quick", action="store_true", help="only the three tracks of the original menu"
    )
    args = parser.parse_args(argv)

    tracks = args.tracks or (FIRST_TRACKS if args.quick else list_tracks())
    tracks = [resolve_track(name).stem for name in tracks]
    jobs = [{"track": t, "planner": p} for t in tracks for p in PLANNERS]

    started = time.perf_counter()
    if args.jobs > 1:
        with ProcessPoolExecutor(max_workers=args.jobs) as pool:
            runs = list(pool.map(run_one, jobs))
    else:
        runs = [run_one(job) for job in jobs]
    wall = time.perf_counter() - started

    data = {
        "seed": SEED,
        "tight_clearance_m": TIGHT_CLEARANCE_M,
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "system": platform.system(),
            "machine": platform.machine(),
            "cpu_count": os.cpu_count(),
        },
        "jobs": args.jobs,
        "wall_time_s": round(wall, 1),
        "runs_time_s": round(sum(r["planning_time_ms"] for r in runs) / 1000.0, 1),
        "tracks": [describe_track(name) for name in tracks],
        "runs": runs,
    }
    write_outputs(data, args.out_dir)
    full_run = not args.quick and args.tracks is None
    if full_run and args.out_dir.resolve() == (ROOT / "results").resolve():
        update_readme(render_markdown(data))

    for r in runs:
        print(
            f"{r['track']:32s} {r['planner']:9s} {r['planning_time_ms']:9.1f} ms "
            f"{r['path_length_m']:7.1f} m  clearance {r['min_clearance_m']:.2f} m  "
            f"RRT* {_rrt(r)}"
        )
    print(f"wrote benchmark.json, benchmark.csv and benchmark.md ({wall:.0f} s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
