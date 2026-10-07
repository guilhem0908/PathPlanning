"""
scripts/record_gif.py

Record the three planners on one track to a GIF, without opening a window.

Pygame draws each frame on an off-screen surface (SDL "dummy" video driver)
with the viewer's own drawing code, every frame is written as a PNG and
ffmpeg assembles the GIF. One panel per planner, same track, same seed as the
benchmark.

The cars move at the same constant speed along their own line, so the
shortest line is finished first. This is an animation, not a vehicle model.

Usage (from the repository root, ffmpeg on the PATH):
    python scripts/record_gif.py --track small_track --out docs/planners.gif
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pygame  # noqa: E402

from metrics import densify, min_clearance, path_length  # noqa: E402
from planners import PLANNERS, plan, split_cones  # noqa: E402
from ui.offscreen import render_panel  # noqa: E402
from utils.track_catalog import resolve_track  # noqa: E402
from utils.track_utils import get_start_pos, load_track  # noqa: E402

SEED = 0
SAMPLE_STEP_M = 0.25
SEPARATOR = (70, 70, 70)
HOLD_SECONDS = 1.0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--track", default="small_track")
    parser.add_argument("--panel-width", type=int, default=296)
    parser.add_argument("--panel-height", type=int, default=300)
    parser.add_argument("--speed", type=float, default=10.0, help="metres per second of the GIF")
    parser.add_argument("--fps", type=int, default=20)
    parser.add_argument("--colors", type=int, default=32, help="GIF palette size")
    parser.add_argument("--out", type=Path, default=ROOT / "docs" / "planners.gif")
    parser.add_argument("--keep-frames", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if shutil.which("ffmpeg") is None:
        print("ffmpeg was not found on the PATH", file=sys.stderr)
        return 1

    track = resolve_track(args.track)
    cones = load_track(track)
    yellow, blue = split_cones(cones)
    start = get_start_pos(cones)

    panels = []
    for key in PLANNERS:
        result = plan(key, cones, start, seed=SEED)
        samples = [tuple(p) for p in densify(result.path, SAMPLE_STEP_M)]
        clearance = min_clearance(result.path, yellow + blue)
        panels.append(
            {
                "key": key,
                "samples": samples,
                "lines": [
                    f"{key}   {path_length(result.path):.0f} m",
                    f"closest cone {clearance:.2f} m",
                ],
            }
        )

    pygame.init()
    size = (args.panel_width, args.panel_height)
    screen = pygame.Surface((size[0] * len(panels) + len(panels) - 1, size[1]))

    frames_dir = ROOT / "build" / "gif_frames"
    if frames_dir.exists():
        shutil.rmtree(frames_dir)
    frames_dir.mkdir(parents=True)

    samples_per_frame = args.speed / (SAMPLE_STEP_M * args.fps)
    longest = max(len(p["samples"]) for p in panels)
    frame_count = int(longest / samples_per_frame) + 1 + int(HOLD_SECONDS * args.fps)

    for index in range(frame_count):
        screen.fill(SEPARATOR)
        for column, panel in enumerate(panels):
            samples = panel["samples"]
            car_index = min(len(samples) - 1, int(index * samples_per_frame))
            surface = render_panel(
                cones,
                samples,
                size,
                car_index=car_index,
                lines=panel["lines"],
                display_scale=2.0,
            )
            screen.blit(surface, (column * (size[0] + 1), 0))
        pygame.image.save(screen, str(frames_dir / f"{index:05d}.png"))

    pygame.quit()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    palette = (
        f"split[a][b];[a]palettegen=max_colors={args.colors}:stats_mode=diff[p];"
        "[b][p]paletteuse=dither=none:diff_mode=rectangle"
    )
    command = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-framerate", str(args.fps),
        "-i", str(frames_dir / "%05d.png"),
        "-vf", palette,
        str(args.out),
    ]
    subprocess.run(command, check=True)
    if not args.keep_frames:
        shutil.rmtree(frames_dir)

    shown = args.out.relative_to(ROOT) if args.out.is_relative_to(ROOT) else args.out
    print(f"{shown}: {frame_count} frames, {args.out.stat().st_size / 1024:.0f} kB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
