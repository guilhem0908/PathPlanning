import pygame
import math

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
FPS = 60
PAN_SPEED = 400
LOOKAHEAD_INDEX = 5


def process_pygame(csv_file, cones, world_bounds, path=None):
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Visualisation du circuit et du chemin")

    camera = Camera(world_bounds, screen.get_size())

    base_cone_radius_px = WIDTH * 0.005
    base_start_radius_px = WIDTH * 0.0083

    base_car_width_px = WIDTH * 0.012
    base_car_length_px = WIDTH * 0.024

    display_scale = 1.0

    clock = pygame.time.Clock()
    running = True

    fullscreen = False
    k11_pressed = False
    windowed_size = (WIDTH, HEIGHT)

    dragging = False
    last_mouse_pos = None

    car_path_index = 0

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

                min_dim = min(event.w, event.h)
                base_cone_radius_px = min_dim * 0.0075
                base_start_radius_px = min_dim * 0.0125
                base_car_width_px = min_dim * 0.015
                base_car_length_px = min_dim * 0.030

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
                    dx = mx - lx
                    dy = my - ly
                    camera.pan_pixels(dx, dy)
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

        screen.fill(BACKGROUND_COLOR)

        if path and len(path) > 1:
            screen_points = []
            for pt in path:
                sx, sy = camera.world_to_screen(pt[0], pt[1], screen_size)
                screen_points.append((sx, sy))

            if len(screen_points) >= 2:
                pygame.draw.lines(screen, COLORS["path_line"], False, screen_points, 3)
                pygame.draw.aalines(screen, COLORS["path_line"], False, screen_points)

            if 0 <= car_path_index < len(path):
                cx, cy = path[car_path_index]
                scx, scy = camera.world_to_screen(cx, cy, screen_size)

                target_index = min(len(path) - 1, car_path_index + LOOKAHEAD_INDEX)

                angle = 0.0
                if target_index > car_path_index:
                    nx, ny = path[target_index]

                    angle = math.degrees(math.atan2(ny - cy, nx - cx))

                elif car_path_index > 0:
                    px, py = path[car_path_index - 1]
                    angle = math.degrees(math.atan2(cy - py, cx - px))

                car_w = max(4, int(base_car_width_px * (camera.zoom / camera.base_zoom) * display_scale))
                car_l = max(8, int(base_car_length_px * (camera.zoom / camera.base_zoom) * display_scale))

                car_surf = pygame.Surface((car_l, car_w), pygame.SRCALPHA)
                pygame.draw.rect(car_surf, COLORS["car_body"], (0, 0, car_l, car_w))
                pygame.draw.rect(car_surf, COLORS["car_front"], (car_l * 0.7, 0, car_l * 0.3, car_w))

                rotated_car = pygame.transform.rotate(car_surf, angle)
                rect = rotated_car.get_rect(center=(scx, scy))

                screen.blit(rotated_car, rect)

                car_path_index += 1
                if car_path_index >= len(path):
                    car_path_index = 0

        for c in cones:
            tag = c["tag"]
            wx, wy = c["x"], c["y"]
            sx, sy = camera.world_to_screen(wx, wy, screen_size)

            color = COLORS.get(tag, (200, 200, 200))

            if tag == "car_start":
                base_r = base_start_radius_px
            else:
                base_r = base_cone_radius_px

            final_radius = int(base_r * (camera.zoom / camera.base_zoom) * display_scale)
            radius = max(2, final_radius)

            pygame.draw.circle(screen, color, (sx, sy), radius)

        font = pygame.font.SysFont("Arial", 20)
        txt = font.render(
            "Zoom: molette | Déplacement: Clic-gauche+glisser | Taille: Flèches | Reset: R",
            True,
            (200, 200, 200), )
        screen.blit(txt, (10, 10))

        pygame.display.flip()

    pygame.quit()
