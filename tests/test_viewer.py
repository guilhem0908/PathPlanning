"""Off-screen drawing of the viewer (no window is opened)."""

from __future__ import annotations

import pygame
import pytest

from ui.camera import Camera
from ui.process_pygame import BACKGROUND_COLOR, COLORS, base_sizes, car_heading_deg, draw_frame

SIZE = (320, 240)
BOUNDS = (-10.0, 10.0, -7.5, 7.5)


@pytest.fixture
def surface():
    pygame.init()
    yield pygame.Surface(SIZE)
    pygame.quit()


def count_pixels(surface, colour):
    width, height = surface.get_size()
    return sum(
        surface.get_at((x, y))[:3] == colour for x in range(width) for y in range(height)
    )


def test_heading_points_towards_the_sample_ahead():
    path = [(float(i), 0.0) for i in range(20)] + [(19.0, float(i)) for i in range(1, 20)]
    assert car_heading_deg(path, 0) == pytest.approx(0.0)
    assert car_heading_deg(path, 19 + 5) == pytest.approx(90.0)


def test_heading_at_the_end_follows_the_last_segment():
    path = [(0.0, 0.0), (0.0, 1.0), (0.0, 2.0)]
    assert car_heading_deg(path, 2) == pytest.approx(90.0)


def test_heading_of_a_single_point_is_zero():
    assert car_heading_deg([(1.0, 1.0)], 0) == 0.0


def test_sizes_scale_with_the_smaller_window_side():
    assert base_sizes((800, 400))["cone_radius"] == pytest.approx(3.0)
    assert base_sizes((400, 800)) == base_sizes((800, 400))


def test_a_frame_shows_the_path_and_every_cone_colour(surface):
    camera = Camera(BOUNDS, SIZE)
    cones = [
        {"tag": "blue", "x": -5.0, "y": 0.0},
        {"tag": "yellow", "x": 5.0, "y": 0.0},
        {"tag": "car_start", "x": 0.0, "y": 5.0},
    ]
    path = [(-8.0, -6.0), (8.0, -6.0), (8.0, 6.0), (-8.0, 6.0)]
    draw_frame(surface, camera, cones, path, car_index=1)
    for key in ("blue", "yellow", "car_start", "path_line", "car_body"):
        assert count_pixels(surface, COLORS[key]) > 0, key


def test_a_frame_without_a_path_draws_only_cones(surface):
    camera = Camera(BOUNDS, SIZE)
    draw_frame(surface, camera, [{"tag": "blue", "x": 0.0, "y": 0.0}], path=None)
    assert count_pixels(surface, COLORS["path_line"]) == 0
    assert count_pixels(surface, COLORS["blue"]) > 0


def test_a_frame_clears_the_previous_one(surface):
    camera = Camera(BOUNDS, SIZE)
    surface.fill((255, 255, 255))
    draw_frame(surface, camera, [])
    assert count_pixels(surface, BACKGROUND_COLOR) == SIZE[0] * SIZE[1]
