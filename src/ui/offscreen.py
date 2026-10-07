"""
ui/offscreen.py

Draw a track and a planned path on a surface without opening a window, with
the same drawing code as the viewer. Used to make the figures of the README.
"""

from __future__ import annotations

import pygame

from ui.camera import Camera
from ui.process_pygame import BACKGROUND_COLOR, TEXT_COLOR, base_sizes, draw_frame
from utils.track_utils import compute_world_bounds

CAPTION_FONT_PX = 24
CAPTION_LINE_PX = 20
CAPTION_PAD_PX = 6


def caption_height(line_count):
    """Height in pixels of a caption band holding ``line_count`` lines of text."""
    if line_count <= 0:
        return 0
    return line_count * CAPTION_LINE_PX + 2 * CAPTION_PAD_PX


def render_panel(
    cones,
    path,
    size,
    car_index=-1,
    lines=(),
    caption_px=None,
    display_scale=1.0,
    margin=2.0,
):
    """
    Render one panel: a caption band on top, the track below it.

    Args:
        cones: Track cones with fields "tag", "x", "y".
        path: Planned path to draw, or None.
        size: (width, height) of the whole panel in pixels.
        car_index: Index of the path sample the car sits on; -1 draws no car.
        lines: Text lines of the caption.
        caption_px: Height of the caption band; the default fits ``lines``.
        display_scale: Extra scale applied to the cones and the car.
        margin: Space around the cones, in metres.

    Returns:
        A new ``pygame.Surface``. ``pygame`` must have been initialised.
    """
    width, height = size
    band = caption_height(len(lines)) if caption_px is None else caption_px
    view_size = (width, height - band)

    panel = pygame.Surface(size)
    panel.fill(BACKGROUND_COLOR)
    view = panel.subsurface((0, band, *view_size))
    camera = Camera(compute_world_bounds(cones, margin=margin), view_size)
    draw_frame(
        view,
        camera,
        cones,
        path,
        car_index=car_index,
        sizes=base_sizes(view_size),
        display_scale=display_scale,
    )

    font = pygame.font.Font(None, CAPTION_FONT_PX)
    y = CAPTION_PAD_PX
    for text in lines:
        panel.blit(font.render(text, True, TEXT_COLOR), (CAPTION_PAD_PX, y))
        y += CAPTION_LINE_PX
    return panel
