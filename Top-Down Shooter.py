import math

import pygame


# -----------------------------------------------------------------------------
# MOVEMENT LABORATORY SETTINGS
# These are safe values to experiment with while learning the project.
# -----------------------------------------------------------------------------
FPS = 60
PLAYER_SPEED = 250
PLAYER_SIZE = 55
WORLD_WIDTH = 2300
WORLD_HEIGHT = 1600

BACKGROUND_COLOR = (31, 37, 46)
GRID_COLOR = (42, 49, 60)
WALL_COLOR = (104, 114, 128)
WALL_EDGE_COLOR = (180, 192, 208)
PLAYER_COLOR = (48, 150, 220)
PLAYER_EDGE_COLOR = (193, 232, 255)
TEXT_COLOR = (235, 241, 248)


def make_walls():
    """Create the laboratory's boundary and obstacle collision rectangles."""
    thickness = 80

    return [
        # Outer boundary
        pygame.Rect(0, 0, WORLD_WIDTH, thickness),
        pygame.Rect(0, WORLD_HEIGHT - thickness, WORLD_WIDTH, thickness),
        pygame.Rect(0, 0, thickness, WORLD_HEIGHT),
        pygame.Rect(WORLD_WIDTH - thickness, 0, thickness, WORLD_HEIGHT),

        # Interior test walls
        pygame.Rect(420, 300, 520, 70),
        pygame.Rect(870, 370, 70, 420),
        pygame.Rect(1250, 230, 620, 70),
        pygame.Rect(1250, 300, 70, 390),
        pygame.Rect(420, 1050, 610, 70),
        pygame.Rect(1430, 930, 70, 420),
        pygame.Rect(1500, 1280, 480, 70),

        # Small pieces of cover
        pygame.Rect(1090, 820, 110, 110),
        pygame.Rect(1770, 630, 150, 90),
        pygame.Rect(650, 760, 120, 120),
    ]


def get_movement_input():
    """Turn WASD keyboard input into a direction with a maximum length of 1."""
    keys = pygame.key.get_pressed()
    direction = pygame.Vector2(
        int(keys[pygame.K_d]) - int(keys[pygame.K_a]),
        int(keys[pygame.K_s]) - int(keys[pygame.K_w]),
    )

    # Normalizing prevents diagonal movement from being faster than straight movement.
    if direction.length_squared() > 0:
        direction = direction.normalize()

    return direction


def move_player(position, movement, walls):
    """Move on each axis separately so the player slides naturally along walls."""
    player_rect = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)

    position.x += movement.x
    player_rect.center = (round(position.x), round(position.y))
    for wall in walls:
        if player_rect.colliderect(wall):
            if movement.x > 0:
                player_rect.right = wall.left
            elif movement.x < 0:
                player_rect.left = wall.right
            position.x = player_rect.centerx

    position.y += movement.y
    player_rect.center = (round(position.x), round(position.y))
    for wall in walls:
        if player_rect.colliderect(wall):
            if movement.y > 0:
                player_rect.bottom = wall.top
            elif movement.y < 0:
                player_rect.top = wall.bottom
            position.y = player_rect.centery

    return player_rect


def calculate_camera(player_position, screen_size):
    """Center the camera on the player without showing space outside the map."""
    screen_width, screen_height = screen_size
    maximum_x = max(0, WORLD_WIDTH - screen_width)
    maximum_y = max(0, WORLD_HEIGHT - screen_height)

    camera_x = player_position.x - screen_width / 2
    camera_y = player_position.y - screen_height / 2

    return pygame.Vector2(
        max(0, min(camera_x, maximum_x)),
        max(0, min(camera_y, maximum_y)),
    )


def draw_grid(screen, camera):
    """Draw a simple floor grid so movement and camera motion are easy to judge."""
    grid_size = 100
    screen_width, screen_height = screen.get_size()
    first_x = int(camera.x // grid_size) * grid_size
    first_y = int(camera.y // grid_size) * grid_size

    for world_x in range(first_x, int(camera.x + screen_width) + grid_size, grid_size):
        screen_x = round(world_x - camera.x)
        pygame.draw.line(screen, GRID_COLOR, (screen_x, 0), (screen_x, screen_height))

    for world_y in range(first_y, int(camera.y + screen_height) + grid_size, grid_size):
        screen_y = round(world_y - camera.y)
        pygame.draw.line(screen, GRID_COLOR, (0, screen_y), (screen_width, screen_y))


def draw_world(screen, walls, camera):
    """Draw the laboratory obstacles at their camera-adjusted positions."""
    draw_grid(screen, camera)

    for wall in walls:
        screen_rect = wall.move(-round(camera.x), -round(camera.y))
        pygame.draw.rect(screen, WALL_COLOR, screen_rect, border_radius=5)
        pygame.draw.rect(screen, WALL_EDGE_COLOR, screen_rect, width=3, border_radius=5)


def draw_player(screen, player_position, aim_angle, camera):
    """Draw a readable placeholder character facing toward the mouse."""
    center = pygame.Vector2(player_position - camera)
    shadow_center = center + pygame.Vector2(7, 9)
    radius = PLAYER_SIZE // 2

    pygame.draw.circle(screen, (15, 18, 24), shadow_center, radius)
    pygame.draw.circle(screen, PLAYER_COLOR, center, radius)
    pygame.draw.circle(screen, PLAYER_EDGE_COLOR, center, radius, width=3)

    facing = pygame.Vector2(math.cos(aim_angle), math.sin(aim_angle))
    side = pygame.Vector2(-facing.y, facing.x)
    arrow_tip = center + facing * 34
    arrow_left = center - facing * 5 + side * 10
    arrow_right = center - facing * 5 - side * 10
    pygame.draw.polygon(screen, PLAYER_EDGE_COLOR, (arrow_tip, arrow_left, arrow_right))


def draw_crosshair(screen, mouse_position):
    """Draw a small aiming reticle at the mouse position."""
    x, y = mouse_position
    color = (118, 211, 255)
    pygame.draw.circle(screen, color, mouse_position, 9, width=2)
    pygame.draw.line(screen, color, (x - 15, y), (x - 5, y), width=2)
    pygame.draw.line(screen, color, (x + 5, y), (x + 15, y), width=2)
    pygame.draw.line(screen, color, (x, y - 15), (x, y - 5), width=2)
    pygame.draw.line(screen, color, (x, y + 5), (x, y + 15), width=2)


def draw_debug_panel(screen, font, player_position, aim_angle, current_fps):
    """Show the values that matter while testing movement."""
    lines = [
        "MOVEMENT LABORATORY 0.1",
        "WASD: Move    Mouse: Aim    ESC: Quit",
        f"Position: ({player_position.x:.1f}, {player_position.y:.1f})",
        f"Facing: {math.degrees(aim_angle):.1f} degrees",
        f"Speed setting: {PLAYER_SPEED} pixels/second",
        f"FPS: {current_fps:.0f}",
    ]

    panel = pygame.Surface((470, 178), pygame.SRCALPHA)
    panel.fill((10, 13, 18, 205))
    screen.blit(panel, (18, 18))

    for index, line in enumerate(lines):
        rendered_text = font.render(line, True, TEXT_COLOR)
        screen.blit(rendered_text, (34, 32 + index * 25))


def main():
    pygame.init()

    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Riftbound - Movement Laboratory")
    pygame.mouse.set_visible(False)

    clock = pygame.time.Clock()
    debug_font = pygame.font.Font(None, 26)
    walls = make_walls()

    player_position = pygame.Vector2(260, 240)
    aim_angle = 0.0
    game_running = True

    while game_running:
        # Delta time keeps movement speed consistent even if the frame rate changes.
        delta_time = min(clock.tick(FPS) / 1000.0, 0.05)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                game_running = False

        movement_direction = get_movement_input()
        movement = movement_direction * PLAYER_SPEED * delta_time
        move_player(player_position, movement, walls)

        camera = calculate_camera(player_position, screen.get_size())
        mouse_screen_position = pygame.Vector2(pygame.mouse.get_pos())
        mouse_world_position = mouse_screen_position + camera
        aim_vector = mouse_world_position - player_position
        if aim_vector.length_squared() > 0:
            aim_angle = math.atan2(aim_vector.y, aim_vector.x)

        screen.fill(BACKGROUND_COLOR)
        draw_world(screen, walls, camera)
        draw_player(screen, player_position, aim_angle, camera)
        draw_debug_panel(screen, debug_font, player_position, aim_angle, clock.get_fps())
        draw_crosshair(screen, pygame.mouse.get_pos())

        pygame.display.flip()

    pygame.mouse.set_visible(True)
    pygame.quit()


if __name__ == "__main__":
    main()