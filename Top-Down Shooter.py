import math
import random

import pygame


# -----------------------------------------------------------------------------
# MOVEMENT LABORATORY SETTINGS
# These are safe values to experiment with while learning the project.
# -----------------------------------------------------------------------------
FPS = 80
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
# Corner rays define rectangular-wall shadows. A small circular safety set is
# enough between corners and avoids dozens of redundant ray tests per viewer.
VISION_BASE_RAY_COUNT = 16
VISION_CORNER_ANGLE_OFFSET = 0.0001
VISION_MAX_DISTANCE = math.hypot(WORLD_WIDTH, WORLD_HEIGHT)
# Recalculate visibility every second rendered frame: 40 vision updates while
# targeting 80 FPS. Frame-based skipping also recovers when performance dips.
VISION_RENDER_FRAMES_PER_UPDATE = 2
# Wall-shadow geometry is calculated at half resolution, then smoothly scaled.
# Actors keep a fast full-size mask so only one mask is enlarged each frame.
VISION_MASK_SCALE = 0.5
# The alpha value keeps concealed terrain readable instead of covering it.
# Visible terrain keeps its normal color; concealed terrain is darkened.
VISION_SHADOW_COLOR = (10, 12, 18, 175)

# -----------------------------------------------------------------------------
# FIRST MATCH 0.5 SETTINGS
# The player joins two blue bots against three red bots.
# -----------------------------------------------------------------------------
ACTOR_MAX_HEALTH = 100
ACTOR_RADIUS = PLAYER_SIZE // 2
TEAM_SIZE = 3
ROUNDS_TO_WIN = 5
ROUND_END_DELAY = 3.0
REVIVE_DURATION = 2.0
REVIVE_RANGE = 90
REVIVE_HEALTH = 50

BOT_SPEED = 175
BOT_RETREAT_DISTANCE = 260
BOT_PREFERRED_DISTANCE = 480
BOT_FIRE_INTERVAL = 0.32
BOT_BULLET_DAMAGE = 12
BOT_SPREAD = 0.08
ACTOR_SEPARATION_DISTANCE = PLAYER_SIZE + 10

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
ALLY_COLOR = (70, 174, 226)
ALLY_EDGE_COLOR = (190, 235, 255)
ENEMY_COLOR = (208, 73, 82)
ENEMY_EDGE_COLOR = (255, 190, 196)
DOWNED_COLOR = (225, 158, 65)
ELIMINATED_COLOR = (79, 61, 66)

BLUE_SPAWNS = [(260, 240), (260, 690), (260, 1320)]
RED_SPAWNS = [(2140, 240), (2140, 800), (2140, 1360)]

# Each lane is a simple route around the laboratory walls. This is intentionally
# understandable waypoint AI; proper navigation can replace it later.
BOT_ROUTES = [
    [(300, 190), (1050, 180), (1950, 180), (1950, 380), (2100, 380), (2100, 700)],
    [
        (300, 650),
        (800, 700),
        (800, 950),
        (1000, 950),
        (1030, 780),
        (1120, 730),
        (1600, 760),
        (2100, 800),
    ],
    [(300, 1320), (1100, 1320), (1320, 1450), (2050, 1400)],
]


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


def make_actor(name, team, spawn_position, is_player=False, route=None):
    """Create one player or bot with round, combat, and revival state."""
    return {
        "name": name,
        "team": team,
        "is_player": is_player,
        "spawn_position": pygame.Vector2(spawn_position),
        "position": pygame.Vector2(spawn_position),
        "health": ACTOR_MAX_HEALTH,
        "alive": True,
        "downed": False,
        "eliminated": False,
        "times_downed": 0,
        "revive_progress": 0.0,
        "revive_source": None,
        "aim_angle": 0.0,
        "shot_cooldown": random.uniform(0.0, BOT_FIRE_INTERVAL),
        "strafe_direction": random.choice((-1, 1)),
        "strafe_timer": random.uniform(0.7, 1.5),
        "route": [pygame.Vector2(point) for point in (route or [])],
        "route_index": 0,
    }


def make_match_actors():
    """Create the human player, two blue bots, and three red bots."""
    actors = [make_actor("YOU", "blue", BLUE_SPAWNS[0], is_player=True)]

    for index in range(1, TEAM_SIZE):
        actors.append(
            make_actor(
                f"ALLY {index}",
                "blue",
                BLUE_SPAWNS[index],
                route=BOT_ROUTES[index],
            )
        )

    for index in range(TEAM_SIZE):
        actors.append(
            make_actor(
                f"ENEMY {index + 1}",
                "red",
                RED_SPAWNS[index],
                route=list(reversed(BOT_ROUTES[index])),
            )
        )

    return actors


def reset_actor_for_round(actor):
    """Restore one actor to its original spawn and first-life state."""
    actor["position"].update(actor["spawn_position"])
    actor["health"] = ACTOR_MAX_HEALTH
    actor["alive"] = True
    actor["downed"] = False
    actor["eliminated"] = False
    actor["times_downed"] = 0
    actor["revive_progress"] = 0.0
    actor["revive_source"] = None
    actor["aim_angle"] = 0.0
    actor["shot_cooldown"] = random.uniform(0.0, BOT_FIRE_INTERVAL)
    actor["route_index"] = 0


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


def create_bullet(
    shooter,
    aim_angle,
    spread_percent,
    weapon,
    damage_override=None,
):
    """Create one bullet with random deviation inside the current spread range."""
    maximum_deviation = MAX_SPREAD_DEGREES * spread_percent
    deviation_degrees = random.uniform(-maximum_deviation, maximum_deviation)
    bullet_angle = aim_angle + math.radians(deviation_degrees)

    direction = pygame.Vector2(math.cos(bullet_angle), math.sin(bullet_angle))
    muzzle_distance = PLAYER_SIZE / 2 + weapon["bullet_radius"] + 7

    return {
        "position": pygame.Vector2(shooter["position"]) + direction * muzzle_distance,
        "velocity": direction * weapon["bullet_speed"],
        "damage": weapon["damage"] if damage_override is None else damage_override,
        "radius": weapon["bullet_radius"],
        "team": shooter["team"],
        "shooter": shooter,
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


def down_or_eliminate_actor(actor):
    """Down an actor once; a second lethal defeat eliminates them for the round."""
    actor["times_downed"] += 1
    actor["health"] = 0
    actor["alive"] = False
    actor["revive_progress"] = 0.0
    actor["revive_source"] = None

    if actor["times_downed"] >= 2:
        actor["downed"] = False
        actor["eliminated"] = True
    else:
        actor["downed"] = True
        actor["eliminated"] = False


def revive_actor(actor):
    """Return a first-time downed actor with partial health."""
    actor["health"] = REVIVE_HEALTH
    actor["alive"] = True
    actor["downed"] = False
    actor["revive_progress"] = 0.0
    actor["revive_source"] = None


def update_bullets(bullets, delta_time, walls, actors, bullet_marks):
    """Move bullets and damage the first enemy actor or wall they strike."""
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

            for actor in actors:
                if (
                    actor["team"] == bullet["team"]
                    or not actor["alive"]
                    or actor is bullet["shooter"]
                ):
                    continue

                distance_to_target = bullet["position"].distance_to(
                    actor["position"]
                )
                if distance_to_target <= bullet["radius"] + ACTOR_RADIUS:
                    hit_damage = calculate_bullet_damage(bullet)
                    actor["health"] = max(0, actor["health"] - hit_damage)

                    if actor["health"] == 0:
                        down_or_eliminate_actor(actor)

                    bullet_removed = True
                    break

            if bullet_removed:
                break

        if not bullet_removed:
            surviving_bullets.append(bullet)

    return surviving_bullets


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


def get_wall_segments(walls):
    """Precalculate compact numeric wall segments for fast vision rays."""
    segments = []

    for wall in walls:
        left = float(wall.left)
        right = float(wall.right)
        top = float(wall.top)
        bottom = float(wall.bottom)
        segments.extend(
            [
                (left, top, right - left, 0.0),
                (right, top, 0.0, bottom - top),
                (right, bottom, left - right, 0.0),
                (left, bottom, 0.0, top - bottom),
            ]
        )

    return segments


def get_wall_corners(walls):
    """Precalculate wall-corner coordinates used to aim precision rays."""
    corners = []
    for wall in walls:
        corners.extend(
            [
                (float(wall.left), float(wall.top)),
                (float(wall.right), float(wall.top)),
                (float(wall.right), float(wall.bottom)),
                (float(wall.left), float(wall.bottom)),
            ]
        )
    return corners


def calculate_vision_polygon(
    player_position,
    walls,
    camera,
    wall_segments=None,
    wall_corners=None,
):
    """Build a vision polygon using compact float math instead of Vector2 loops."""
    if wall_segments is None:
        wall_segments = get_wall_segments(walls)
    if wall_corners is None:
        wall_corners = get_wall_corners(walls)

    origin_x = player_position.x
    origin_y = player_position.y
    ray_angles = [
        math.tau * ray_index / VISION_BASE_RAY_COUNT
        for ray_index in range(VISION_BASE_RAY_COUNT)
    ]

    # Corner rays make the visible area hug both sides of each obstruction.
    for corner_x, corner_y in wall_corners:
        corner_angle = math.atan2(corner_y - origin_y, corner_x - origin_x)
        ray_angles.extend(
            [
                corner_angle - VISION_CORNER_ANGLE_OFFSET,
                corner_angle,
                corner_angle + VISION_CORNER_ANGLE_OFFSET,
            ]
        )

    vision_points = []
    for angle in ray_angles:
        direction_x = math.cos(angle)
        direction_y = math.sin(angle)
        nearest_distance = VISION_MAX_DISTANCE

        for segment_x, segment_y, segment_dx, segment_dy in wall_segments:
            denominator = direction_x * segment_dy - direction_y * segment_dx
            if abs(denominator) < 0.000001:
                continue

            origin_to_segment_x = segment_x - origin_x
            origin_to_segment_y = segment_y - origin_y
            ray_distance = (
                origin_to_segment_x * segment_dy
                - origin_to_segment_y * segment_dx
            ) / denominator
            segment_progress = (
                origin_to_segment_x * direction_y
                - origin_to_segment_y * direction_x
            ) / denominator

            if (
                ray_distance >= 0
                and 0 <= segment_progress <= 1
                and ray_distance < nearest_distance
            ):
                nearest_distance = ray_distance

        screen_point = (
            origin_x + direction_x * nearest_distance - camera.x,
            origin_y + direction_y * nearest_distance - camera.y,
        )
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


def is_actor_visible(viewer_position, actor, walls):
    """Check an actor's center and edges so partial peeks count as visible."""
    target_position = actor["position"]
    sample_distance = ACTOR_RADIUS * 0.80
    sample_points = [
        target_position,
        target_position + pygame.Vector2(sample_distance, 0),
        target_position + pygame.Vector2(-sample_distance, 0),
        target_position + pygame.Vector2(0, sample_distance),
        target_position + pygame.Vector2(0, -sample_distance),
    ]

    return any(
        has_line_of_sight(viewer_position, sample_point, walls)
        for sample_point in sample_points
    )


def actor_can_fight(actor):
    """Return True only for actors who can move, aim, and shoot."""
    return actor["alive"] and not actor["downed"] and not actor["eliminated"]


def find_nearest_actor(origin_actor, actors, team=None, downed_only=False):
    """Return the nearest actor matching the requested team and state."""
    candidates = []
    for actor in actors:
        if actor is origin_actor:
            continue
        if team is not None and actor["team"] != team:
            continue
        if downed_only:
            if not actor["downed"] or actor["eliminated"]:
                continue
        elif not actor_can_fight(actor):
            continue
        candidates.append(actor)

    if not candidates:
        return None
    return min(
        candidates,
        key=lambda actor: origin_actor["position"].distance_squared_to(
            actor["position"]
        ),
    )


def move_actor_toward(actor, destination, speed, delta_time, walls):
    """Move an actor toward a point using the existing sliding collision."""
    direction = pygame.Vector2(destination) - actor["position"]
    if direction.length_squared() == 0:
        return
    direction = direction.normalize()
    move_player(actor["position"], direction * speed * delta_time, walls)


def try_revive(reviver, target, delta_time, walls):
    """Advance a hold-to-revive action while one teammate remains nearby."""
    if (
        target is None
        or not target["downed"]
        or target["eliminated"]
        or reviver["position"].distance_to(target["position"]) > REVIVE_RANGE
        or not has_line_of_sight(reviver["position"], target["position"], walls)
    ):
        return False

    # Only one teammate contributes progress during a frame.
    if target["revive_source"] not in (None, reviver["name"]):
        return False

    target["revive_source"] = reviver["name"]
    target["revive_progress"] += delta_time
    if target["revive_progress"] >= REVIVE_DURATION:
        revive_actor(target)
    return True


def get_bot_patrol_destination(bot):
    """Return the bot's current route point and advance after reaching it."""
    if not bot["route"]:
        return bot["position"]

    destination = bot["route"][bot["route_index"]]
    if bot["position"].distance_to(destination) < 70:
        bot["route_index"] = (bot["route_index"] + 1) % len(bot["route"])
        destination = bot["route"][bot["route_index"]]
    return destination


def update_bot(bot, actors, walls, bullets, delta_time):
    """Run understandable bot priorities: revive, seek, move, then fire."""
    if not actor_can_fight(bot):
        return

    bot["shot_cooldown"] = max(0.0, bot["shot_cooldown"] - delta_time)
    bot["strafe_timer"] -= delta_time
    if bot["strafe_timer"] <= 0:
        bot["strafe_direction"] *= -1
        bot["strafe_timer"] = random.uniform(0.7, 1.5)

    downed_ally = find_nearest_actor(
        bot,
        actors,
        team=bot["team"],
        downed_only=True,
    )
    if downed_ally is not None:
        possible_revivers = [
            actor
            for actor in actors
            if actor["team"] == bot["team"]
            and not actor["is_player"]
            and actor_can_fight(actor)
            and has_line_of_sight(
                actor["position"],
                downed_ally["position"],
                walls,
            )
        ]
        if possible_revivers:
            designated_reviver = min(
                possible_revivers,
                key=lambda actor: actor["position"].distance_squared_to(
                    downed_ally["position"]
                ),
            )
            if designated_reviver is not bot:
                downed_ally = None
        else:
            downed_ally = None

    if downed_ally is not None:
        ally_distance = bot["position"].distance_to(downed_ally["position"])
        if ally_distance > REVIVE_RANGE:
            move_actor_toward(
                bot,
                downed_ally["position"],
                BOT_SPEED,
                delta_time,
                walls,
            )
        else:
            try_revive(bot, downed_ally, delta_time, walls)
        return

    enemy_team = "red" if bot["team"] == "blue" else "blue"
    visible_enemies = [
        actor
        for actor in actors
        if actor["team"] == enemy_team
        and actor_can_fight(actor)
        and is_actor_visible(bot["position"], actor, walls)
    ]

    if not visible_enemies:
        move_actor_toward(
            bot,
            get_bot_patrol_destination(bot),
            BOT_SPEED,
            delta_time,
            walls,
        )
        return

    target = min(
        visible_enemies,
        key=lambda actor: bot["position"].distance_squared_to(actor["position"]),
    )
    target_vector = target["position"] - bot["position"]
    target_distance = target_vector.length()
    if target_distance == 0:
        return

    forward = target_vector.normalize()
    bot["aim_angle"] = math.atan2(forward.y, forward.x)

    if target_distance > BOT_PREFERRED_DISTANCE:
        move_player(bot["position"], forward * BOT_SPEED * delta_time, walls)
    elif target_distance < BOT_RETREAT_DISTANCE:
        move_player(bot["position"], -forward * BOT_SPEED * delta_time, walls)
    else:
        sideways = pygame.Vector2(-forward.y, forward.x)
        move_player(
            bot["position"],
            sideways * BOT_SPEED * 0.55 * bot["strafe_direction"] * delta_time,
            walls,
        )

    if bot["shot_cooldown"] <= 0:
        bullets.append(
            create_bullet(
                bot,
                bot["aim_angle"],
                BOT_SPREAD,
                RIFLE,
                damage_override=BOT_BULLET_DAMAGE,
            )
        )
        bot["shot_cooldown"] = BOT_FIRE_INTERVAL


def reset_revival_sources(actors):
    """Require uninterrupted proximity or holding E for revival progress."""
    for actor in actors:
        if actor["downed"]:
            actor["revive_source"] = None


def finish_unattended_revives(actors):
    """Reset progress when nobody continued a revive during this frame."""
    for actor in actors:
        if actor["downed"] and actor["revive_source"] is None:
            actor["revive_progress"] = 0.0


def team_has_standing_actor(actors, team):
    """A team loses when nobody remains standing to fight or revive."""
    return any(actor_can_fight(actor) for actor in actors if actor["team"] == team)


def separate_standing_actors(actors, walls):
    """Prevent living players and bots from occupying the same position."""
    standing_actors = [actor for actor in actors if actor_can_fight(actor)]

    for first_index, first_actor in enumerate(standing_actors):
        for second_actor in standing_actors[first_index + 1:]:
            difference = second_actor["position"] - first_actor["position"]
            distance_squared = difference.length_squared()
            minimum_distance = ACTOR_SEPARATION_DISTANCE
            if distance_squared >= minimum_distance * minimum_distance:
                continue

            if distance_squared <= 0.0001:
                # Stable fallback direction for actors at precisely one point.
                direction = pygame.Vector2(1, 0)
                distance = 0.0
            else:
                distance = math.sqrt(distance_squared)
                direction = difference / distance

            overlap = minimum_distance - distance
            if first_actor["is_player"]:
                move_player(
                    second_actor["position"],
                    direction * overlap,
                    walls,
                )
            elif second_actor["is_player"]:
                move_player(
                    first_actor["position"],
                    -direction * overlap,
                    walls,
                )
            else:
                push = direction * (overlap / 2)
                move_player(first_actor["position"], -push, walls)
                move_player(second_actor["position"], push, walls)


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


def draw_bullet_marks(
    screen,
    bullet_marks,
    camera,
    player_position=None,
    walls=None,
    visible_only=False,
    only_wall=None,
):
    """Draw world-space impact holes and fade them near the end of their life."""
    # This function now draws directly onto a reusable transparent layer.
    mark_layer = screen
    screen_rect = screen.get_rect().inflate(40, 40)

    for mark in bullet_marks:
        if only_wall is not None and mark.get("wall") is not only_wall:
            continue
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

def draw_actor(screen, font, actor, camera):
    """Draw one team actor with health, facing, and downed state."""
    center = pygame.Vector2(actor["position"] - camera)
    center_tuple = (round(center.x), round(center.y))
    shadow_center = center + pygame.Vector2(7, 9)
    radius = ACTOR_RADIUS

    if actor["team"] == "blue":
        fill_color = PLAYER_COLOR if actor["is_player"] else ALLY_COLOR
        edge_color = PLAYER_EDGE_COLOR if actor["is_player"] else ALLY_EDGE_COLOR
    else:
        fill_color = ENEMY_COLOR
        edge_color = ENEMY_EDGE_COLOR

    if actor["eliminated"]:
        pygame.draw.circle(screen, ELIMINATED_COLOR, center_tuple, radius, width=4)
        pygame.draw.line(
            screen,
            ELIMINATED_COLOR,
            center + pygame.Vector2(-16, -16),
            center + pygame.Vector2(16, 16),
            width=5,
        )
        pygame.draw.line(
            screen,
            ELIMINATED_COLOR,
            center + pygame.Vector2(16, -16),
            center + pygame.Vector2(-16, 16),
            width=5,
        )
        return

    if actor["downed"]:
        pygame.draw.circle(screen, (15, 18, 24), shadow_center, radius)
        pygame.draw.circle(screen, (32, 35, 43), center_tuple, radius)
        pygame.draw.circle(screen, edge_color, center_tuple, radius, width=5)
        pygame.draw.circle(
            screen,
            DOWNED_COLOR,
            center_tuple,
            radius - 8,
            width=3,
        )
        revive_fraction = min(1.0, actor["revive_progress"] / REVIVE_DURATION)
        pygame.draw.arc(
            screen,
            HEALTH_COLOR,
            pygame.Rect(center.x - 36, center.y - 36, 72, 72),
            -math.pi / 2,
            -math.pi / 2 + math.tau * revive_fraction,
            width=5,
        )
        downed_text = font.render("DOWN", True, DOWNED_COLOR)
        screen.blit(downed_text, downed_text.get_rect(center=center_tuple))
        return

    pygame.draw.circle(screen, (15, 18, 24), shadow_center, radius)
    pygame.draw.circle(screen, fill_color, center_tuple, radius)
    pygame.draw.circle(screen, edge_color, center_tuple, radius, width=3)

    facing = pygame.Vector2(
        math.cos(actor["aim_angle"]),
        math.sin(actor["aim_angle"]),
    )
    side = pygame.Vector2(-facing.y, facing.x)
    arrow_tip = center + facing * 34
    arrow_left = center - facing * 5 + side * 10
    arrow_right = center - facing * 5 - side * 10
    pygame.draw.polygon(screen, edge_color, (arrow_tip, arrow_left, arrow_right))

    bar_width = 70
    bar_height = 8
    bar_x = round(center.x - bar_width / 2)
    bar_y = round(center.y - ACTOR_RADIUS - 20)
    health_fraction = actor["health"] / ACTOR_MAX_HEALTH
    pygame.draw.rect(screen, (26, 29, 36), (bar_x, bar_y, bar_width, bar_height))
    pygame.draw.rect(
        screen,
        HEALTH_COLOR,
        (bar_x, bar_y, round(bar_width * health_fraction), bar_height),
    )
    pygame.draw.rect(
        screen,
        edge_color,
        (bar_x, bar_y, bar_width, bar_height),
        width=1,
    )


def make_vision_render_buffers(screen_size, walls):
    """Allocate efficient half-resolution masks plus full-size display masks."""
    mask_size = (
        max(1, round(screen_size[0] * VISION_MASK_SCALE)),
        max(1, round(screen_size[1] * VISION_MASK_SCALE)),
    )

    return {
        "mask_size": mask_size,
        "wall_mask_low": pygame.Surface(mask_size, pygame.SRCALPHA),
        "wall_occlusion_low": pygame.Surface(mask_size, pygame.SRCALPHA),
        "actor_mask": pygame.Surface(screen_size, pygame.SRCALPHA),
        "actor_mask_cache": pygame.Surface(screen_size, pygame.SRCALPHA),
        "wall_mask": pygame.Surface(screen_size, pygame.SRCALPHA),
        "wall_mask_cache": pygame.Surface(screen_size, pygame.SRCALPHA),
        "wall_piece_masks": [
            pygame.Surface(
                (
                    max(1, math.ceil(wall.width * VISION_MASK_SCALE) + 2),
                    max(1, math.ceil(wall.height * VISION_MASK_SCALE) + 2),
                ),
                pygame.SRCALPHA,
            )
            for wall in walls
        ],
        "wall_detail_layers": [
            pygame.Surface((wall.width, wall.height), pygame.SRCALPHA)
            for wall in walls
        ],
        "actor_object_layer": pygame.Surface((160, 140), pygame.SRCALPHA),
        "bullet_object_layer": pygame.Surface((24, 24), pygame.SRCALPHA),
        "shadow_layer": pygame.Surface(screen_size, pygame.SRCALPHA),
    }


def scale_mask_points(points):
    """Convert screen-space polygon points to the smaller mask surface."""
    return [
        (
            round(point[0] * VISION_MASK_SCALE),
            round(point[1] * VISION_MASK_SCALE),
        )
        for point in points
    ]


def make_scaled_screen_rect(wall, camera):
    """Return the wall's mask-space rectangle without losing edge pixels."""
    left = math.floor((wall.left - camera.x) * VISION_MASK_SCALE)
    top = math.floor((wall.top - camera.y) * VISION_MASK_SCALE)
    right = math.ceil((wall.right - camera.x) * VISION_MASK_SCALE)
    bottom = math.ceil((wall.bottom - camera.y) * VISION_MASK_SCALE)
    return pygame.Rect(left, top, right - left, bottom - top)


def get_wall_distance_squared(player_position, wall):
    """Return squared distance from the player to the wall's nearest point."""
    nearest_x = max(wall.left, min(player_position.x, wall.right))
    nearest_y = max(wall.top, min(player_position.y, wall.bottom))
    difference = pygame.Vector2(nearest_x, nearest_y) - player_position
    return difference.length_squared()


def calculate_wall_shadow_polygon(
    wall,
    player_position,
    camera,
):
    """Return the diagonal shadow wedge cast behind one rectangular wall."""
    corners = [
        pygame.Vector2(wall.topleft),
        pygame.Vector2(wall.topright),
        pygame.Vector2(wall.bottomright),
        pygame.Vector2(wall.bottomleft),
    ]
    angle_corners = [
        (
            math.atan2(
                corner.y - player_position.y,
                corner.x - player_position.x,
            )
            % math.tau,
            corner,
        )
        for corner in corners
    ]
    angle_corners.sort(key=lambda item: item[0])

    # The two corners surrounding the largest empty angular gap form the
    # silhouette edges seen from the player.
    largest_gap_index = 0
    largest_gap = -1.0
    for index in range(len(angle_corners)):
        current_angle = angle_corners[index][0]
        next_angle = angle_corners[(index + 1) % len(angle_corners)][0]
        if index == len(angle_corners) - 1:
            next_angle += math.tau
        angle_gap = next_angle - current_angle
        if angle_gap > largest_gap:
            largest_gap = angle_gap
            largest_gap_index = index

    first_corner = angle_corners[
        (largest_gap_index + 1) % len(angle_corners)
    ][1]
    second_corner = angle_corners[largest_gap_index][1]

    first_direction = first_corner - player_position
    second_direction = second_corner - player_position
    if first_direction.length_squared() > 0:
        first_direction = first_direction.normalize()
    if second_direction.length_squared() > 0:
        second_direction = second_direction.normalize()

    shadow_distance = VISION_MAX_DISTANCE * 2
    first_far = player_position + first_direction * shadow_distance
    second_far = player_position + second_direction * shadow_distance

    return [
        (
            round(first_corner.x - camera.x),
            round(first_corner.y - camera.y),
        ),
        (
            round(first_far.x - camera.x),
            round(first_far.y - camera.y),
        ),
        (
            round(second_far.x - camera.x),
            round(second_far.y - camera.y),
        ),
        (
            round(second_corner.x - camera.x),
            round(second_corner.y - camera.y),
        ),
    ]


def update_wall_visibility_mask(
    player_position,
    walls,
    camera,
    buffers,
):
    """Build the local player's special whole-section wall visibility mask."""
    wall_mask = buffers["wall_mask"]
    wall_mask_low = buffers["wall_mask_low"]
    wall_occlusion = buffers["wall_occlusion_low"]
    wall_piece_masks = buffers["wall_piece_masks"]
    mask_rect = wall_mask_low.get_rect()
    wall_mask_low.fill((255, 255, 255, 0))
    wall_occlusion.fill((0, 0, 0, 0))

    ordered_wall_indices = sorted(
        range(len(walls)),
        key=lambda index: get_wall_distance_squared(
            player_position,
            walls[index],
        ),
    )

    for wall_index in ordered_wall_indices:
        wall = walls[wall_index]
        wall_piece_mask = wall_piece_masks[wall_index]
        wall_piece_mask.fill((255, 255, 255, 255))
        wall_screen_rect = make_scaled_screen_rect(wall, camera)
        visible_wall_rect = wall_screen_rect.clip(mask_rect)

        if visible_wall_rect.width > 0 and visible_wall_rect.height > 0:
            local_destination = (
                visible_wall_rect.left - wall_screen_rect.left,
                visible_wall_rect.top - wall_screen_rect.top,
            )
            wall_piece_mask.blit(
                wall_occlusion,
                local_destination,
                area=visible_wall_rect,
                special_flags=pygame.BLEND_RGBA_SUB,
            )
            wall_mask_low.blit(
                wall_piece_mask,
                wall_screen_rect.topleft,
                area=pygame.Rect(
                    0,
                    0,
                    wall_screen_rect.width,
                    wall_screen_rect.height,
                ),
                special_flags=pygame.BLEND_RGBA_MAX,
            )

        # The wall casts only onto farther sections, never onto itself.
        shadow_polygon = calculate_wall_shadow_polygon(
            wall,
            player_position,
            camera,
        )
        pygame.draw.polygon(
            wall_occlusion,
            (0, 0, 0, 255),
            scale_mask_points(shadow_polygon),
        )

    # Enlarge only after all polygons have been combined. This removes the
    # dotted diagonal seams caused by overlapping antialiased polygons.
    pygame.transform.smoothscale(
        wall_mask_low,
        wall_mask.get_size(),
        wall_mask,
    )


def update_visibility_masks(
    visible_polygon,
    player_position,
    walls,
    camera,
    buffers,
    refresh_visibility=True,
):
    """Build actor and wall masks from only the local player's visibility."""
    if refresh_visibility:
        actor_mask = buffers["actor_mask"]
        actor_mask.fill((255, 255, 255, 0))
        if len(visible_polygon) >= 3:
            screen_polygon = [
                (round(point[0]), round(point[1]))
                for point in visible_polygon
            ]
            pygame.draw.polygon(
                actor_mask,
                (255, 255, 255, 255),
                screen_polygon,
            )

        update_wall_visibility_mask(
            player_position,
            walls,
            camera,
            buffers,
        )


def save_visibility_cache(buffers):
    """Remember the newest actor and wall masks between vision updates."""
    for mask_name in ("actor_mask", "wall_mask"):
        cache = buffers[f"{mask_name}_cache"]
        cache.fill((255, 255, 255, 0))
        cache.blit(buffers[mask_name], (0, 0))


def restore_visibility_cache(buffers, cached_camera, current_camera):
    """Camera-align cached actor and wall views without recalculating them."""
    offset = (
        round(cached_camera.x - current_camera.x),
        round(cached_camera.y - current_camera.y),
    )
    for mask_name in ("actor_mask", "wall_mask"):
        mask = buffers[mask_name]
        mask.fill((255, 255, 255, 0))
        mask.blit(buffers[f"{mask_name}_cache"], offset)


def blit_surface_through_mask(
    screen,
    source_surface,
    visibility_mask,
    destination,
):
    """Clip one small object surface without processing the whole screen."""
    destination_rect = source_surface.get_rect(topleft=destination)
    clipped_rect = destination_rect.clip(screen.get_rect())
    if clipped_rect.width <= 0 or clipped_rect.height <= 0:
        return

    source_area = pygame.Rect(
        clipped_rect.left - destination_rect.left,
        clipped_rect.top - destination_rect.top,
        clipped_rect.width,
        clipped_rect.height,
    )
    source_surface.blit(
        visibility_mask,
        source_area.topleft,
        area=clipped_rect,
        special_flags=pygame.BLEND_RGBA_MULT,
    )
    screen.blit(source_surface, clipped_rect.topleft, area=source_area)


def draw_visible_wall_details(
    screen,
    walls,
    bullet_marks,
    camera,
    visibility_mask,
    wall_layers,
):
    """Restore visible wall color using wall-sized surfaces instead of 1080p."""
    for wall_index, wall in enumerate(walls):
        destination = (
            round(wall.left - camera.x),
            round(wall.top - camera.y),
        )
        destination_rect = pygame.Rect(
            destination,
            (wall.width, wall.height),
        )
        if not destination_rect.colliderect(screen.get_rect()):
            continue

        wall_layer = wall_layers[wall_index]
        wall_layer.fill((0, 0, 0, 0))
        local_rect = wall_layer.get_rect()
        pygame.draw.rect(
            wall_layer,
            WALL_COLOR,
            local_rect,
            border_radius=5,
        )
        pygame.draw.rect(
            wall_layer,
            WALL_EDGE_COLOR,
            local_rect,
            width=3,
            border_radius=5,
        )
        draw_bullet_marks(
            wall_layer,
            bullet_marks,
            pygame.Vector2(wall.topleft),
            only_wall=wall,
        )
        blit_surface_through_mask(
            screen,
            wall_layer,
            visibility_mask,
            destination,
        )


def draw_visible_actors_and_bullets(
    screen,
    font,
    actors,
    bullets,
    camera,
    visibility_mask,
    actor_layer,
    bullet_layer,
):
    """Partially reveal enemies and bullets using the player's vision mask."""
    actor_center = pygame.Vector2(
        actor_layer.get_width() / 2,
        actor_layer.get_height() / 2,
    )
    actor_screen_rect = screen.get_rect().inflate(200, 200)
    for actor in actors:
        # Blue teammates are drawn later without a vision mask so their
        # position, health, and condition remain readable through cover.
        if actor["is_player"] or actor["team"] == "blue":
            continue
        screen_center = actor["position"] - camera
        if not actor_screen_rect.collidepoint(screen_center):
            continue
        destination = (
            round(screen_center.x - actor_center.x),
            round(screen_center.y - actor_center.y),
        )
        actor_layer.fill((0, 0, 0, 0))
        local_camera = actor["position"] - actor_center
        draw_actor(actor_layer, font, actor, local_camera)
        blit_surface_through_mask(
            screen,
            actor_layer,
            visibility_mask,
            destination,
        )

    bullet_center = pygame.Vector2(
        bullet_layer.get_width() / 2,
        bullet_layer.get_height() / 2,
    )
    bullet_screen_rect = screen.get_rect().inflate(48, 48)
    for bullet in bullets:
        screen_center = bullet["position"] - camera
        if not bullet_screen_rect.collidepoint(screen_center):
            continue
        destination = (
            round(screen_center.x - bullet_center.x),
            round(screen_center.y - bullet_center.y),
        )
        bullet_layer.fill((0, 0, 0, 0))
        bullet_color = (
            BULLET_COLOR if bullet["team"] == "blue" else (255, 105, 92)
        )
        pygame.draw.circle(
            bullet_layer,
            bullet_color,
            (round(bullet_center.x), round(bullet_center.y)),
            bullet["radius"],
        )
        blit_surface_through_mask(
            screen,
            bullet_layer,
            visibility_mask,
            destination,
        )


def draw_vision_shadow(screen, visible_polygon, shadow_layer):
    """Darken terrain outside the local player's line of sight."""
    shadow_layer.fill(VISION_SHADOW_COLOR)

    if len(visible_polygon) >= 3:
        pygame.draw.polygon(
            shadow_layer,
            (0, 0, 0, 0),
            visible_polygon,
        )

    screen.blit(shadow_layer, (0, 0))


def draw_match_actors(screen, font, actors, camera, include_player=False):
    """Draw either the masked bots or the unmasked local player."""
    for actor in actors:
        if actor["is_player"] != include_player:
            continue
        draw_actor(screen, font, actor, camera)


def draw_teammate_information(screen, font, actors, camera):
    """Always show blue teammates and their health while they are on-screen."""
    screen_rect = screen.get_rect().inflate(200, 200)
    for actor in actors:
        if actor["team"] != "blue" or actor["is_player"]:
            continue
        if not screen_rect.collidepoint(actor["position"] - camera):
            continue
        draw_actor(screen, font, actor, camera)


def draw_revive_prompt(screen, font, player, actors, walls, camera):
    """Show the hold key only when a downed teammate is within reach."""
    if not actor_can_fight(player):
        return

    downed_ally = find_nearest_actor(
        player,
        actors,
        team="blue",
        downed_only=True,
    )
    if (
        downed_ally is None
        or player["position"].distance_to(downed_ally["position"]) > REVIVE_RANGE
        or not has_line_of_sight(
            player["position"],
            downed_ally["position"],
            walls,
        )
    ):
        return

    center = downed_ally["position"] - camera
    prompt = font.render("HOLD E TO REVIVE", True, TEXT_COLOR)
    background = prompt.get_rect(center=(round(center.x), round(center.y + 55)))
    background.inflate_ip(18, 10)
    pygame.draw.rect(screen, (10, 13, 18), background, border_radius=5)
    screen.blit(prompt, prompt.get_rect(center=background.center))


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
        "FIRST MATCH LABORATORY 0.5",
        "WASD Move | SHIFT Run | LMB Fire | E Revive | R Reload | 1/2/3 Swap",
        f"Position: ({player_position.x:.1f}, {player_position.y:.1f})",
        f"Facing: {math.degrees(aim_angle):.1f} degrees",
        f"Movement: {movement_state}",
        f"Current speed: {actual_speed:.0f} pixels/second",
        f"{active_weapon['name']} spread: {spread_percent * 100:.0f}%",
        f"Stamina: {stamina:.0f} / {MAX_STAMINA}",
        f"FPS: {current_fps:.0f} / target {FPS}",
    ]

    panel = pygame.Surface((700, 253), pygame.SRCALPHA)
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
    player,
):
    """Display ammunition and the local player's combat condition."""
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

    if player["eliminated"]:
        player_status = "YOU: ELIMINATED"
    elif player["downed"]:
        player_status = "YOU: DOWNED - WAIT FOR AN ALLY"
    else:
        player_status = f"Health: {player['health']} / {ACTOR_MAX_HEALTH}"

    player_text = regular_font.render(player_status, True, TEXT_COLOR)
    life_text = regular_font.render(
        f"Downs used: {player['times_downed']} / 2",
        True,
        TEXT_COLOR,
    )
    screen.blit(player_text, (panel_x + 18, panel_y + 142))
    screen.blit(life_text, (panel_x + 18, panel_y + 168))


def count_team_states(actors, team):
    """Return standing, downed, and eliminated counts for one team."""
    team_actors = [actor for actor in actors if actor["team"] == team]
    standing = sum(actor_can_fight(actor) for actor in team_actors)
    downed = sum(actor["downed"] for actor in team_actors)
    eliminated = sum(actor["eliminated"] for actor in team_actors)
    return standing, downed, eliminated


def draw_match_panel(screen, font, scores, round_number, actors):
    """Show the first-to-five score and current team conditions."""
    blue_state = count_team_states(actors, "blue")
    red_state = count_team_states(actors, "red")
    lines = [
        f"BLUE  {scores['blue']}  -  {scores['red']}  RED",
        f"ROUND {round_number}    FIRST TO {ROUNDS_TO_WIN}",
        f"Up {blue_state[0]}-{red_state[0]}   "
        f"Down {blue_state[1]}-{red_state[1]}   "
        f"Out {blue_state[2]}-{red_state[2]}",
    ]

    panel = pygame.Surface((460, 92), pygame.SRCALPHA)
    panel.fill((10, 13, 18, 220))
    panel_x = screen.get_width() - panel.get_width() - 18
    screen.blit(panel, (panel_x, 18))
    panel_center_x = panel_x + panel.get_width() // 2

    for index, line in enumerate(lines):
        rendered = font.render(line, True, TEXT_COLOR)
        screen.blit(
            rendered,
            rendered.get_rect(center=(panel_center_x, 36 + index * 25)),
        )


def draw_round_banner(screen, regular_font, large_font, match_state):
    """Display round and match results during the transition pause."""
    if match_state["phase"] == "playing":
        return

    panel = pygame.Surface((720, 180), pygame.SRCALPHA)
    panel.fill((8, 10, 15, 235))
    panel_rect = panel.get_rect(center=screen.get_rect().center)
    screen.blit(panel, panel_rect)

    title = large_font.render(match_state["message"], True, TEXT_COLOR)
    screen.blit(
        title,
        title.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 25)),
    )

    if match_state["phase"] == "match_over":
        instruction = "Press ENTER to start a new match"
    else:
        instruction = f"Next round in {max(0.0, match_state['timer']):.1f}"
    instruction_text = regular_font.render(instruction, True, (182, 198, 218))
    screen.blit(
        instruction_text,
        instruction_text.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 2 + 32)
        ),
    )


def reset_round(actors, weapon_states, bullets, bullet_marks):
    """Reset actors, ammunition, projectiles, and marks for a clean round."""
    for actor in actors:
        reset_actor_for_round(actor)
    for index, weapon in enumerate(WEAPONS):
        weapon_states[index] = make_weapon_state(weapon)
    bullets.clear()
    clear_bullet_marks(bullet_marks)


def begin_new_match(match_state, scores, actors, weapon_states, bullets, bullet_marks):
    """Restore the score and begin round one."""
    scores["blue"] = 0
    scores["red"] = 0
    match_state["phase"] = "playing"
    match_state["timer"] = 0.0
    match_state["message"] = ""
    match_state["round_number"] = 1
    reset_round(actors, weapon_states, bullets, bullet_marks)


def main():
    pygame.init()

    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Riftbound - First Match Laboratory")
    pygame.mouse.set_visible(False)

    clock = pygame.time.Clock()
    debug_font = pygame.font.Font(None, 26)
    ammunition_font = pygame.font.Font(None, 48)
    walls = make_walls()
    vision_buffers = make_vision_render_buffers(screen.get_size(), walls)
    wall_segments = get_wall_segments(walls)
    wall_corners = get_wall_corners(walls)
    actors = make_match_actors()
    player = actors[0]

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
    scores = {"blue": 0, "red": 0}
    match_state = {
        "phase": "playing",
        "timer": 0.0,
        "message": "",
        "round_number": 1,
    }
    vision_frames_since_update = VISION_RENDER_FRAMES_PER_UPDATE
    cached_world_polygon = []
    cached_vision_camera = pygame.Vector2()
    game_running = True

    while game_running:
        # Delta time keeps movement, bullets, and timers consistent at any frame rate.
        delta_time = min(clock.tick(FPS) / 1000.0, 0.05)
        reload_requested = False
        weapon_switch_requested = None
        trigger_just_pressed = False
        restart_requested = False

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
                elif event.key == pygame.K_RETURN:
                    restart_requested = True
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                trigger_just_pressed = True

        if restart_requested and match_state["phase"] == "match_over":
            begin_new_match(
                match_state,
                scores,
                actors,
                weapon_states,
                bullets,
                bullet_marks,
            )
            active_weapon_index = 0
            stamina = MAX_STAMINA
            sprint_exhausted = False
            camera_recoil_offset.update(0, 0)
            camera_recoil_velocity.update(0, 0)
            camera_shake_strength = 0.0
            vision_frames_since_update = VISION_RENDER_FRAMES_PER_UPDATE

        if match_state["phase"] == "round_over":
            match_state["timer"] -= delta_time
            if match_state["timer"] <= 0:
                match_state["round_number"] += 1
                reset_round(actors, weapon_states, bullets, bullet_marks)
                match_state["phase"] = "playing"
                match_state["message"] = ""
                stamina = MAX_STAMINA
                sprint_exhausted = False
                camera_recoil_offset.update(0, 0)
                camera_recoil_velocity.update(0, 0)
                camera_shake_strength = 0.0
                vision_frames_since_update = VISION_RENDER_FRAMES_PER_UPDATE

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
        player_can_act = (
            match_state["phase"] == "playing" and actor_can_fight(player)
        )
        if not player_can_act:
            movement_direction.update(0, 0)

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
        move_player(player["position"], movement, walls)

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
        base_camera = calculate_camera(player["position"], screen.get_size())
        camera = apply_camera_effects(
            base_camera,
            camera_recoil_offset,
            camera_shake_strength,
            screen.get_size(),
        )
        mouse_screen_position = pygame.Vector2(pygame.mouse.get_pos())
        mouse_world_position = mouse_screen_position + camera
        aim_vector = mouse_world_position - player["position"]
        if aim_vector.length_squared() > 0:
            aim_angle = math.atan2(aim_vector.y, aim_vector.x)
        player["aim_angle"] = aim_angle

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
            player_can_act
            and match_state["phase"] == "playing"
            and firing
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
                        player,
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

        if match_state["phase"] == "playing":
            reset_revival_sources(actors)

            keys = pygame.key.get_pressed()
            if player_can_act and keys[pygame.K_e]:
                downed_ally = find_nearest_actor(
                    player,
                    actors,
                    team="blue",
                    downed_only=True,
                )
                try_revive(player, downed_ally, delta_time, walls)

            for actor in actors:
                if not actor["is_player"]:
                    update_bot(actor, actors, walls, bullets, delta_time)

            separate_standing_actors(actors, walls)
            finish_unattended_revives(actors)
            bullets = update_bullets(
                bullets,
                delta_time,
                walls,
                actors,
                bullet_marks,
            )

            blue_standing = team_has_standing_actor(actors, "blue")
            red_standing = team_has_standing_actor(actors, "red")
            if not blue_standing or not red_standing:
                bullets.clear()
                clear_bullet_marks(bullet_marks)

                if blue_standing and not red_standing:
                    winner = "blue"
                    round_message = "BLUE WINS THE ROUND"
                elif red_standing and not blue_standing:
                    winner = "red"
                    round_message = "RED WINS THE ROUND"
                else:
                    winner = None
                    round_message = "ROUND DRAW"

                if winner is not None:
                    scores[winner] += 1

                if winner is not None and scores[winner] >= ROUNDS_TO_WIN:
                    match_state["phase"] = "match_over"
                    match_state["message"] = f"{winner.upper()} WINS THE MATCH"
                else:
                    match_state["phase"] = "round_over"
                    match_state["timer"] = ROUND_END_DELAY
                    match_state["message"] = round_message

        update_bullet_marks(bullet_marks, delta_time)
        # Only the local player's line of sight controls the world. Teammates
        # are shown separately as always-readable blue position/health markers.
        # Visibility geometry updates every second rendered frame and cached
        # polygons remain camera-aligned between calculations.
        vision_frames_since_update += 1
        refresh_visibility = (
            vision_frames_since_update >= VISION_RENDER_FRAMES_PER_UPDATE
            or not cached_world_polygon
        )
        if refresh_visibility:
            vision_frames_since_update = 0
            world_camera = pygame.Vector2()
            cached_world_polygon = calculate_vision_polygon(
                player["position"],
                walls,
                world_camera,
                wall_segments,
                wall_corners,
            )

        visible_polygon = [
            (
                world_point[0] - camera.x,
                world_point[1] - camera.y,
            )
            for world_point in cached_world_polygon
        ]
        update_visibility_masks(
            visible_polygon,
            player["position"],
            walls,
            camera,
            vision_buffers,
            refresh_visibility=refresh_visibility,
        )
        if refresh_visibility:
            save_visibility_cache(vision_buffers)
            cached_vision_camera.update(camera)
        else:
            restore_visibility_cache(
                vision_buffers,
                cached_vision_camera,
                camera,
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

        # Restore normal wall color through wall-sized masks. Avoiding a full
        # 1920x1080 temporary surface here saves several million pixel
        # operations every frame.
        draw_visible_wall_details(
            screen,
            walls,
            bullet_marks,
            camera,
            vision_buffers["wall_mask"],
            vision_buffers["wall_detail_layers"],
        )

        # Bots and bullets retain exact partial visibility, but only their
        # small bounding surfaces are multiplied by the visibility mask.
        draw_visible_actors_and_bullets(
            screen,
            debug_font,
            actors,
            bullets,
            camera,
            vision_buffers["actor_mask"],
            vision_buffers["actor_object_layer"],
            vision_buffers["bullet_object_layer"],
        )

        # Teammates do not reveal the world or enemies. Only their own marker,
        # health bar, and downed/eliminated state remain visible through cover.
        draw_teammate_information(
            screen,
            debug_font,
            actors,
            camera,
        )

        draw_match_actors(
            screen,
            debug_font,
            actors,
            camera,
            include_player=True,
        )
        if match_state["phase"] == "playing":
            draw_revive_prompt(
                screen,
                debug_font,
                player,
                actors,
                walls,
                camera,
            )
        draw_debug_panel(
            screen,
            debug_font,
            player["position"],
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
            player,
        )
        draw_stamina_panel(
            screen,
            debug_font,
            stamina,
            sprinting,
            sprint_exhausted,
        )
        draw_match_panel(
            screen,
            debug_font,
            scores,
            match_state["round_number"],
            actors,
        )
        draw_crosshair(screen, pygame.mouse.get_pos(), current_spread)
        draw_round_banner(
            screen,
            debug_font,
            ammunition_font,
            match_state,
        )

        pygame.display.flip()

    pygame.mouse.set_visible(True)
    pygame.quit()


if __name__ == "__main__":
    main()