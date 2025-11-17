import pygame

from ui.camera import Camera
from utils.track_utils import load_track, compute_world_bounds


WIDTH, HEIGHT = 1200, 800
COLORS = {
    "yellow": (255, 255, 0),
    "blue": (50, 100, 255),
    "big_orange": (255, 150, 0),
    "car_start": (0, 255, 0),
}
BACKGROUND_COLOR = (30, 30, 30)
FPS = 60
PAN_SPEED = 400


def process_pygame(csv_file):
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Visualisation du circuit")

    cones = load_track(csv_file)
    world_bounds = compute_world_bounds(cones)

    camera = Camera(world_bounds, screen.get_size())

    base_cone_radius_px = WIDTH * 0.005
    base_start_radius_px = WIDTH * 0.0083

    clock = pygame.time.Clock()
    running = True

    fullscreen = False
    k11_pressed = False
    windowed_size = (WIDTH, HEIGHT)

    dragging = False
    last_mouse_pos = None

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
                base_cone_radius_px = min(event.w, event.h) * 0.0075
                base_start_radius_px = min(event.w, event.h) * 0.0125
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

            elif event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    camera.change_zoom(1.1, pygame.mouse.get_pos(), screen_size)
                elif event.y < 0:
                    camera.change_zoom(1 / 1.1, pygame.mouse.get_pos(), screen_size)

        keys = pygame.key.get_pressed()
        pan_speed_px = PAN_SPEED * dt

        if keys[pygame.K_LEFT]:
            camera.pan_pixels(pan_speed_px, 0)
        if keys[pygame.K_RIGHT]:
            camera.pan_pixels(-pan_speed_px, 0)
        if keys[pygame.K_UP]:
            camera.pan_pixels(0, pan_speed_px)
        if keys[pygame.K_DOWN]:
            camera.pan_pixels(0, -pan_speed_px)

        screen.fill(BACKGROUND_COLOR)

        for c in cones:
            tag = c["tag"]
            wx, wy = c["x"], c["y"]
            sx, sy = camera.world_to_screen(wx, wy, screen_size)

            color = COLORS.get(tag, (200, 200, 200))

            if tag == "car_start":
                radius = max(3, int(base_start_radius_px * camera.zoom / camera.base_zoom))
            else:
                radius = max(2, int(base_cone_radius_px * camera.zoom / camera.base_zoom))

            pygame.draw.circle(screen, color, (sx, sy), radius)

        font = pygame.font.SysFont("Arial", 20)
        txt = font.render(
            "Zoom: molette | Déplacement: flèches ou clic-gauche + glisser | Plein écran: F11 | Reset: R",
            True,
            (200, 200, 200),)
        screen.blit(txt, (10, 10))

        pygame.display.flip()

    pygame.quit()