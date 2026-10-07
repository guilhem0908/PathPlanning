"""
ui/process_pygame.py

Pygame viewer: draws the cones and the planned path, and moves a car along
the path.

The car is an animation, not a simulation: it advances by a fixed number of
path samples per frame and points towards a sample a little further ahead.

Controls:
- Zoom: mouse wheel (about the cursor)
- Pan: left click + drag
- Size of the cones and of the car: arrow keys
- Reset view and car: R
- Fullscreen: F11
- Quit: ESC or window close
"""

import math
from pathlib import Path

import pygame

from ui.camera import Camera

WIDTH, HEIGHT = 1200, 800
COLORS = {
    "yellow": (255, 255, 0),
    "blue": (50, 100, 255),
    "big_orange": (255, 150, 0),
    "car_start": (0, 255, 0),
    "path_line": (255, 50, 50),
    "car_body": (255, 0, 255),
    "car_front": (200, 0, 200),
}
BACKGROUND_COLOR = (30, 30, 30)
TEXT_COLOR = (200, 200, 200)
FPS = 60
LOOKAHEAD_INDEX = 5
HUD_TEXT = "Zoom: wheel | Pan: left-drag | Size: arrows | Reset: R | Fullscreen: F11"


def base_sizes(screen_size):
    """Pixel sizes of the cones and of the car for a window size, at fit zoom."""
    min_dim = min(screen_size)
    return {
        "cone_radius": min_dim * 0.0075,
        "start_radius": min_dim * 0.0125,
        "car_width": min_dim * 0.015,
        "car_length": min_dim * 0.030,
    }


def car_heading_deg(path, index, lookahead=LOOKAHEAD_INDEX):
    """
    Heading of the car at a path index, in degrees.

    The car points towards the sample ``lookahead`` indices further along the
    path, or along the last segment once it reaches the end.
    """
    if len(path) < 2:
        return 0.0
    cx, cy = path[index]
    target_index = min(len(path) - 1, index + lookahead)
    if target_index > index:
        nx, ny = path[target_index]
        return math.degrees(math.atan2(ny - cy, nx - cx))
    px, py = path[index - 1]
    return math.degrees(math.atan2(cy - py, cx - px))


def draw_frame(
    screen, camera, cones, path=None, car_index=0, sizes=None, display_scale=1.0, lines=()
):
    """
    Draw one frame: path, car, cones and text.

    Args:
        screen: Target surface (cleared first).
        camera: World-to-screen camera.
        cones: Track cones with fields "tag", "x", "y".
        path: Planned path as a sequence of (x, y), or None.
        car_index: Index of the path sample the car sits on.
        sizes: Result of ``base_sizes``; computed from the surface if None.
        display_scale: Extra scale applied to the cones and the car.
        lines: Text lines drawn in the top-left corner.
    """
    screen_size = screen.get_size()
    if sizes is None:
        sizes = base_sizes(screen_size)
    scale = (camera.zoom / camera.base_zoom) * display_scale

    screen.fill(BACKGROUND_COLOR)

    if path and len(path) > 1:
        screen_points = [camera.world_to_screen(pt[0], pt[1], screen_size) for pt in path]
        pygame.draw.lines(screen, COLORS["path_line"], False, screen_points, 3)
        pygame.draw.aalines(screen, COLORS["path_line"], False, screen_points)

        if 0 <= car_index < len(path):
            cx, cy = path[car_index]
            scx, scy = camera.world_to_screen(cx, cy, screen_size)
            angle = car_heading_deg(path, car_index)

            car_w = max(4, int(sizes["car_width"] * scale))
            car_l = max(8, int(sizes["car_length"] * scale))
            car_surf = pygame.Surface((car_l, car_w), pygame.SRCALPHA)
            pygame.draw.rect(car_surf, COLORS["car_body"], (0, 0, car_l, car_w))
            pygame.draw.rect(car_surf, COLORS["car_front"], (car_l * 0.7, 0, car_l * 0.3, car_w))

            rotated_car = pygame.transform.rotate(car_surf, angle)
            screen.blit(rotated_car, rotated_car.get_rect(center=(scx, scy)))

    for c in cones:
        tag = c["tag"]
        sx, sy = camera.world_to_screen(c["x"], c["y"], screen_size)
        base_r = sizes["start_radius"] if tag == "car_start" else sizes["cone_radius"]
        radius = max(2, int(base_r * scale))
        pygame.draw.circle(screen, COLORS.get(tag, (200, 200, 200)), (sx, sy), radius)

    if lines:
        font = pygame.font.Font(None, 24)
        y = 10
        for text in lines:
            screen.blit(font.render(text, True, TEXT_COLOR), (10, y))
            y += font.get_linesize()


def process_pygame(csv_file, cones, world_bounds, path=None, info=None):
    """
    Open the viewer window.

    Args:
        csv_file: Track file, shown in the window title.
        cones: Track cones with fields "tag", "x", "y".
        world_bounds: (min_x, max_x, min_y, max_y) to fit in the window.
        path: Planned path to draw and to move the car along.
        info: Optional line of text shown above the key help.
    """
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption(f"Track and planned path - {Path(str(csv_file)).stem}")

    camera = Camera(world_bounds, screen.get_size())
    sizes = base_sizes(screen.get_size())
    display_scale = 1.0

    clock = pygame.time.Clock()
    running = True

    fullscreen = False
    k11_pressed = False
    windowed_size = (WIDTH, HEIGHT)

    dragging = False
    last_mouse_pos = None

    car_path_index = 0
    hud = ([info] if info else []) + [HUD_TEXT]

    while running:
        dt = clock.tick(FPS) / 1000.0
        screen_size = screen.get_size()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                if k11_pressed:
                    k11_pressed = False
                else:
                    screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

                sizes = base_sizes((event.w, event.h))
                camera = Camera(world_bounds, screen.get_size())

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    dragging = True
                    last_mouse_pos = event.pos

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False
                    last_mouse_pos = None

            elif event.type == pygame.MOUSEMOTION:
                if dragging and last_mouse_pos is not None:
                    mx, my = event.pos
                    lx, ly = last_mouse_pos
                    camera.pan_pixels(mx - lx, my - ly)
                    last_mouse_pos = event.pos

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        windowed_size = screen.get_size()
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode(windowed_size, pygame.RESIZABLE)
                    k11_pressed = True

                elif event.key == pygame.K_r:
                    camera = Camera(world_bounds, screen.get_size())
                    display_scale = 1.0
                    car_path_index = 0

            elif event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    camera.change_zoom(1.1, pygame.mouse.get_pos(), screen_size)
                elif event.y < 0:
                    camera.change_zoom(1 / 1.1, pygame.mouse.get_pos(), screen_size)

        keys = pygame.key.get_pressed()
        scale_speed = 2.0 * dt
        if keys[pygame.K_UP] or keys[pygame.K_RIGHT]:
            display_scale += scale_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_LEFT]:
            display_scale -= scale_speed
        display_scale = max(0.1, min(display_scale, 10.0))

        draw_frame(screen, camera, cones, path, car_path_index, sizes, display_scale, hud)

        if path and len(path) > 1:
            car_path_index += 1
            if car_path_index >= len(path):
                car_path_index = 0

        pygame.display.flip()

    pygame.quit()
