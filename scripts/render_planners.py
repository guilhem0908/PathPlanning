"""
scripts/render_planners.py

Draw the three planners on several tracks into one picture.

One row per track, one column per planner, same seed as the benchmark. Each
panel shows the planned line, the length of the loop and the closest approach
to a cone centre, rendered off-screen with the viewer's drawing code.

Usage (from the repository root):
    python scripts/render_planners.py
    python scripts/render_planners.py --tracks small_track peanut spa
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import List, Tuple

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pygame  # noqa: E402

from metrics import min_clearance, path_length  # noqa: E402
from planners import PLANNERS, plan, split_cones  # noqa: E402
from ui.offscreen import caption_height, render_panel  # noqa: E402
from utils.track_catalog import resolve_track  # noqa: E402
from utils.track_utils import compute_world_bounds, get_start_pos, load_track  # noqa: E402

SEED = 0
GAP = 2
GAP_COLOR = (70, 70, 70)
MARGIN_M = 2.0
MIN_VIEW_HEIGHT = 150
MAX_VIEW_HEIGHT = 420
CAPTION_LINES = 3


def row_height(cones, panel_width: int) -> int:
    """Panel height: caption band plus a view that fits the track at ``panel_width``."""
    min_x, max_x, min_y, max_y = compute_world_bounds(cones, margin=MARGIN_M)
    view = panel_width * (max_y - min_y) / (max_x - min_x)
    view = max(MIN_VIEW_HEIGHT, min(MAX_VIEW_HEIGHT, view))
    return int(view) + caption_height(CAPTION_LINES)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--tracks", nargs="+", default=["small_track", "peanut", "spa"])
    parser.add_argument("--panel-width", type=int, default=430)
    parser.add_argument("--out", type=Path, default=ROOT / "docs" / "planners.png")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    pygame.init()

    rows: List[Tuple[str, List[pygame.Surface]]] = []
    for name in args.tracks:
        track = resolve_track(name)
        cones = load_track(track)
        yellow, blue = split_cones(cones)
        height = row_height(cones, args.panel_width)
        panels = []
        for key in PLANNERS:
            result = plan(key, cones, get_start_pos(cones), seed=SEED)
            lines = [f"{track.stem}   {key}"]
            if result.path:
                clearance = min_clearance(result.path, yellow + blue)
                lines.append(f"{path_length(result.path):.0f} m, closest cone {clearance:.2f} m")
                if result.rrt_segments:
                    lines.append(f"RRT* solved {result.rrt_solved} / {result.rrt_segments}")
            panels.append(
                render_panel(
                    cones,
                    result.path,
                    (args.panel_width, height),
                    lines=lines,
                    caption_px=caption_height(CAPTION_LINES),
                    margin=MARGIN_M,
                )
            )
        rows.append((track.stem, panels))

    columns = len(PLANNERS)
    width = columns * args.panel_width + (columns - 1) * GAP
    total_height = sum(panels[0].get_height() for _, panels in rows) + GAP * (len(rows) - 1)
    figure = pygame.Surface((width, total_height))
    figure.fill(GAP_COLOR)

    y = 0
    for _, panels in rows:
        for column, panel in enumerate(panels):
            figure.blit(panel, (column * (args.panel_width + GAP), y))
        y += panels[0].get_height() + GAP

    args.out.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(figure, str(args.out))
    pygame.quit()

    shown = args.out.relative_to(ROOT) if args.out.is_relative_to(ROOT) else args.out
    print(f"{shown}: {width} x {total_height} px, {len(rows)} tracks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
