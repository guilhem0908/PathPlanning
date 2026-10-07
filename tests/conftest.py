"""Shared fixtures: a synthetic ring track whose centre line is known exactly."""

from __future__ import annotations

import math
import os

import pytest

# The viewer tests draw on off-screen surfaces.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

RING_CENTRE_RADIUS_M = 10.0
RING_HALF_WIDTH_M = 1.8
RING_CONES_PER_ROW = 48


def make_ring(half_width_m=RING_HALF_WIDTH_M):
    """Blue cones on the inner circle, yellow on the outer one, start on the loop."""
    inner = RING_CENTRE_RADIUS_M - half_width_m
    outer = RING_CENTRE_RADIUS_M + half_width_m
    cones = []
    for i in range(RING_CONES_PER_ROW):
        angle = 2.0 * math.pi * i / RING_CONES_PER_ROW
        cones.append({"tag": "blue", "x": inner * math.cos(angle), "y": inner * math.sin(angle)})
        cones.append({"tag": "yellow", "x": outer * math.cos(angle), "y": outer * math.sin(angle)})
    cones.append({"tag": "car_start", "x": RING_CENTRE_RADIUS_M, "y": 0.0})
    return cones


@pytest.fixture
def ring_cones():
    """The ring with its default width of 3.6 m."""
    return make_ring()
