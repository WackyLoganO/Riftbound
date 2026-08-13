import math
import random

import pygame


# -----------------------------------------------------------------------------
# MOVEMENT LABORATORY SETTINGS
# These are safe values to experiment with while learning the project.
# -----------------------------------------------------------------------------
FPS = 60
PLAYER_SPEED = 250
SPRINT_MULTIPLIER = 1.3
PLAYER_SIZE = 55
WORLD_WIDTH = 2400
WORLD_HEIGHT = 1600

MAX_STAMINA = 100
SPRINT_STAMINA_DRAIN_PER_SECOND = 30
SPRINT_STAMINA_REGEN_PER_SECOND = 15
SPRINT_RECOVERY_THRESHOLD = 20

# -----------------------------------------------------------------------------
# SHOOTING LABORATORY SETTINGS
# Keeping weapon values together makes balancing and adding weapons easier.
# -----------------------------------------------------------------------------
PISTOL = {
    "slot": 1,
    "name": "Pistol",
    "fire_mode": "semi",
    "projectiles_per_shot": 1,
    "damage": 25,
    "bullet_speed": 3500,
    "bullet_radius": 5,
    "magazine_size": 12,
    "starting_reserve_ammo": 36 ,
    "seconds_per_shot": 0.20,
    "reload_time": 1.2,
    "standing_spread": 0.03,
    "walking_spread": 0.06,
    "running_spread": 0.10,
    "sustained_spread_per_shot": 0.0,
    "maximum_sustained_spread": 0.0,
    "tap_camera_shake": 3.0,
    "sustained_camera_kick": 0.0,
    "sustained_camera_sway": 0.0,
}

RIFLE = {
    "slot": 2,
    "name": "Rifle",
    "fire_mode": "automatic",
    "projectiles_per_shot": 1,
    "damage": 20,
    "bullet_speed": 4200,
    "bullet_radius": 4,
    "magazine_size": 30,
    "starting_reserve_ammo": 90,
    "seconds_per_shot": 0.095,
    "reload_time": 1.8,
    "standing_spread": 0.02,
    "walking_spread": 0.05,
    "running_spread": 0.09,
    "sustained_spread_per_shot": 0.007,
    "maximum_sustained_spread": 0.05,
    "tap_camera_shake": 4.0,
    "sustained_camera_kick": 135.0,
    "sustained_camera_sway": 70.0,
}

SHOTGUN = {
    "slot": 3,
    "name": "Shotgun",
    "fire_mode": "semi",
    "projectiles_per_shot": 8,
    "damage": 14,
    "damage_falloff_start": 300,
    "damage_falloff_end": 1000,
    "minimum_damage_multiplier": 0.25,
    "bullet_speed": 3000,
    "bullet_radius": 4,
    "magazine_size": 6,
    "starting_reserve_ammo": 24,
    "seconds_per_shot": 0.75,
    "reload_time": 2.4,
    "standing_spread": 0.12,
    "walking_spread": 0.17,
    "running_spread": 0.24,
    "sustained_spread_per_shot": 0.0,
    "maximum_sustained_spread": 0.0,
    "tap_camera_shake": 6.0,
    "sustained_camera_kick": 0.0,
    "sustained_camera_sway": 0.0,
}

WEAPONS = [PISTOL, RIFLE, SHOTGUN]

CAMERA_RECOIL_SPRING = 90.0
CAMERA_RECOIL_DAMPING = 12.0
CAMERA_SHAKE_DECAY_PER_SECOND = 32.0

# At 100% spread, a shot could deviate by as much as 45 degrees either way.
MAX_SPREAD_DEGREES = 45

# Bullet marks persist in world space. The oldest mark is removed when this
# limit is reached so long matches do not collect an unlimited number of them.
MAX_BULLET_MARKS = 300
BULLET_MARK_MIN_RADIUS = 5
BULLET_MARK_MAX_RADIUS = 8
BULLET_MARK_LIFETIME = 12.0
BULLET_MARK_FADE_TIME = 4.0
BULLET_MARK_MIN_LIFETIME = 4.0
BULLET_MARK_NEAR_DISTANCE = 200
BULLET_MARK_FAR_DISTANCE = 1400

# -----------------------------------------------------------------------------
# VISION LABORATORY SETTINGS
# The player has 360-degree vision, but solid walls stop every vision ray.
# Extra rays are aimed beside wall corners so shadows do not have large gaps.
# -----------------------------------------------------------------------------
VISION_BASE_RAY_COUNT = 96
VISION_CORNER_ANGLE_OFFSET = 0.0001
VISION_MAX_DISTANCE = math.hypot(WORLD_WIDTH, WORLD_HEIGHT)
# The alpha value keeps concealed terrain readable instead of covering it.
# Visible terrain keeps its normal color; concealed terrain is darkened.
VISION_SHADOW_COLOR = (10, 12, 18, 175)
# Partially visible walls receive color only this far past the sight boundary.
# A completely unobstructed wall is colored in full regardless of this value.
VISIBLE_WALL_COLOR_DEPTH = 36
# Visibility masks are calculated at one quarter of the screen resolution and
# enlarged afterward. This preserves partial visibility without processing
# millions of extra transparent pixels several times per frame.
VISION_MASK_SCALE = 0.25

TARGET_MAX_HEALTH = 100
TARGET_RADIUS = 32
TARGET_RESPAWN_TIME = 1.25

BACKGROUND_COLOR = (31, 37, 46)
GRID_COLOR = (42, 49, 60)
WALL_COLOR = (104, 114, 128)
WALL_EDGE_COLOR = (180, 192, 208)
HIDDEN_WALL_COLOR = (55, 61, 71)
HIDDEN_WALL_EDGE_COLOR = (82, 90, 103)
PLAYER_COLOR = (48, 150, 220)
PLAYER_EDGE_COLOR = (193, 232, 255)
TEXT_COLOR = (235, 241, 248)
BULLET_COLOR = (255, 211, 86)
BULLET_MARK_RIM_COLOR = (54, 59, 67)
BULLET_MARK_HOLE_COLOR = (19, 21, 25)
TARGET_COLOR = (208, 73, 82)
TARGET_EDGE_COLOR = (255, 190, 196)
HEALTH_COLOR = (82, 210, 118)


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


def make_practice_target():
    """Create the target and the values needed to damage and respawn it."""
    return {
        "position": pygame.Vector2(1100, 650),
        "health": TARGET_MAX_HEALTH,
        "alive": True,
        "respawn_timer": 0.0,
        "defeated_count": 0,
    }


def make_weapon_state(weapon):
    """Create ammunition and timing values that belong to one carried weapon."""
    return {
        "magazine_ammo": weapon["magazine_size"],
        "reserve_ammo": weapon["starting_reserve_ammo"],
        "shot_cooldown": 0.0,
        "reloading": False,
        "reload_timer": 0.0,
        "sustained_shots": 0,
    }


def get_movement_input():
    """Read WASD movement and whether either Shift key is being held."""
    keys = pygame.key.get_pressed()
    direction = pygame.Vector2(
        int(keys[pygame.K_d]) - int(keys[pygame.K_a]),
        int(keys[pygame.K_s]) - int(keys[pygame.K_w]),
    )
    sprint_key_held = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

    # Normalizing prevents diagonal movement from being faster than straight movement.
    if direction.length_squared() > 0:
        direction = direction.normalize()

    return direction, sprint_key_held


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


def get_weapon_spread(weapon, movement_state):
    """Return the active weapon's spread for the current movement state."""
    if movement_state == "Running":
        return weapon["running_spread"]
    if movement_state == "Walking":
        return weapon["walking_spread"]
    return weapon["standing_spread"]


def create_bullet(player_position, aim_angle, spread_percent, weapon):
    """Create one bullet with random deviation inside the current spread range."""
    maximum_deviation = MAX_SPREAD_DEGREES * spread_percent
    deviation_degrees = random.uniform(-maximum_deviation, maximum_deviation)
    bullet_angle = aim_angle + math.radians(deviation_degrees)

    direction = pygame.Vector2(math.cos(bullet_angle), math.sin(bullet_angle))
    muzzle_distance = PLAYER_SIZE / 2 + weapon["bullet_radius"] + 7

    return {
        "position": pygame.Vector2(player_position) + direction * muzzle_distance,
        "velocity": direction * weapon["bullet_speed"],
        "damage": weapon["damage"],
        "radius": weapon["bullet_radius"],
        "distance_traveled": 0.0,
        "damage_falloff_start": weapon.get("damage_falloff_start"),
        "damage_falloff_end": weapon.get("damage_falloff_end"),
        "minimum_damage_multiplier": weapon.get(
            "minimum_damage_multiplier",
            1.0,
        ),
    }


def calculate_bullet_damage(bullet):
    """Calculate integer damage using optional distance-based falloff."""
    falloff_start = bullet["damage_falloff_start"]
    falloff_end = bullet["damage_falloff_end"]

    if falloff_start is None or falloff_end is None:
        return bullet["damage"]

    distance = bullet["distance_traveled"]
    if distance <= falloff_start:
        multiplier = 1.0
    elif distance >= falloff_end:
        multiplier = bullet["minimum_damage_multiplier"]
    else:
        falloff_progress = (
            (distance - falloff_start) / (falloff_end - falloff_start)
        )
        multiplier = 1.0 + (
            bullet["minimum_damage_multiplier"] - 1.0
        ) * falloff_progress

    return max(1, round(bullet["damage"] * multiplier))


def get_bullet_hit_wall(bullet, walls):
    """Return the wall struck by the bullet, or None if there is no collision."""
    radius = bullet["radius"]
    bullet_rect = pygame.Rect(0, 0, radius * 2, radius * 2)
    bullet_rect.center = (
        round(bullet["position"].x),
        round(bullet["position"].y),
    )

    for wall in walls:
        if bullet_rect.colliderect(wall):
            return wall

    return None


def calculate_bullet_mark_lifetime(distance):
    """Return a shorter mark lifetime for an impact farther from its shooter."""
    if distance <= BULLET_MARK_NEAR_DISTANCE:
        return BULLET_MARK_LIFETIME
    if distance >= BULLET_MARK_FAR_DISTANCE:
        return BULLET_MARK_MIN_LIFETIME

    distance_progress = (
        (distance - BULLET_MARK_NEAR_DISTANCE)
        / (BULLET_MARK_FAR_DISTANCE - BULLET_MARK_NEAR_DISTANCE)
    )
    return BULLET_MARK_LIFETIME + (
        BULLET_MARK_MIN_LIFETIME - BULLET_MARK_LIFETIME
    ) * distance_progress


def create_bullet_mark(bullet, wall):
    """Create a fixed world-space mark clamped onto the struck wall's surface."""
    mark_radius = random.randint(BULLET_MARK_MIN_RADIUS, BULLET_MARK_MAX_RADIUS)

    # Clamping keeps the center of the mark on the visible top of the wall.
    mark_x = max(
        wall.left + mark_radius,
        min(bullet["position"].x, wall.right - mark_radius),
    )
    mark_y = max(
        wall.top + mark_radius,
        min(bullet["position"].y, wall.bottom - mark_radius),
    )

    mark_lifetime = calculate_bullet_mark_lifetime(
        bullet["distance_traveled"]
    )

    return {
        "position": pygame.Vector2(mark_x, mark_y),
        "wall": wall,
        "radius": mark_radius,
        "rotation": random.uniform(0, math.tau),
        "time_remaining": mark_lifetime,
        "fade_time": min(BULLET_MARK_FADE_TIME, mark_lifetime / 2),
    }


def update_bullet_marks(bullet_marks, delta_time):
    """Age impact marks and remove them after their lifetime expires."""
    for mark in bullet_marks:
        mark["time_remaining"] -= delta_time

    bullet_marks[:] = [
        mark for mark in bullet_marks if mark["time_remaining"] > 0
    ]


def clear_bullet_marks(bullet_marks):
    """Remove every impact mark; the future round manager calls this at round end."""
    bullet_marks.clear()


def update_bullets(bullets, delta_time, walls, target, bullet_marks):
    """Move bullets and remove them when they hit a wall, target, or map edge."""
    surviving_bullets = []

    for bullet in bullets:
        total_movement = bullet["velocity"] * delta_time
        step_length = max(1, bullet["radius"] * 2)
        step_count = max(1, math.ceil(total_movement.length() / step_length))
        movement_step = total_movement / step_count
        movement_step_length = movement_step.length()
        bullet_removed = False

        # Small movement steps prevent fast bullets from skipping through thin walls.
        for _ in range(step_count):
            bullet["position"] += movement_step
            bullet["distance_traveled"] += movement_step_length

            outside_world = not (
                0 <= bullet["position"].x <= WORLD_WIDTH
                and 0 <= bullet["position"].y <= WORLD_HEIGHT
            )
            if outside_world:
                bullet_removed = True
                break

            hit_wall = get_bullet_hit_wall(bullet, walls)
            if hit_wall is not None:
                bullet_marks.append(create_bullet_mark(bullet, hit_wall))
                if len(bullet_marks) > MAX_BULLET_MARKS:
                    del bullet_marks[0]

                bullet_removed = True
                break

            if target["alive"]:
                distance_to_target = bullet["position"].distance_to(target["position"])
                if distance_to_target <= bullet["radius"] + TARGET_RADIUS:
                    hit_damage = calculate_bullet_damage(bullet)
                    target["health"] = max(0, target["health"] - hit_damage)

                    if target["health"] == 0:
                        target["alive"] = False
                        target["respawn_timer"] = TARGET_RESPAWN_TIME
                        target["defeated_count"] += 1

                    bullet_removed = True
                    break

        if not bullet_removed:
            surviving_bullets.append(bullet)

    return surviving_bullets


def update_target(target, delta_time):
    """Restore the practice target after a short delay when it is defeated."""
    if target["alive"]:
        return

    target["respawn_timer"] -= delta_time
    if target["respawn_timer"] <= 0:
        target["health"] = TARGET_MAX_HEALTH
        target["alive"] = True
        target["respawn_timer"] = 0.0


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


def cross_product(vector_a, vector_b):
    """Return the two-dimensional cross product of two vectors."""
    return vector_a.x * vector_b.y - vector_a.y * vector_b.x


def get_wall_segments(walls):
    """Return the four blocking line segments around every rectangular wall."""
    segments = []

    for wall in walls:
        top_left = pygame.Vector2(wall.topleft)
        top_right = pygame.Vector2(wall.topright)
        bottom_right = pygame.Vector2(wall.bottomright)
        bottom_left = pygame.Vector2(wall.bottomleft)
        segments.extend(
            [
                (top_left, top_right),
                (top_right, bottom_right),
                (bottom_right, bottom_left),
                (bottom_left, top_left),
            ]
        )

    return segments


def get_ray_segment_distance(origin, direction, segment_start, segment_end):
    """Return how far a ray travels before hitting a segment, or None."""
    segment_direction = segment_end - segment_start
    denominator = cross_product(direction, segment_direction)

    if abs(denominator) < 0.000001:
        return None

    origin_to_segment = segment_start - origin
    ray_distance = (
        cross_product(origin_to_segment, segment_direction) / denominator
    )
    segment_progress = cross_product(origin_to_segment, direction) / denominator

    if ray_distance >= 0 and 0 <= segment_progress <= 1:
        return ray_distance
    return None


def calculate_vision_polygon(
    player_position,
    walls,
    camera,
    wall_segments=None,
):
    """Build the visible polygon created by rays stopping at nearby walls."""
    if wall_segments is None:
        wall_segments = get_wall_segments(walls)
    ray_angles = [
        math.tau * ray_index / VISION_BASE_RAY_COUNT
        for ray_index in range(VISION_BASE_RAY_COUNT)
    ]

    # Corner rays make the visible area hug both sides of each obstruction.
    for wall in walls:
        for corner in (wall.topleft, wall.topright, wall.bottomright, wall.bottomleft):
            corner_vector = pygame.Vector2(corner) - player_position
            corner_angle = math.atan2(corner_vector.y, corner_vector.x)
            ray_angles.extend(
                [
                    corner_angle - VISION_CORNER_ANGLE_OFFSET,
                    corner_angle,
                    corner_angle + VISION_CORNER_ANGLE_OFFSET,
                ]
            )

    vision_points = []
    for angle in ray_angles:
        direction = pygame.Vector2(math.cos(angle), math.sin(angle))
        nearest_distance = VISION_MAX_DISTANCE

        for segment_start, segment_end in wall_segments:
            hit_distance = get_ray_segment_distance(
                player_position,
                direction,
                segment_start,
                segment_end,
            )
            if hit_distance is not None:
                nearest_distance = min(nearest_distance, hit_distance)

        world_point = player_position + direction * nearest_distance
        screen_point = world_point - camera
        vision_points.append((angle % math.tau, screen_point))

    vision_points.sort(key=lambda item: item[0])
    return [point for _, point in vision_points]


def has_line_of_sight(
    start_position,
    end_position,
    walls,
    ignored_wall=None,
):
    """Return False when any wall crosses the line between two world points."""
    line_start = (round(start_position.x), round(start_position.y))
    line_end = (round(end_position.x), round(end_position.y))

    for wall in walls:
        if wall is ignored_wall:
            continue
        if wall.clipline(line_start, line_end):
            return False
    return True


def is_target_visible(player_position, target, walls):
    """Check the target's center and edges so it can peek around cover."""
    target_position = target["position"]
    sample_distance = TARGET_RADIUS * 0.80
    sample_points = [
        target_position,
        target_position + pygame.Vector2(sample_distance, 0),
        target_position + pygame.Vector2(-sample_distance, 0),
        target_position + pygame.Vector2(0, sample_distance),
        target_position + pygame.Vector2(0, -sample_distance),
    ]

    return any(
        has_line_of_sight(player_position, sample_point, walls)
        for sample_point in sample_points
    )


def update_camera_recoil(recoil_offset, recoil_velocity, shake_strength, delta_time):
    """Return the camera toward center with a damped spring after each shot."""
    recoil_velocity += -recoil_offset * CAMERA_RECOIL_SPRING * delta_time
    recoil_velocity *= math.exp(-CAMERA_RECOIL_DAMPING * delta_time)
    recoil_offset += recoil_velocity * delta_time
    shake_strength = max(
        0.0,
        shake_strength - CAMERA_SHAKE_DECAY_PER_SECOND * delta_time,
    )

    if recoil_offset.length_squared() < 0.0025 and recoil_velocity.length_squared() < 0.25:
        recoil_offset.update(0, 0)
        recoil_velocity.update(0, 0)

    return shake_strength


def add_shot_recoil(
    weapon,
    aim_angle,
    sustained_shot,
    recoil_velocity,
    shake_strength,
    sway_direction,
):
    """Apply tap shake or directional automatic-fire recoil for one shot."""
    if sustained_shot and weapon["fire_mode"] == "automatic":
        firing_direction = pygame.Vector2(
            math.cos(aim_angle),
            math.sin(aim_angle),
        )
        sideways_direction = pygame.Vector2(
            -firing_direction.y,
            firing_direction.x,
        )

        recoil_velocity -= firing_direction * weapon["sustained_camera_kick"]
        recoil_velocity += (
            sideways_direction
            * weapon["sustained_camera_sway"]
            * sway_direction
        )
        sway_direction *= -1
    else:
        shake_strength = max(shake_strength, weapon["tap_camera_shake"])

    return shake_strength, sway_direction


def apply_camera_effects(
    base_camera,
    recoil_offset,
    shake_strength,
    screen_size,
):
    """Add recoil and shake, then keep the final camera inside the map."""
    if shake_strength > 0:
        shake_offset = pygame.Vector2(
            random.uniform(-shake_strength, shake_strength),
            random.uniform(-shake_strength, shake_strength),
        )
    else:
        shake_offset = pygame.Vector2()

    camera = base_camera + recoil_offset + shake_offset
    maximum_x = max(0, WORLD_WIDTH - screen_size[0])
    maximum_y = max(0, WORLD_HEIGHT - screen_size[1])
    camera.x = max(0, min(camera.x, maximum_x))
    camera.y = max(0, min(camera.y, maximum_y))
    return camera


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


def draw_wall(
    screen,
    wall,
    camera,
    fill_color=WALL_COLOR,
    edge_color=WALL_EDGE_COLOR,
):
    """Draw one complete wall using the supplied visibility colors."""
    screen_rect = wall.move(-round(camera.x), -round(camera.y))
    pygame.draw.rect(screen, fill_color, screen_rect, border_radius=5)
    pygame.draw.rect(
        screen,
        edge_color,
        screen_rect,
        width=3,
        border_radius=5,
    )


def draw_hidden_walls(screen, walls, camera):
    """Keep every complete wall section visible using dark-gray colors."""
    for wall in walls:
        draw_wall(
            screen,
            wall,
            camera,
            HIDDEN_WALL_COLOR,
            HIDDEN_WALL_EDGE_COLOR,
        )


def draw_normal_walls(layer, walls, camera):
    """Draw normal wall colors before clipping them to visible portions."""
    for wall in walls:
        draw_wall(layer, wall, camera)


def draw_bullet_marks(
    screen,
    bullet_marks,
    camera,
    player_position=None,
    walls=None,
    visible_only=False,
):
    """Draw world-space impact holes and fade them near the end of their life."""
    # This function now draws directly onto a reusable transparent layer.
    mark_layer = screen
    screen_rect = screen.get_rect().inflate(40, 40)

    for mark in bullet_marks:
        if visible_only:
            mark_wall = mark.get("wall")
            if not has_line_of_sight(
                player_position,
                mark["position"],
                walls,
                ignored_wall=mark_wall,
            ):
                continue

        center = mark["position"] - camera
        center_tuple = (round(center.x), round(center.y))
        radius = mark["radius"]

        if not screen_rect.collidepoint(center_tuple):
            continue

        if mark["time_remaining"] < mark["fade_time"]:
            fade_fraction = mark["time_remaining"] / mark["fade_time"]
        else:
            fade_fraction = 1.0

        alpha = max(0, min(255, round(255 * fade_fraction)))
        rim_color = (*BULLET_MARK_RIM_COLOR, alpha)
        hole_color = (*BULLET_MARK_HOLE_COLOR, alpha)
        highlight_color = (91, 97, 107, alpha)

        # Three short cracks create a readable impact without requiring artwork.
        for crack_index in range(3):
            crack_angle = mark["rotation"] + crack_index * (math.tau / 3)
            crack_start = center + pygame.Vector2(
                math.cos(crack_angle),
                math.sin(crack_angle),
            ) * (radius - 1)
            crack_end = center + pygame.Vector2(
                math.cos(crack_angle),
                math.sin(crack_angle),
            ) * (radius + 5)
            pygame.draw.line(
                mark_layer,
                rim_color,
                (round(crack_start.x), round(crack_start.y)),
                (round(crack_end.x), round(crack_end.y)),
                width=2,
            )

        pygame.draw.circle(
            mark_layer,
            rim_color,
            center_tuple,
            radius + 2,
        )
        pygame.draw.circle(
            mark_layer,
            hole_color,
            center_tuple,
            radius,
        )
        pygame.draw.circle(
            mark_layer,
            highlight_color,
            center_tuple,
            radius,
            width=1,
        )

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


def draw_bullets(screen, bullets, camera):
    """Draw every bullet; the shared visibility mask clips hidden portions."""
    for bullet in bullets:
        screen_position = bullet["position"] - camera
        pygame.draw.circle(
            screen,
            BULLET_COLOR,
            (round(screen_position.x), round(screen_position.y)),
            bullet["radius"],
        )


def make_vision_render_buffers(screen_size):
    """Allocate vision surfaces once instead of rebuilding them every frame."""
    mask_size = (
        max(1, round(screen_size[0] * VISION_MASK_SCALE)),
        max(1, round(screen_size[1] * VISION_MASK_SCALE)),
    )

    return {
        "mask_size": mask_size,
        "small_actor_mask": pygame.Surface(mask_size, pygame.SRCALPHA),
        "small_wall_mask": pygame.Surface(mask_size, pygame.SRCALPHA),
        "actor_mask": pygame.Surface(screen_size, pygame.SRCALPHA),
        "wall_mask": pygame.Surface(screen_size, pygame.SRCALPHA),
        "shadow_layer": pygame.Surface(screen_size, pygame.SRCALPHA),
        "visible_world_layer": pygame.Surface(screen_size, pygame.SRCALPHA),
        "actor_layer": pygame.Surface(screen_size, pygame.SRCALPHA),
    }


def is_wall_fully_visible(player_position, target_wall, walls):
    """Return True only when no different wall blocks the target wall."""
    sample_fractions = (0.08, 0.50, 0.92)
    sample_points = [
        pygame.Vector2(
            target_wall.left + target_wall.width * x_fraction,
            target_wall.top + target_wall.height * y_fraction,
        )
        for x_fraction in sample_fractions
        for y_fraction in sample_fractions
    ]

    return all(
        has_line_of_sight(
            player_position,
            sample_point,
            walls,
            ignored_wall=target_wall,
        )
        for sample_point in sample_points
    )


def update_wall_visibility_mask(
    player_position,
    walls,
    camera,
    scale_x,
    scale_y,
    buffers,
):
    """Fully color clear walls and partially color walls behind cover."""
    small_actor_mask = buffers["small_actor_mask"]
    small_wall_mask = buffers["small_wall_mask"]

    # Begin with the exact sight shape, then add a small amount of depth so an
    # exposed corner of a farther wall is readable rather than a one-pixel line.
    small_wall_mask.fill((255, 255, 255, 0))
    small_wall_mask.blit(small_actor_mask, (0, 0))
    expansion_x = max(1, round(VISIBLE_WALL_COLOR_DEPTH * scale_x))
    expansion_y = max(1, round(VISIBLE_WALL_COLOR_DEPTH * scale_y))
    for direction_index in range(8):
        angle = math.tau * direction_index / 8
        small_wall_mask.blit(
            small_actor_mask,
            (
                round(math.cos(angle) * expansion_x),
                round(math.sin(angle) * expansion_y),
            ),
        )

    # A wall with no other cover in front of it is the near purple wall in the
    # reference image: color that entire wall section. A wall behind cover does
    # not enter this branch, so only its exposed tip keeps normal color.
    for target_wall in walls:
        if not is_wall_fully_visible(player_position, target_wall, walls):
            continue

        pygame.draw.rect(
            small_wall_mask,
            (255, 255, 255, 255),
            pygame.Rect(
                round((target_wall.left - camera.x) * scale_x),
                round((target_wall.top - camera.y) * scale_y),
                max(1, round(target_wall.width * scale_x)),
                max(1, round(target_wall.height * scale_y)),
            ),
        )


def update_visibility_masks(
    visible_polygon,
    player_position,
    walls,
    camera,
    screen_size,
    buffers,
):
    """Update partial-visibility masks for actors, bullets, and wall color."""
    mask_width, mask_height = buffers["mask_size"]
    scale_x = mask_width / screen_size[0]
    scale_y = mask_height / screen_size[1]
    small_actor_mask = buffers["small_actor_mask"]
    small_wall_mask = buffers["small_wall_mask"]

    small_actor_mask.fill((255, 255, 255, 0))
    if len(visible_polygon) >= 3:
        small_polygon = [
            (round(point.x * scale_x), round(point.y * scale_y))
            for point in visible_polygon
        ]
        pygame.draw.polygon(
            small_actor_mask,
            (255, 255, 255, 255),
            small_polygon,
        )

    update_wall_visibility_mask(
        player_position,
        walls,
        camera,
        scale_x,
        scale_y,
        buffers,
    )

    # Fast nearest-neighbor enlargement keeps this laboratory responsive.
    pygame.transform.scale(
        small_actor_mask,
        screen_size,
        buffers["actor_mask"],
    )
    pygame.transform.scale(
        small_wall_mask,
        screen_size,
        buffers["wall_mask"],
    )


def clip_layer_to_visibility(layer, visibility_mask):
    """Erase every pixel of a transparent layer outside the supplied mask."""
    layer.blit(
        visibility_mask,
        (0, 0),
        special_flags=pygame.BLEND_RGBA_MULT,
    )


def draw_vision_shadow(screen, visible_polygon, shadow_layer):
    """Darken concealed terrain while leaving its shapes and textures visible."""
    shadow_layer.fill(VISION_SHADOW_COLOR)

    if len(visible_polygon) >= 3:
        pygame.draw.polygon(
            shadow_layer,
            (0, 0, 0, 0),
            visible_polygon,
        )

    screen.blit(shadow_layer, (0, 0))


def draw_target(screen, font, target, camera):
    """Draw the practice target, its health bar, or its respawn countdown."""
    center = target["position"] - camera
    center_tuple = (round(center.x), round(center.y))

    if target["alive"]:
        pygame.draw.circle(screen, (35, 20, 24), center_tuple, TARGET_RADIUS + 6)
        pygame.draw.circle(screen, TARGET_COLOR, center_tuple, TARGET_RADIUS)
        pygame.draw.circle(screen, TARGET_EDGE_COLOR, center_tuple, TARGET_RADIUS, width=4)
        pygame.draw.circle(screen, TARGET_EDGE_COLOR, center_tuple, 10, width=3)

        bar_width = 90
        bar_height = 10
        bar_x = round(center.x - bar_width / 2)
        bar_y = round(center.y - TARGET_RADIUS - 28)
        health_fraction = target["health"] / TARGET_MAX_HEALTH
        pygame.draw.rect(screen, (26, 29, 36), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(
            screen,
            HEALTH_COLOR,
            (bar_x, bar_y, round(bar_width * health_fraction), bar_height),
        )
        pygame.draw.rect(
            screen,
            TARGET_EDGE_COLOR,
            (bar_x, bar_y, bar_width, bar_height),
            width=2,
        )
    else:
        pygame.draw.circle(
            screen,
            (79, 61, 66),
            center_tuple,
            TARGET_RADIUS,
            width=3,
        )
        countdown = font.render(
            f"{target['respawn_timer']:.1f}",
            True,
            TARGET_EDGE_COLOR,
        )
        countdown_rect = countdown.get_rect(center=center_tuple)
        screen.blit(countdown, countdown_rect)


def draw_crosshair(screen, mouse_position, spread_percent):
    """Expand the aiming reticle to indicate the current movement spread."""
    x, y = mouse_position
    color = (118, 211, 255)
    spread_number = spread_percent * 100
    gap = 5 + round(spread_number * 1.4)
    line_end = gap + 10

    pygame.draw.circle(screen, color, mouse_position, gap + 3, width=2)
    pygame.draw.line(screen, color, (x - line_end, y), (x - gap, y), width=2)
    pygame.draw.line(screen, color, (x + gap, y), (x + line_end, y), width=2)
    pygame.draw.line(screen, color, (x, y - line_end), (x, y - gap), width=2)
    pygame.draw.line(screen, color, (x, y + gap), (x, y + line_end), width=2)


def draw_stamina_panel(screen, font, stamina, sprinting, sprint_exhausted):
    """Draw the player's current stamina and sprint condition."""
    panel_width = 355
    panel_height = 78
    panel_x = 18
    panel_y = screen.get_height() - panel_height - 18

    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel.fill((10, 13, 18, 220))
    screen.blit(panel, (panel_x, panel_y))

    if sprint_exhausted:
        label = "STAMINA - EXHAUSTED (RELEASE SHIFT)"
        bar_color = (215, 78, 78)
    elif sprinting:
        label = "STAMINA - RUNNING"
        bar_color = (255, 174, 66)
    else:
        label = "STAMINA"
        bar_color = (76, 183, 232)

    label_text = font.render(label, True, TEXT_COLOR)
    screen.blit(label_text, (panel_x + 16, panel_y + 10))

    bar_x = panel_x + 16
    bar_y = panel_y + 40
    bar_width = panel_width - 32
    bar_height = 20
    stamina_fraction = stamina / MAX_STAMINA

    pygame.draw.rect(screen, (29, 34, 43), (bar_x, bar_y, bar_width, bar_height))
    pygame.draw.rect(
        screen,
        bar_color,
        (bar_x, bar_y, round(bar_width * stamina_fraction), bar_height),
    )
    pygame.draw.rect(
        screen,
        TEXT_COLOR,
        (bar_x, bar_y, bar_width, bar_height),
        width=2,
    )


def draw_debug_panel(
    screen,
    font,
    player_position,
    aim_angle,
    actual_speed,
    movement_state,
    spread_percent,
    stamina,
    active_weapon,
    current_fps,
):
    """Show the values that matter while testing movement."""
    lines = [
        "VISION LABORATORY 0.3",
        "WASD: Move  SHIFT: Run  LMB: Fire  R: Reload  1/2/3: Weapons  ESC: Quit",
        f"Position: ({player_position.x:.1f}, {player_position.y:.1f})",
        f"Facing: {math.degrees(aim_angle):.1f} degrees",
        f"Movement: {movement_state}",
        f"Current speed: {actual_speed:.0f} pixels/second",
        f"{active_weapon['name']} spread: {spread_percent * 100:.0f}%",
        f"Stamina: {stamina:.0f} / {MAX_STAMINA}",
        f"FPS: {current_fps:.0f}",
    ]

    panel = pygame.Surface((880, 253), pygame.SRCALPHA)
    panel.fill((10, 13, 18, 205))
    screen.blit(panel, (18, 18))

    for index, line in enumerate(lines):
        rendered_text = font.render(line, True, TEXT_COLOR)
        screen.blit(rendered_text, (34, 32 + index * 25))


def draw_weapon_panel(
    screen,
    regular_font,
    large_font,
    active_weapon,
    weapon_state,
    target,
    target_visible,
):
    """Display ammunition, reload status, target health, and target defeats."""
    panel_width = 355
    panel_height = 200
    panel_x = screen.get_width() - panel_width - 18
    panel_y = screen.get_height() - panel_height - 18

    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel.fill((10, 13, 18, 220))
    screen.blit(panel, (panel_x, panel_y))

    fire_mode_label = (
        "AUTO" if active_weapon["fire_mode"] == "automatic" else "SEMI"
    )
    weapon_name = regular_font.render(
        f"SLOT {active_weapon['slot']}: {active_weapon['name'].upper()} [{fire_mode_label}]",
        True,
        TEXT_COLOR,
    )
    screen.blit(weapon_name, (panel_x + 18, panel_y + 14))

    ammunition = large_font.render(
        f"{weapon_state['magazine_ammo']} / {weapon_state['reserve_ammo']}",
        True,
        BULLET_COLOR,
    )
    screen.blit(ammunition, (panel_x + 18, panel_y + 38))

    if weapon_state["reloading"]:
        weapon_status = f"RELOADING: {weapon_state['reload_timer']:.1f}s"
    elif weapon_state["magazine_ammo"] == 0:
        weapon_status = "OUT OF AMMO"
    else:
        weapon_status = "READY"

    status_text = regular_font.render(weapon_status, True, TEXT_COLOR)
    screen.blit(status_text, (panel_x + 18, panel_y + 87))

    slots_text = regular_font.render(
        "1: Pistol    2: Rifle    3: Shotgun",
        True,
        (166, 180, 198),
    )
    screen.blit(slots_text, (panel_x + 18, panel_y + 113))

    if not target_visible:
        target_status = "Target: CONCEALED"
    elif target["alive"]:
        target_status = f"Target health: {target['health']} / {TARGET_MAX_HEALTH}"
    else:
        target_status = "Target defeated"

    target_text = regular_font.render(target_status, True, TEXT_COLOR)
    defeat_text = regular_font.render(
        f"Targets defeated: {target['defeated_count']}",
        True,
        TEXT_COLOR,
    )
    screen.blit(target_text, (panel_x + 18, panel_y + 142))
    screen.blit(defeat_text, (panel_x + 18, panel_y + 168))


def main():
    pygame.init()

    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Riftbound - Vision Laboratory")
    pygame.mouse.set_visible(False)
    vision_buffers = make_vision_render_buffers(screen.get_size())

    clock = pygame.time.Clock()
    debug_font = pygame.font.Font(None, 26)
    ammunition_font = pygame.font.Font(None, 48)
    walls = make_walls()
    wall_segments = get_wall_segments(walls)
    target = make_practice_target()

    player_position = pygame.Vector2(260, 240)
    aim_angle = 0.0
    bullets = []
    bullet_marks = []

    weapon_states = [make_weapon_state(weapon) for weapon in WEAPONS]
    active_weapon_index = 0
    camera_recoil_offset = pygame.Vector2()
    camera_recoil_velocity = pygame.Vector2()
    camera_shake_strength = 0.0
    recoil_sway_direction = 1
    stamina = MAX_STAMINA
    sprint_exhausted = False
    game_running = True

    while game_running:
        # Delta time keeps movement, bullets, and timers consistent at any frame rate.
        delta_time = min(clock.tick(FPS) / 1000.0, 0.05)
        reload_requested = False
        weapon_switch_requested = None
        trigger_just_pressed = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_running = False
                elif event.key == pygame.K_r:
                    reload_requested = True
                elif event.key == pygame.K_1:
                    weapon_switch_requested = 0
                elif event.key == pygame.K_2:
                    weapon_switch_requested = 1
                elif event.key == pygame.K_3:
                    weapon_switch_requested = 2
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                trigger_just_pressed = True

        if (
            weapon_switch_requested is not None
            and weapon_switch_requested != active_weapon_index
        ):
            # Switching weapons cancels, rather than completes, the current reload.
            old_weapon_state = weapon_states[active_weapon_index]
            old_weapon_state["reloading"] = False
            old_weapon_state["reload_timer"] = 0.0
            old_weapon_state["sustained_shots"] = 0
            active_weapon_index = weapon_switch_requested
            weapon_states[active_weapon_index]["sustained_shots"] = 0

        active_weapon = WEAPONS[active_weapon_index]
        active_weapon_state = weapon_states[active_weapon_index]
        trigger_held = pygame.mouse.get_pressed()[0]
        if trigger_just_pressed or not trigger_held:
            active_weapon_state["sustained_shots"] = 0

        movement_direction, sprint_key_held = get_movement_input()
        moving = movement_direction.length_squared() > 0
        sprinting = (
            moving
            and sprint_key_held
            and not sprint_exhausted
            and stamina > 0
        )

        if sprinting:
            stamina = max(
                0.0,
                stamina - SPRINT_STAMINA_DRAIN_PER_SECOND * delta_time,
            )
            if stamina == 0:
                sprint_exhausted = True
        else:
            stamina = min(
                MAX_STAMINA,
                stamina + SPRINT_STAMINA_REGEN_PER_SECOND * delta_time,
            )

            # Releasing Shift after recovering prevents rapid run/walk stuttering.
            if (
                sprint_exhausted
                and not sprint_key_held
                and stamina >= SPRINT_RECOVERY_THRESHOLD
            ):
                sprint_exhausted = False

        selected_speed = (
            PLAYER_SPEED * SPRINT_MULTIPLIER if sprinting else PLAYER_SPEED
        )
        movement = movement_direction * selected_speed * delta_time
        move_player(player_position, movement, walls)

        if movement_direction.length_squared() == 0:
            movement_state = "Idle"
            actual_speed = 0
        elif sprinting:
            movement_state = "Running"
            actual_speed = selected_speed
        else:
            movement_state = "Walking"
            actual_speed = selected_speed

        base_spread = get_weapon_spread(active_weapon, movement_state)
        sustained_spread = min(
            active_weapon_state["sustained_shots"]
            * active_weapon["sustained_spread_per_shot"],
            active_weapon["maximum_sustained_spread"],
        )
        current_spread = base_spread + sustained_spread

        camera_shake_strength = update_camera_recoil(
            camera_recoil_offset,
            camera_recoil_velocity,
            camera_shake_strength,
            delta_time,
        )
        base_camera = calculate_camera(player_position, screen.get_size())
        camera = apply_camera_effects(
            base_camera,
            camera_recoil_offset,
            camera_shake_strength,
            screen.get_size(),
        )
        mouse_screen_position = pygame.Vector2(pygame.mouse.get_pos())
        mouse_world_position = mouse_screen_position + camera
        aim_vector = mouse_world_position - player_position
        if aim_vector.length_squared() > 0:
            aim_angle = math.atan2(aim_vector.y, aim_vector.x)

        for weapon_state in weapon_states:
            weapon_state["shot_cooldown"] = max(
                0.0,
                weapon_state["shot_cooldown"] - delta_time,
            )

        if reload_requested and not active_weapon_state["reloading"]:
            magazine_has_space = (
                active_weapon_state["magazine_ammo"]
                < active_weapon["magazine_size"]
            )
            if magazine_has_space and active_weapon_state["reserve_ammo"] > 0:
                active_weapon_state["reloading"] = True
                active_weapon_state["reload_timer"] = active_weapon["reload_time"]
                active_weapon_state["sustained_shots"] = 0

        if active_weapon_state["reloading"]:
            active_weapon_state["reload_timer"] -= delta_time
            if active_weapon_state["reload_timer"] <= 0:
                ammunition_needed = (
                    active_weapon["magazine_size"]
                    - active_weapon_state["magazine_ammo"]
                )
                ammunition_loaded = min(
                    ammunition_needed,
                    active_weapon_state["reserve_ammo"],
                )
                active_weapon_state["magazine_ammo"] += ammunition_loaded
                active_weapon_state["reserve_ammo"] -= ammunition_loaded
                active_weapon_state["reloading"] = False
                active_weapon_state["reload_timer"] = 0.0

        if active_weapon["fire_mode"] == "semi":
            firing = trigger_just_pressed
        else:
            firing = trigger_held or trigger_just_pressed

        can_fire = (
            firing
            and not active_weapon_state["reloading"]
            and active_weapon_state["magazine_ammo"] > 0
            and active_weapon_state["shot_cooldown"] <= 0
        )
        if can_fire:
            sustained_shot = (
                active_weapon["fire_mode"] == "automatic"
                and active_weapon_state["sustained_shots"] > 0
                and not trigger_just_pressed
            )
            for _ in range(active_weapon["projectiles_per_shot"]):
                bullets.append(
                    create_bullet(
                        player_position,
                        aim_angle,
                        current_spread,
                        active_weapon,
                    )
                )
            active_weapon_state["magazine_ammo"] -= 1
            active_weapon_state["shot_cooldown"] = active_weapon["seconds_per_shot"]
            camera_shake_strength, recoil_sway_direction = add_shot_recoil(
                active_weapon,
                aim_angle,
                sustained_shot,
                camera_recoil_velocity,
                camera_shake_strength,
                recoil_sway_direction,
            )
            if active_weapon["fire_mode"] == "automatic":
                active_weapon_state["sustained_shots"] += 1

        # Reaching zero starts the same reload used by the R key.
        if (
            not active_weapon_state["reloading"]
            and active_weapon_state["magazine_ammo"] == 0
            and active_weapon_state["reserve_ammo"] > 0
        ):
            active_weapon_state["reloading"] = True
            active_weapon_state["reload_timer"] = active_weapon["reload_time"]
            active_weapon_state["sustained_shots"] = 0

        bullets = update_bullets(
            bullets,
            delta_time,
            walls,
            target,
            bullet_marks,
        )
        update_bullet_marks(bullet_marks, delta_time)
        update_target(target, delta_time)
        target_visible = is_target_visible(player_position, target, walls)
        visible_polygon = calculate_vision_polygon(
            player_position,
            walls,
            camera,
            wall_segments,
        )
        update_visibility_masks(
            visible_polygon,
            player_position,
            walls,
            camera,
            screen.get_size(),
            vision_buffers,
        )

        screen.fill(BACKGROUND_COLOR)
        draw_grid(screen, camera)
        draw_vision_shadow(
            screen,
            visible_polygon,
            vision_buffers["shadow_layer"],
        )

        # First redraw every complete wall section dark gray. Nothing in the
        # vision mask is allowed to remove or cut away the wall's shape.
        draw_hidden_walls(screen, walls, camera)

        # Then restore normal color only to the portions inside the wall mask.
        visible_world_layer = vision_buffers["visible_world_layer"]
        visible_world_layer.fill((0, 0, 0, 0))
        draw_normal_walls(visible_world_layer, walls, camera)
        draw_bullet_marks(
            visible_world_layer,
            bullet_marks,
            camera,
        )
        clip_layer_to_visibility(
            visible_world_layer,
            vision_buffers["wall_mask"],
        )
        screen.blit(visible_world_layer, (0, 0))

        # Characters, their health display, and bullets use the exact mask.
        # If only a sliver is exposed, only that sliver is rendered.
        actor_layer = vision_buffers["actor_layer"]
        actor_layer.fill((0, 0, 0, 0))
        draw_target(actor_layer, debug_font, target, camera)
        draw_bullets(actor_layer, bullets, camera)
        clip_layer_to_visibility(
            actor_layer,
            vision_buffers["actor_mask"],
        )
        screen.blit(actor_layer, (0, 0))

        draw_player(screen, player_position, aim_angle, camera)
        draw_debug_panel(
            screen,
            debug_font,
            player_position,
            aim_angle,
            actual_speed,
            movement_state,
            current_spread,
            stamina,
            active_weapon,
            clock.get_fps(),
        )
        draw_weapon_panel(
            screen,
            debug_font,
            ammunition_font,
            active_weapon,
            active_weapon_state,
            target,
            target_visible,
        )
        draw_stamina_panel(
            screen,
            debug_font,
            stamina,
            sprinting,
            sprint_exhausted,
        )
        draw_crosshair(screen, pygame.mouse.get_pos(), current_spread)

        pygame.display.flip()

    pygame.mouse.set_visible(True)
    pygame.quit()


if __name__ == "__main__":
    main()