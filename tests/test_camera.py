"""World/screen transforms of the viewer camera."""

from __future__ import annotations

import pytest

from ui.camera import Camera, compute_fit_zoom

SCREEN = (1200, 800)
BOUNDS = (-10.0, 30.0, -5.0, 15.0)


def test_fit_zoom_is_set_by_the_tighter_axis():
    assert compute_fit_zoom(BOUNDS, SCREEN) == pytest.approx(30.0)  # 1200 / 40 beats 800 / 20


def test_the_centre_of_the_world_bounds_maps_to_the_centre_of_the_screen():
    camera = Camera(BOUNDS, SCREEN)
    assert camera.world_to_screen(10.0, 5.0, SCREEN) == (600, 400)


def test_screen_y_points_down_while_world_y_points_up():
    camera = Camera(BOUNDS, SCREEN)
    _, sy_low = camera.world_to_screen(10.0, 0.0, SCREEN)
    _, sy_high = camera.world_to_screen(10.0, 10.0, SCREEN)
    assert sy_high < sy_low


def test_world_to_screen_and_back_round_trip_within_a_pixel():
    camera = Camera(BOUNDS, SCREEN)
    camera.change_zoom(2.5, (300, 200), SCREEN)
    camera.pan_pixels(40, -25)
    for point in [(-3.2, 1.1), (12.0, 9.5), (27.5, -4.0)]:
        sx, sy = camera.world_to_screen(*point, SCREEN)
        wx, wy = camera.screen_to_world(sx, sy, SCREEN)
        assert wx == pytest.approx(point[0], abs=1.0 / camera.zoom)
        assert wy == pytest.approx(point[1], abs=1.0 / camera.zoom)


def test_zooming_keeps_the_world_point_under_the_cursor_fixed():
    camera = Camera(BOUNDS, SCREEN)
    cursor = (850, 150)
    before = camera.screen_to_world(*cursor, SCREEN)
    camera.change_zoom(1.7, cursor, SCREEN)
    after = camera.screen_to_world(*cursor, SCREEN)
    assert after == pytest.approx(before)


def test_zoom_is_clamped_between_a_tenth_and_ten_times_the_fit_zoom():
    camera = Camera(BOUNDS, SCREEN)
    for _ in range(100):
        camera.change_zoom(1.5, (600, 400), SCREEN)
    assert camera.zoom == pytest.approx(10.0 * camera.base_zoom)
    for _ in range(200):
        camera.change_zoom(1 / 1.5, (600, 400), SCREEN)
    assert camera.zoom == pytest.approx(0.1 * camera.base_zoom)


def test_dragging_right_moves_the_world_right_on_screen():
    camera = Camera(BOUNDS, SCREEN)
    x_before, _ = camera.world_to_screen(0.0, 0.0, SCREEN)
    camera.pan_pixels(50, 0)
    x_after, _ = camera.world_to_screen(0.0, 0.0, SCREEN)
    assert x_after - x_before == pytest.approx(50, abs=1)
