import heapq
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
WORLD_WIDTH = 3200
WORLD_HEIGHT = 2200

MAX_STAMINA = 100
SPRINT_STAMINA_DRAIN_PER_SECOND = 30
SPRINT_STAMINA_REGEN_PER_SECOND = 15
SPRINT_RECOVERY_THRESHOLD = 20

# -----------------------------------------------------------------------------
# SHOOTING LABORATORY SETTINGS
# Keeping weapon values together makes balancing and adding weapons easier.
# -----------------------------------------------------------------------------
KNIFE = {
    "slot": 1,
    "name": "Knife",
    "price": 0,
    "fire_mode": "melee",
    "damage": 50,
    "melee_range": 105,
    "melee_arc_degrees": 80,
    "seconds_per_shot": 0.50,
    "attack_animation_time": 0.18,
    "magazine_size": 0,
    "starting_reserve_ammo": 0,
    "reload_time": 0.0,
    "standing_spread": 0.0,
    "walking_spread": 0.0,
    "running_spread": 0.0,
    "sustained_spread_per_shot": 0.0,
    "maximum_sustained_spread": 0.0,
}

PISTOL = {
    "slot": 2,
    "name": "Pistol",
    "price": 0,
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
    "tap_camera_shake": 5.0,
    "sustained_camera_kick": 0.0,
    "sustained_camera_sway": 0.0,
}

RIFLE = {
    "slot": 3,
    "name": "Rifle",
    "price": 700,
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
    "sustained_spread_per_shot": 0.009,
    "maximum_sustained_spread": 0.07,
    "tap_camera_shake": 6.0,
    "sustained_camera_kick": 155.0,
    "sustained_camera_sway": 90.0,
}

SHOTGUN = {
    "slot": 4,
    "name": "Shotgun",
    "price": 600,
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
    "tap_camera_shake": 8.0,
    "sustained_camera_kick": 0.0,
    "sustained_camera_sway": 0.0,
}

WEAPONS = [KNIFE, PISTOL, RIFLE, SHOTGUN]

CAMERA_RECOIL_SPRING = 120.0
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
# While the player moves, recalculate visibility every second rendered frame.
# While stationary, reuse the cached geometry until movement or cover changes.
VISION_RENDER_FRAMES_PER_UPDATE = 2
# Wall-shadow geometry is calculated at half resolution, then smoothly scaled.
# Actors keep a fast full-size mask so only one mask is enlarged each frame.
VISION_MASK_SCALE = 0.5
# The alpha value keeps concealed terrain readable instead of covering it.
# Visible terrain keeps its normal color; concealed terrain is darkened.
VISION_SHADOW_COLOR = (10, 12, 18, 175)

# -----------------------------------------------------------------------------
# RIFT HUNT 0.6 SETTINGS
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

RIFT_LOCATIONS = [
    {"name": "NORTH", "position": (1650, 520)},
    {"name": "EAST", "position": (2450, 1050)},
    {"name": "SOUTH", "position": (1650, 1620)},
]
RIFT_RADIUS = 145
RIFT_CAPTURE_TIME = 5.0
RIFT_HOLD_TIME_TO_WIN = 60.0
RIFT_CAPTURE_DECAY_PER_SECOND = 1.0
RIFT_INTEL_INTERVAL = 5.0
RIFT_INTEL_DURATION = 1.5
RIFT_NEUTRAL_COLOR = (151, 102, 219)
RIFT_BLUE_COLOR = (73, 188, 255)
RIFT_RED_COLOR = (255, 91, 105)
RIFT_CONTESTED_COLOR = (255, 194, 75)

# -----------------------------------------------------------------------------
# ECONOMY 0.7 SETTINGS
# Credits persist between rounds but reset when a completely new match begins.
# The small win/loss reward gap reduces economy snowballing while we test it.
# -----------------------------------------------------------------------------
STARTING_CREDITS = 800
ROUND_WIN_CREDITS = 700
ROUND_LOSS_CREDITS = 500
ROUND_DRAW_CREDITS = 600
MAX_CREDITS = 9000
CHARACTER_SELECT_DURATION = 20.0
BUY_PHASE_DURATION = 15.0
MAX_OWNED_WEAPONS = 3
STARTING_WEAPON_INDICES = (0, 1)
WEAPON_SHARE_RANGE = 100
WEAPON_SHARE_DRAW_DISTANCE = 520
DROPPED_WEAPON_RADIUS = 18
SHARE_STATUS_DURATION = 2.5

# Bots make one shop decision per Buy Phase. They sometimes save instead of
# automatically filling the third slot, which keeps the economy less predictable
# and leaves occasional opportunities for the player to share a weapon with them.
BOT_BUY_CHANCE = 0.70
BOT_RIFLE_BUY_CHANCE = 0.60

# Team Rift Energy is shared by each team, persists between rounds, and resets
# only when a completely new match begins. Environmental purchases will spend it
# in the next economy update.
STARTING_TEAM_RIFT_ENERGY = 0
MAX_TEAM_RIFT_ENERGY = 100
RIFT_ENERGY_REVIVE_REWARD = 5
RIFT_ENERGY_ANCHOR_BREAK_REWARD = 10
RIFT_ENERGY_CAPTURE_REWARD = 10
RIFT_ENERGY_CONTROL_INTERVAL = 5.0
RIFT_ENERGY_CONTROL_REWARD = 3
RIFT_ENERGY_ROUND_WIN_REWARD = 10

# -----------------------------------------------------------------------------
# CHARACTERS 0.8 SETTINGS
# Each playable character keeps statistics, ability balance, and placeholder-art
# colors together so the roster can grow without rewriting shared game systems.
# -----------------------------------------------------------------------------
MALPHAS = {
    "id": "malphas",
    "name": "Malphas",
    "class": "Phantom",
    "max_health": 110,
    "move_speed": 260,
    "sprint_multiplier": 1.32,
    "max_stamina": 105,
}

LONGSHOT = {
    "id": "longshot",
    "name": "Longshot",
    "class": "Hunter",
    "max_health": 95,
    "move_speed": 245,
    "sprint_multiplier": 1.25,
    "max_stamina": 100,
}

VAREK = {
    "id": "varek",
    "name": "Varek",
    "class": "Breaker",
    "max_health": 105,
    "move_speed": 255,
    "sprint_multiplier": 1.30,
    "max_stamina": 110,
}

MIRI = {
    "id": "miri",
    "name": "Miri",
    "class": "Guardian",
    "max_health": 80,
    "move_speed": 250,
    "sprint_multiplier": 1.35,
    "max_stamina": 115,
}

RELAY = {
    "id": "relay",
    "name": "Relay",
    "class": "Conduit",
    "max_health": 100,
    "move_speed": 250,
    "sprint_multiplier": 1.30,
    "max_stamina": 100,
}

HAZE = {
    "id": "haze",
    "name": "Haze",
    "class": "Phantom",
    "max_health": 95,
    "move_speed": 275,
    "sprint_multiplier": 1.30,
    "max_stamina": 100,
}

SABLE = {
    "id": "sable",
    "name": "Sable",
    "class": "Hunter",
    "max_health": 100,
    "move_speed": 250,
    "sprint_multiplier": 1.30,
    "max_stamina": 120,
}

AUREL = {
    "id": "aurel",
    "name": "Aurel",
    "class": "Breaker",
    "max_health": 95,
    "move_speed": 260,
    "sprint_multiplier": 1.30,
    "max_stamina": 110,
}

CHARACTER_ROSTER = [
    {**MALPHAS, "implemented": True},
    {**LONGSHOT, "implemented": True},
    {**VAREK, "implemented": True},
    {**MIRI, "implemented": True},
    {**RELAY, "implemented": True},
    {**HAZE, "implemented": True},
    {**SABLE, "implemented": True},
    {**AUREL, "implemented": True},
]

# Malphas - Phantom
MALPHAS_HELLSTEP_RANGE = 650
MALPHAS_HELLSTEP_DELAY = 0.65
MALPHAS_HELLSTEP_COOLDOWN = 8.0

MALPHAS_SILENCE_DURATION = 4.5
MALPHAS_SILENCE_COOLDOWN = 12.0
MALPHAS_WALK_SOUND_RADIUS = 180
MALPHAS_RUN_SOUND_RADIUS = 430
MALPHAS_SOUND_MEMORY = 1.5

MALPHAS_BLOODLUST_DURATION = 8.0
MALPHAS_BLOODLUST_RADIUS = 400
MALPHAS_BLOODLUST_DRAIN_PER_SECOND = 6.0
MALPHAS_BLOODLUST_HEAL_FRACTION = 0.30
MALPHAS_BLOODLUST_ELIMINATION_HEALTH_FRACTION = 0.80

MALPHAS_BODY_COLOR = (77, 34, 60)
MALPHAS_GLOW_COLOR = (210, 62, 115)
MALPHAS_HORN_COLOR = (235, 207, 224)
MALPHAS_EFFECT_COLOR = (227, 67, 92)

# Longshot - Hunter
LONGSHOT_RESONANCE_RADIUS = 900
LONGSHOT_RESONANCE_COOLDOWN = 12.0
LONGSHOT_RESONANCE_ECHO_DURATION = 2.4
LONGSHOT_RESONANCE_PULSE_DURATION = 0.75
LONGSHOT_MOVE_ACTIVITY_MEMORY = 0.35
LONGSHOT_FIRE_ACTIVITY_MEMORY = 0.55

LONGSHOT_TRACK_DURATION = 6.0
LONGSHOT_TRACK_COOLDOWN = 14.0
LONGSHOT_TRACK_EVENT_LIFETIME = 5.0
LONGSHOT_TRACK_SAMPLE_INTERVAL = 0.30
LONGSHOT_TRACK_MAX_EVENTS_PER_ACTOR = 24

LONGSHOT_DEAD_LINE_SHOTS = 2
LONGSHOT_DEAD_LINE_DAMAGE = 150
LONGSHOT_DEAD_LINE_OBJECT_DAMAGE = 180
LONGSHOT_DEAD_LINE_AIM_TIME = 0.65
LONGSHOT_DEAD_LINE_RECOVERY = 1.35
LONGSHOT_DEAD_LINE_RANGE = 2400
LONGSHOT_DEAD_LINE_MAX_WALL_THICKNESS = 90
LONGSHOT_DEAD_LINE_TRACER_DURATION = 0.20

LONGSHOT_BODY_COLOR = (48, 61, 73)
LONGSHOT_ARMOR_COLOR = (102, 123, 139)
LONGSHOT_VISOR_COLOR = (90, 219, 255)
LONGSHOT_RIFLE_COLOR = (205, 219, 228)
LONGSHOT_EFFECT_COLOR = (72, 190, 255)
LONGSHOT_TRACK_COLOR = (125, 224, 255)

# Varek - Breaker
VAREK_ONI_BLADE_DURATION = 5.0
VAREK_ONI_BLADE_COOLDOWN = 10.0
VAREK_ONI_BLADE_DAMAGE = 70
VAREK_ONI_BLADE_RANGE = 140
VAREK_ONI_BLADE_ARC_DEGREES = 100
VAREK_ONI_BLADE_SECONDS_PER_SWING = 0.42
VAREK_ONI_BLADE_ANIMATION_TIME = 0.20

# Shared Breaker class ability. Breach Charge instantly destroys destructible
# cover in its cone, damages only enemies, and physically pushes both teams.
BREAKER_BREACH_COOLDOWN = 11.0
BREAKER_BREACH_RANGE = 280
BREAKER_BREACH_ARC_DEGREES = 70
BREAKER_BREACH_DAMAGE = 25
BREAKER_BREACH_PUSH_DISTANCE = 150
BREAKER_BREACH_EFFECT_DURATION = 0.28

VAREK_FURY_DURATION = 8.0
VAREK_FURY_SPEED_MULTIPLIER = 1.30
VAREK_FURY_EXTENSION_PER_ELIMINATION = 1.5
VAREK_FURY_MAX_REMAINING = 12.0

VAREK_ONI_BLADE = {
    "name": "Oni Blade",
    "fire_mode": "melee",
    "damage": VAREK_ONI_BLADE_DAMAGE,
    "melee_range": VAREK_ONI_BLADE_RANGE,
    "melee_arc_degrees": VAREK_ONI_BLADE_ARC_DEGREES,
    "seconds_per_shot": VAREK_ONI_BLADE_SECONDS_PER_SWING,
    "attack_animation_time": VAREK_ONI_BLADE_ANIMATION_TIME,
}

VAREK_BODY_COLOR = (75, 55, 48)
VAREK_ARMOR_COLOR = (121, 106, 91)
VAREK_MASK_COLOR = (222, 203, 173)
VAREK_BLADE_COLOR = (116, 215, 255)
VAREK_EFFECT_COLOR = (83, 174, 232)
VAREK_FURY_COLOR = (217, 91, 67)

# Miri - Guardian
MIRI_FELINE_LUNGE_DURATION = 6.0
MIRI_FELINE_LUNGE_COOLDOWN = 8.0
MIRI_CLAW_DAMAGE = 35
MIRI_CLAW_RANGE = 100
MIRI_CLAW_ARC_DEGREES = 90
MIRI_CLAW_SECONDS_PER_ATTACK = 0.35
MIRI_CLAW_ANIMATION_TIME = 0.16

MIRI_FIELD_TREATMENT_RADIUS = 180
MIRI_FIELD_TREATMENT_CAST_TIME = 1.0
MIRI_FIELD_TREATMENT_COOLDOWN = 12.0
MIRI_FIELD_TREATMENT_MISSING_HEALTH_FRACTION = 0.50
MIRI_FIELD_TREATMENT_MOVE_MULTIPLIER = 0.60

MIRI_NINE_LIVES_RANGE = 100
MIRI_NINE_LIVES_CHANNEL_TIME = 4.0
MIRI_NINE_LIVES_REVIVE_HEALTH = 50
MIRI_NINE_LIVES_MOVE_CANCEL_DISTANCE = 3.0

MIRI_BODY_COLOR = (237, 143, 185)
MIRI_COAT_COLOR = (242, 244, 247)
MIRI_EAR_COLOR = (245, 169, 203)
MIRI_EAR_INNER_COLOR = (255, 208, 226)
MIRI_HEAL_COLOR = (91, 225, 136)
MIRI_EFFECT_COLOR = (118, 255, 168)

# Relay - Conduit
RELAY_RIFT_BOOST_CHARGE_TIME = 3.0
RELAY_RIFT_BOOST_PROJECTILES = 20
RELAY_RIFT_BOOST_DAMAGE_MULTIPLIER = 1.20
RELAY_RIFT_BOOST_COOLDOWN = 10.0

RELAY_RIFT_TELEPORT_CHANNEL = 3.0
RELAY_RIFT_TELEPORT_COOLDOWN = 15.0
RELAY_RIFT_TELEPORT_SAFE_MARGIN = 110
RELAY_RIFT_TELEPORT_ATTEMPTS = 160

RELAY_RIFT_OVERCLOCK_HOLD_MULTIPLIER = 1.50

RELAY_BODY_COLOR = (173, 185, 195)
RELAY_JOINT_COLOR = (75, 91, 104)
RELAY_RIFT_COLOR = (168, 92, 235)
RELAY_CORE_COLOR = (104, 188, 255)
RELAY_BOOST_BULLET_COLOR = (190, 112, 255)

# Haze - Phantom
HAZE_HALLUCINATION_DURATION = 15.0
HAZE_HALLUCINATION_COOLDOWN = 10.0
HAZE_HALLUCINATION_SPEED = 250.0
HAZE_HALLUCINATION_FADE_TIME = 1.25
HAZE_CHILDS_PLAY_DURATION = 15.0
HAZE_CHILDS_PLAY_ILLUSIONS_PER_ENEMY = 3
HAZE_CHILD_ILLUSION_MOVE_SPEED = 72.0
HAZE_SPRAY_MARK_DURATION = 10.0

HAZE_BODY_COLOR = (73, 72, 79)
HAZE_CLOAK_COLOR = (91, 88, 101)
HAZE_SHADOW_COLOR = (19, 17, 27)
HAZE_PURPLE_COLOR = (173, 78, 235)
HAZE_GREEN_COLOR = (126, 255, 71)

# Sable - Hunter
SABLE_SCENT_RADIUS = 850
SABLE_SCENT_DURATION = 3.0
SABLE_SCENT_COOLDOWN = 10.0
SABLE_SCENT_HEALTH_THRESHOLD = 0.70
SABLE_DAMAGE_EVIDENCE_MEMORY = 2.5

SABLE_WILD_HUNT_DURATION = 12.0
SABLE_WILD_HUNT_SPEED_MULTIPLIER = 1.10
SABLE_WILD_HUNT_KNIFE_DAMAGE = 50
SABLE_WILD_HUNT_REVEAL_ON_HIT = 0.75
SABLE_WILD_HUNT_VIEW_ANGLE_DEGREES = 25.0

SABLE_HUNTING_KNIFE = {
    "name": "Hunting Knife",
    "fire_mode": "melee",
    "damage": SABLE_WILD_HUNT_KNIFE_DAMAGE,
    "melee_range": KNIFE["melee_range"],
    "melee_arc_degrees": KNIFE["melee_arc_degrees"],
    "seconds_per_shot": KNIFE["seconds_per_shot"],
    "attack_animation_time": KNIFE["attack_animation_time"],
}

SABLE_BODY_COLOR = (94, 84, 58)
SABLE_LEATHER_COLOR = (121, 91, 58)
SABLE_HAIR_COLOR = (74, 51, 34)
SABLE_WARPAINT_COLOR = (56, 120, 64)
SABLE_TRACK_COLOR = (111, 189, 92)
SABLE_CAMOUFLAGE_COLOR = (128, 158, 91)
SABLE_KNIFE_COLOR = (214, 221, 210)


# Aurel - Breaker
AUREL_CINDERBOLT_COOLDOWN = 10.0
AUREL_CINDERBOLT_SPEED = 1050.0
AUREL_CINDERBOLT_PROJECTILE_RADIUS = 12
AUREL_CINDERBOLT_EXPLOSION_RADIUS = 130
AUREL_CINDERBOLT_IMPACT_DAMAGE = 15
AUREL_CINDERBOLT_BURN_DURATION = 3.0
AUREL_CINDERBOLT_BURN_MAX_HEALTH_PER_SECOND = 0.05
AUREL_CINDERBOLT_PUSH_DISTANCE = 120
AUREL_CINDERBOLT_OBJECT_DAMAGE = 65
AUREL_CINDERBOLT_MAX_RANGE = VISION_MAX_DISTANCE
AUREL_CINDERBOLT_EXPLOSION_VISUAL_TIME = 0.45

AUREL_INFERNO_CHARGE_TIME = 2.0
AUREL_INFERNO_RADIUS = 800
AUREL_INFERNO_INITIAL_DAMAGE = 25
AUREL_INFERNO_PUSH_DISTANCE = 300
AUREL_INFERNO_BURN_DURATION = 6.0
AUREL_INFERNO_BURN_MAX_HEALTH_PER_SECOND = 0.08
AUREL_INFERNO_AFTEREFFECT_DURATION = 15.0
AUREL_INFERNO_WEAPON_DAMAGE_MULTIPLIER = 1.15
AUREL_INFERNO_EXPLOSION_VISUAL_TIME = 0.75

AUREL_FIRE_TRAIL_LIFETIME = 5.0
AUREL_FIRE_TRAIL_SPAWN_INTERVAL = 0.30
AUREL_FIRE_TRAIL_RADIUS = 42
AUREL_TRAIL_BURN_DURATION = 3.0
AUREL_TRAIL_BURN_MAX_HEALTH_PER_SECOND = 0.05

AUREL_BODY_COLOR = (236, 232, 219)
AUREL_SUIT_COLOR = (245, 242, 228)
AUREL_GOLD_COLOR = (222, 177, 72)
AUREL_HAIR_COLOR = (248, 246, 236)
AUREL_EYE_COLOR = (255, 210, 67)
AUREL_FIRE_COLOR = (244, 92, 34)
AUREL_FIRE_GOLD_COLOR = (255, 188, 46)
AUREL_INFERNO_COLOR = (156, 24, 24)

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


class UIButton:
    """Small reusable mouse-driven UI button used by menus and overlays."""

    def __init__(self, rectangle, label, action, enabled=True):
        self.rect = pygame.Rect(rectangle)
        self.label = label
        self.action = action
        self.enabled = enabled

    def contains(self, position):
        return self.enabled and self.rect.collidepoint(position)

    def draw(self, screen, font, mouse_position):
        hovered = self.contains(mouse_position)
        if not self.enabled:
            fill = (42, 46, 55)
            edge = (84, 90, 103)
            text_color = (125, 132, 145)
        elif hovered:
            fill = (48, 77, 103)
            edge = PLAYER_EDGE_COLOR
            text_color = TEXT_COLOR
        else:
            fill = (25, 31, 41)
            edge = (104, 126, 151)
            text_color = TEXT_COLOR

        pygame.draw.rect(screen, fill, self.rect, border_radius=8)
        pygame.draw.rect(screen, edge, self.rect, width=2, border_radius=8)
        label_surface = font.render(self.label, True, text_color)
        screen.blit(label_surface, label_surface.get_rect(center=self.rect.center))

# Destructible objects use warm material colors so they cannot be confused
# with the permanent gray concrete walls, even while terrain is darkened.
CRATE_MAX_HEALTH = 80
DOOR_MAX_HEALTH = 140
CRATE_COLOR = (151, 99, 52)
CRATE_EDGE_COLOR = (232, 177, 103)
HIDDEN_CRATE_COLOR = (68, 51, 38)
HIDDEN_CRATE_EDGE_COLOR = (106, 78, 54)
DOOR_COLOR = (121, 76, 46)
DOOR_EDGE_COLOR = (237, 188, 96)
HIDDEN_DOOR_COLOR = (62, 47, 39)
HIDDEN_DOOR_EDGE_COLOR = (111, 80, 57)

BLUE_SPAWNS = [(260, 240), (260, 1100), (260, 1960)]
RED_SPAWNS = [(2940, 240), (2940, 1100), (2940, 1960)]

# Each lane is a simple route around the laboratory walls. This is intentionally
# understandable waypoint AI; proper navigation can replace it later.
BOT_ROUTES = [
    [
        (300, 190),
        (1050, 180),
        (1650, 520),
        (2050, 520),
        (2450, 520),
        (2850, 300),
    ],
    [
        (300, 1100),
        (800, 950),
        (1200, 900),
        (1650, 850),
        (2050, 1050),
        (2450, 1050),
        (2850, 1100),
    ],
    [
        (300, 1960),
        (900, 1960),
        (1250, 1950),
        (1650, 1620),
        (2200, 1800),
        (2850, 1960),
    ],
]

# Bot navigation uses a lightweight grid only when a route must be calculated.
# The previous "best visible waypoint" system could select the waypoint a bot
# was already standing on forever. A 100-pixel grid is small enough to search
# quickly while still routing a full character-sized body around the laboratory.
BOT_NAVIGATION_GRID_SIZE = 100
BOT_NAVIGATION_REACHED_DISTANCE = 25
BOT_NAVIGATION_REPATH_DISTANCE = 260
BOT_NAVIGATION_TARGET_CHANGE_DISTANCE = 80


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
        # This wall has a 120-pixel opening occupied by a destructible door.
        pygame.Rect(1250, 300, 70, 150),
        pygame.Rect(1250, 570, 70, 120),
        pygame.Rect(420, 1050, 610, 70),
        pygame.Rect(1430, 930, 70, 420),
        pygame.Rect(1500, 1280, 480, 70),

        # Expanded east wing
        pygame.Rect(2200, 300, 500, 70),
        pygame.Rect(2630, 370, 70, 440),
        pygame.Rect(2050, 900, 70, 500),
        pygame.Rect(2300, 1450, 600, 70),
        pygame.Rect(2550, 1170, 360, 70),

        # Expanded south wing
        pygame.Rect(420, 1650, 700, 70),
        pygame.Rect(1120, 1550, 70, 350),
        pygame.Rect(1450, 1800, 650, 70),
    ]


def make_destructible_object(object_type, rectangle, maximum_health):
    """Create one bullet-damageable object that also blocks movement and sight."""
    return {
        "type": object_type,
        "rect": pygame.Rect(rectangle),
        "max_health": maximum_health,
        "health": maximum_health,
        "destroyed": False,
    }


def make_destructible_objects():
    """Create the laboratory's crates and reinforced destructible door."""
    return [
        make_destructible_object(
            "crate",
            (1090, 820, 110, 110),
            CRATE_MAX_HEALTH,
        ),
        make_destructible_object(
            "crate",
            (1770, 630, 150, 90),
            CRATE_MAX_HEALTH,
        ),
        make_destructible_object(
            "crate",
            (650, 760, 120, 120),
            CRATE_MAX_HEALTH,
        ),
        make_destructible_object(
            "door",
            (1250, 450, 70, 120),
            DOOR_MAX_HEALTH,
        ),
        make_destructible_object(
            "crate",
            (2310, 700, 120, 120),
            CRATE_MAX_HEALTH,
        ),
        make_destructible_object(
            "crate",
            (2500, 1570, 120, 120),
            CRATE_MAX_HEALTH,
        ),
    ]


def reset_destructible_objects(destructible_objects):
    """Restore every destructible object when a new round begins."""
    for destructible in destructible_objects:
        destructible["health"] = destructible["max_health"]
        destructible["destroyed"] = False


def get_active_obstacle_rects(walls, destructible_objects):
    """Return permanent walls plus destructible objects that still exist."""
    return walls + [
        destructible["rect"]
        for destructible in destructible_objects
        if not destructible["destroyed"]
    ]


def make_rift_state():
    """Create the round-persistent state for one randomly selected Rift."""
    rift_state = {"site_index": -1}
    reset_rift_state(rift_state)
    return rift_state


def reset_rift_state(rift_state):
    """Activate a new Rift site and clear control progress for a round."""
    site_index = random.randrange(len(RIFT_LOCATIONS))
    site = RIFT_LOCATIONS[site_index]
    rift_state.clear()
    rift_state.update(
        {
            "site_index": site_index,
            "site_name": site["name"],
            "position": pygame.Vector2(site["position"]),
            "owner": None,
            "capture_team": None,
            "capture_progress": 0.0,
            "hold_progress": {"blue": 0.0, "red": 0.0},
            "contested": False,
            "occupants": {"blue": 0, "red": 0},
            "intel_timer": 0.0,
            "intel_remaining": 0.0,
            "rift_energy_control_timer": 0.0,
            "rift_energy_capture_pending": None,
            "overclock_team": None,
            "overclock_alert_team": None,
            "overclock_alert_remaining": 0.0,
        }
    )


def update_rift_state(rift_state, actors, delta_time):
    """Advance Rift capture, control, intel pulses, and the Rift victory timer."""
    captured_this_frame = False
    occupants = {"blue": 0, "red": 0}
    for actor in actors:
        if (
            actor_can_fight(actor)
            and actor["position"].distance_to(rift_state["position"])
            <= RIFT_RADIUS
        ):
            occupants[actor["team"]] += 1

    rift_state["occupants"] = occupants
    blue_present = occupants["blue"] > 0
    red_present = occupants["red"] > 0
    rift_state["contested"] = blue_present and red_present

    occupying_team = None
    if blue_present and not red_present:
        occupying_team = "blue"
    elif red_present and not blue_present:
        occupying_team = "red"

    if rift_state["contested"]:
        pass
    elif occupying_team is None:
        rift_state["capture_progress"] = max(
            0.0,
            rift_state["capture_progress"]
            - RIFT_CAPTURE_DECAY_PER_SECOND * delta_time,
        )
        if rift_state["capture_progress"] == 0:
            rift_state["capture_team"] = None
    elif occupying_team == rift_state["owner"]:
        rift_state["capture_progress"] = max(
            0.0,
            rift_state["capture_progress"]
            - RIFT_CAPTURE_DECAY_PER_SECOND * delta_time,
        )
        if rift_state["capture_progress"] == 0:
            rift_state["capture_team"] = None
    else:
        if rift_state["capture_team"] != occupying_team:
            rift_state["capture_team"] = occupying_team
            rift_state["capture_progress"] = 0.0

        rift_state["capture_progress"] += delta_time
        if rift_state["capture_progress"] >= RIFT_CAPTURE_TIME:
            rift_state["owner"] = occupying_team
            rift_state["capture_team"] = None
            rift_state["capture_progress"] = 0.0
            rift_state["hold_progress"] = {"blue": 0.0, "red": 0.0}
            rift_state["intel_timer"] = 0.0
            rift_state["intel_remaining"] = RIFT_INTEL_DURATION
            rift_state["rift_energy_control_timer"] = 0.0
            rift_state["rift_energy_capture_pending"] = occupying_team
            captured_this_frame = True

    rift_state["overclock_alert_remaining"] = max(
        0.0, rift_state.get("overclock_alert_remaining", 0.0) - delta_time
    )

    owner = rift_state["owner"]
    if owner is None:
        rift_state["intel_remaining"] = 0.0
        rift_state["overclock_team"] = None
        for actor in actors:
            if actor.get("character_id") == RELAY["id"]:
                actor.get("ability_state", {})["rift_overclock_active"] = False
        return None

    if not captured_this_frame:
        # Owning the Rift starts the alternate-victory clock. The clock pauses
        # while both teams contest the zone or while the enemy is taking it.
        owner_challenged = (
            rift_state["contested"]
            or (occupying_team is not None and occupying_team != owner)
        )

        # Relay does not accelerate the five-second capture. His ultimate
        # accelerates the sixty-second HOLD timer after his team owns the Rift.
        # Multiple Conduits never stack; the timer is either normal or 1.5x.
        hold_multiplier = 1.0
        rift_state["overclock_team"] = None
        for actor in actors:
            if actor.get("character_id") != RELAY["id"]:
                continue
            state = actor.get("ability_state", {})
            if not state.get("rift_overclock_active", False):
                continue
            valid_overclock = (
                actor_can_fight(actor)
                and actor["team"] == owner
                and not owner_challenged
                and actor["position"].distance_to(rift_state["position"]) <= RIFT_RADIUS
            )
            if valid_overclock:
                hold_multiplier = RELAY_RIFT_OVERCLOCK_HOLD_MULTIPLIER
                rift_state["overclock_team"] = owner
            else:
                state["rift_overclock_active"] = False

        if not owner_challenged:
            rift_state["hold_progress"][owner] += delta_time * hold_multiplier

        rift_state["intel_remaining"] = max(
            0.0,
            rift_state["intel_remaining"] - delta_time,
        )
        rift_state["intel_timer"] += delta_time
        if rift_state["intel_timer"] >= RIFT_INTEL_INTERVAL:
            rift_state["intel_timer"] %= RIFT_INTEL_INTERVAL
            rift_state["intel_remaining"] = RIFT_INTEL_DURATION

    if rift_state["hold_progress"][owner] >= RIFT_HOLD_TIME_TO_WIN:
        return owner
    return None


def make_character_ability_state(character_id):
    """Create per-round ability timers for the requested playable character."""
    if character_id == MALPHAS["id"]:
        return {
            "hellstep_cooldown": 0.0,
            "hellstep_windup": 0.0,
            "hellstep_target": None,
            "silence_cooldown": 0.0,
            "silence_remaining": 0.0,
            "bloodlust_remaining": 0.0,
            "bloodlust_used": False,
        }
    if character_id == LONGSHOT["id"]:
        return {
            "resonance_cooldown": 0.0,
            "resonance_pulse_remaining": 0.0,
            "track_cooldown": 0.0,
            "track_remaining": 0.0,
            "dead_line_active": False,
            "dead_line_used": False,
            "dead_line_shots_remaining": 0,
            "dead_line_charge": 0.0,
            "dead_line_recovery": 0.0,
            "dead_line_requires_release": False,
            "dead_line_tracer_remaining": 0.0,
            "dead_line_tracer_start": None,
            "dead_line_tracer_end": None,
        }
    if character_id == VAREK["id"]:
        return {
            "oni_blade_cooldown": 0.0,
            "oni_blade_remaining": 0.0,
            "blade_attack_cooldown": 0.0,
            "blade_animation_timer": 0.0,
            "breach_cooldown": 0.0,
            "breach_effect_remaining": 0.0,
            "breach_angle": 0.0,
            "fury_remaining": 0.0,
            "fury_used": False,
        }
    if character_id == MIRI["id"]:
        return {
            "feline_lunge_cooldown": 0.0,
            "feline_lunge_remaining": 0.0,
            "claw_attack_cooldown": 0.0,
            "claw_animation_timer": 0.0,
            "field_treatment_cooldown": 0.0,
            "field_treatment_remaining": 0.0,
            "field_treatment_pending": False,
            "nine_lives_remaining": 0.0,
            "nine_lives_target": None,
            "nine_lives_start_position": None,
            "nine_lives_used": False,
        }
    if character_id == RELAY["id"]:
        return {
            "rift_boost_charge_progress": 0.0,
            "rift_boost_charged": False,
            "rift_boost_bullets_remaining": 0,
            "rift_boost_cooldown": 0.0,
            "rift_teleport_selecting": False,
            "rift_teleport_quadrant": None,
            "rift_teleport_remaining": 0.0,
            "rift_teleport_cooldown": 0.0,
            "rift_overclock_active": False,
            "rift_overclock_used": False,
        }
    if character_id == HAZE["id"]:
        return {
            "hallucination_cooldown": 0.0,
            "hallucination": None,
            "hallucination_fades": [],
            "silence_cooldown": 0.0,
            "silence_remaining": 0.0,
            "childs_play_remaining": 0.0,
            "childs_play_used": False,
            "childs_play_illusions": {},
            "spray_marks": [],
        }
    if character_id == SABLE["id"]:
        return {
            "scent_cooldown": 0.0,
            "scent_remaining": 0.0,
            "scent_targets": [],
            "track_cooldown": 0.0,
            "track_remaining": 0.0,
            "wild_hunt_remaining": 0.0,
            "wild_hunt_used": False,
            "wild_hunt_flicker_remaining": 0.0,
            "hunt_attack_cooldown": 0.0,
            "hunt_attack_animation_timer": 0.0,
        }
    if character_id == AUREL["id"]:
        return {
            "cinderbolt_cooldown": 0.0,
            "cinderbolts": [],
            "cinderbolt_explosions": [],
            "breach_cooldown": 0.0,
            "breach_effect_remaining": 0.0,
            "breach_angle": 0.0,
            "inferno_charge_remaining": 0.0,
            "inferno_after_remaining": 0.0,
            "inferno_used": False,
            "inferno_explosion_effect_remaining": 0.0,
            "fire_trail": [],
            "fire_trail_spawn_timer": 0.0,
            "fire_trail_last_position": None,
        }
    return {}


def get_playable_character(character_id):
    """Return an implemented character definition or None for a locked preview."""
    if character_id == MALPHAS["id"]:
        return MALPHAS
    if character_id == LONGSHOT["id"]:
        return LONGSHOT
    if character_id == VAREK["id"]:
        return VAREK
    if character_id == MIRI["id"]:
        return MIRI
    if character_id == RELAY["id"]:
        return RELAY
    if character_id == HAZE["id"]:
        return HAZE
    if character_id == SABLE["id"]:
        return SABLE
    if character_id == AUREL["id"]:
        return AUREL
    return None


def apply_character_to_actor(actor, character):
    """Apply a selected character's statistics and fresh per-round ability state."""
    actor["character_id"] = character["id"]
    actor["character_name"] = character["name"]
    actor["character_class"] = character["class"]
    actor["max_health"] = character.get("max_health", ACTOR_MAX_HEALTH)
    actor["move_speed"] = character.get("move_speed", PLAYER_SPEED)
    actor["sprint_multiplier"] = character.get(
        "sprint_multiplier", SPRINT_MULTIPLIER
    )
    actor["max_stamina"] = character.get("max_stamina", MAX_STAMINA)
    actor["health"] = actor["max_health"]
    actor["ability_state"] = make_character_ability_state(character["id"])
    actor["movement_sound_radius"] = 0.0
    actor["heard_position"] = None
    actor["heard_timer"] = 0.0
    actor["activity_last_position"] = pygame.Vector2(actor["position"])
    actor["movement_recent"] = 0.0
    actor["fired_recent"] = 0.0
    actor["track_sample_timer"] = 0.0
    actor["track_events"] = []
    actor["resonance_echo_remaining"] = 0.0
    actor["resonance_echo_position"] = None
    actor["damaged_recent"] = 0.0
    actor["burn_remaining"] = 0.0
    actor["burn_fraction_per_second"] = 0.0
    actor["burn_source"] = None


def make_actor(
    name,
    team,
    spawn_position,
    is_player=False,
    route=None,
    character=None,
):
    """Create one player or bot with round, combat, revival, and character state."""
    character = character or {}
    character_id = character.get("id")
    max_health = character.get("max_health", ACTOR_MAX_HEALTH)
    return {
        "name": name,
        "team": team,
        "is_player": is_player,
        "spawn_position": pygame.Vector2(spawn_position),
        "position": pygame.Vector2(spawn_position),
        "character_id": character_id,
        "character_name": character.get("name", "Recruit"),
        "character_class": character.get("class", "Soldier"),
        "max_health": max_health,
        "move_speed": character.get("move_speed", PLAYER_SPEED),
        "sprint_multiplier": character.get("sprint_multiplier", SPRINT_MULTIPLIER),
        "max_stamina": character.get("max_stamina", MAX_STAMINA),
        "health": max_health,
        "credits": STARTING_CREDITS,
        "owned_weapon_indices": list(STARTING_WEAPON_INDICES),
        "alive": True,
        "downed": False,
        "eliminated": False,
        "times_downed": 0,
        "revive_progress": 0.0,
        "revive_source": None,
        "rift_energy_revive_pending": False,
        "anchor_energy_awarded": False,
        "resurrected_this_round": False,
        "aim_angle": 0.0,
        "shot_cooldown": random.uniform(0.0, BOT_FIRE_INTERVAL),
        "last_buy_round": 0,
        "strafe_direction": random.choice((-1, 1)),
        "strafe_timer": random.uniform(0.7, 1.5),
        "route": [pygame.Vector2(point) for point in (route or [])],
        "route_index": 0,
        "navigation_path": [],
        "navigation_path_index": 0,
        "navigation_target": None,
        "ability_state": make_character_ability_state(character_id),
        "movement_sound_radius": 0.0,
        "heard_position": None,
        "heard_timer": 0.0,
        "activity_last_position": pygame.Vector2(spawn_position),
        "movement_recent": 0.0,
        "fired_recent": 0.0,
        "track_sample_timer": 0.0,
        "track_events": [],
        "resonance_echo_remaining": 0.0,
        "resonance_echo_position": None,
        "damaged_recent": 0.0,
        "burn_remaining": 0.0,
        "burn_fraction_per_second": 0.0,
        "burn_source": None,
    }


def make_match_actors():
    """Create the human player, two blue bots, and three red bots."""
    actors = [
        make_actor(
            "YOU",
            "blue",
            BLUE_SPAWNS[0],
            is_player=True,
            character=MALPHAS,
        )
    ]

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
    actor["health"] = actor["max_health"]
    actor["alive"] = True
    actor["downed"] = False
    actor["eliminated"] = False
    actor["times_downed"] = 0
    actor["revive_progress"] = 0.0
    actor["revive_source"] = None
    actor["rift_energy_revive_pending"] = False
    actor["anchor_energy_awarded"] = False
    actor["resurrected_this_round"] = False
    actor["aim_angle"] = 0.0
    actor["shot_cooldown"] = random.uniform(0.0, BOT_FIRE_INTERVAL)
    actor["route_index"] = 0
    actor["navigation_path"] = []
    actor["navigation_path_index"] = 0
    actor["navigation_target"] = None
    actor["ability_state"] = make_character_ability_state(actor["character_id"])
    actor["movement_sound_radius"] = 0.0
    actor["heard_position"] = None
    actor["heard_timer"] = 0.0
    actor["activity_last_position"] = pygame.Vector2(actor["position"])
    actor["movement_recent"] = 0.0
    actor["fired_recent"] = 0.0
    actor["track_sample_timer"] = 0.0
    actor["track_events"] = []
    actor["resonance_echo_remaining"] = 0.0
    actor["resonance_echo_position"] = None
    actor["damaged_recent"] = 0.0
    actor["burn_remaining"] = 0.0
    actor["burn_fraction_per_second"] = 0.0
    actor["burn_source"] = None


def make_weapon_state(weapon):
    """Create ammunition and timing values that belong to one carried weapon."""
    return {
        "magazine_ammo": weapon["magazine_size"],
        "reserve_ammo": weapon["starting_reserve_ammo"],
        "shot_cooldown": 0.0,
        "reloading": False,
        "reload_timer": 0.0,
        "sustained_shots": 0,
        "attack_animation_timer": 0.0,
    }


def reset_actor_loadout(actor):
    """Return an actor to the free Knife + Pistol starting loadout."""
    actor["owned_weapon_indices"] = list(STARTING_WEAPON_INDICES)


def actor_owns_weapon(actor, weapon_index):
    """Return whether this actor currently owns the requested weapon slot."""
    return weapon_index in actor["owned_weapon_indices"]


def try_buy_weapon(actor, weapon_index):
    """Buy one weapon during the buy phase and return a short status message."""
    if weapon_index < 0 or weapon_index >= len(WEAPONS):
        return False, "INVALID WEAPON"

    weapon = WEAPONS[weapon_index]
    if actor_owns_weapon(actor, weapon_index):
        return False, f"{weapon['name'].upper()} ALREADY OWNED"

    if len(actor["owned_weapon_indices"]) >= MAX_OWNED_WEAPONS:
        return False, "INVENTORY FULL - MAX 3 WEAPONS"

    price = weapon.get("price", 0)
    if price <= 0:
        return False, f"{weapon['name'].upper()} IS NOT FOR SALE"

    if actor["credits"] < price:
        return False, f"NEED {price - actor['credits']} MORE CREDITS"

    actor["credits"] -= price
    actor["owned_weapon_indices"].append(weapon_index)
    actor["owned_weapon_indices"].sort()
    return True, f"BOUGHT {weapon['name'].upper()} FOR {price}"


def choose_bot_purchase(bot):
    """Choose one affordable third-slot weapon for a bot, or save this round."""
    if len(bot["owned_weapon_indices"]) >= MAX_OWNED_WEAPONS:
        return None

    affordable_weapons = [
        weapon_index
        for weapon_index in (2, 3)
        if not actor_owns_weapon(bot, weapon_index)
        and bot["credits"] >= WEAPONS[weapon_index]["price"]
    ]
    if not affordable_weapons:
        return None

    # Saving is intentional. It keeps some bots available for shared weapons
    # and creates different team economies from round to round.
    if random.random() > BOT_BUY_CHANCE:
        return None

    if 2 in affordable_weapons and 3 in affordable_weapons:
        if random.random() < BOT_RIFLE_BUY_CHANCE:
            return 2
        return 3

    return affordable_weapons[0]


def update_bot_buying(actors, round_number):
    """Let every bot make exactly one purchase decision during this Buy Phase."""
    purchase_events = []
    for actor in actors:
        if actor["is_player"]:
            continue
        if actor["last_buy_round"] == round_number:
            continue

        actor["last_buy_round"] = round_number
        weapon_index = choose_bot_purchase(actor)
        if weapon_index is None:
            continue

        purchased, _ = try_buy_weapon(actor, weapon_index)
        if purchased:
            purchase_events.append((actor, weapon_index))

    return purchase_events


def make_dropped_weapon(owner, weapon_index, weapon_state):
    """Create one team-shareable purchased weapon at an actor's position."""
    return {
        "team": owner["team"],
        "weapon_index": weapon_index,
        "position": pygame.Vector2(owner["position"]),
        "weapon_state": dict(weapon_state),
    }


def drop_player_weapon(player, weapon_index, weapon_states, dropped_weapons):
    """Drop the equipped purchased weapon so a teammate can take it."""
    if not actor_can_fight(player):
        return False, "YOU CANNOT DROP A WEAPON RIGHT NOW"

    if weapon_index in STARTING_WEAPON_INDICES:
        return False, "KNIFE AND PISTOL CANNOT BE DROPPED"

    if not actor_owns_weapon(player, weapon_index):
        return False, "YOU DO NOT OWN THAT WEAPON"

    dropped_weapons.append(
        make_dropped_weapon(
            player,
            weapon_index,
            weapon_states[weapon_index],
        )
    )
    player["owned_weapon_indices"].remove(weapon_index)

    # The dropped copy keeps its current ammunition. If this player later buys
    # another copy, that fresh purchase starts with normal full ammunition.
    weapon_states[weapon_index] = make_weapon_state(WEAPONS[weapon_index])
    return True, f"DROPPED {WEAPONS[weapon_index]['name'].upper()}"


def get_nearest_shareable_weapon(actor, dropped_weapons):
    """Return the nearest friendly dropped weapon within pickup range."""
    candidates = []
    for dropped_weapon in dropped_weapons:
        weapon_index = dropped_weapon["weapon_index"]
        if dropped_weapon["team"] != actor["team"]:
            continue
        if actor_owns_weapon(actor, weapon_index):
            continue

        distance = actor["position"].distance_to(dropped_weapon["position"])
        if distance <= WEAPON_SHARE_RANGE:
            candidates.append((distance, dropped_weapon))

    if not candidates:
        return None
    return min(candidates, key=lambda candidate: candidate[0])[1]


def try_pickup_shared_weapon(actor, dropped_weapons, weapon_states=None):
    """Give one nearby friendly dropped weapon to an actor with inventory room."""
    if not actor_can_fight(actor):
        return False, None, "YOU CANNOT PICK UP A WEAPON RIGHT NOW"

    if len(actor["owned_weapon_indices"]) >= MAX_OWNED_WEAPONS:
        return False, None, "INVENTORY FULL - MAX 3 WEAPONS"

    dropped_weapon = get_nearest_shareable_weapon(actor, dropped_weapons)
    if dropped_weapon is None:
        return False, None, "NO SHARED WEAPON NEARBY"

    weapon_index = dropped_weapon["weapon_index"]
    actor["owned_weapon_indices"].append(weapon_index)
    actor["owned_weapon_indices"].sort()

    if weapon_states is not None:
        weapon_states[weapon_index] = dict(dropped_weapon["weapon_state"])

    dropped_weapons.remove(dropped_weapon)
    return (
        True,
        weapon_index,
        f"PICKED UP {WEAPONS[weapon_index]['name'].upper()}",
    )


def update_bot_weapon_pickups(actors, dropped_weapons):
    """Let bots accept nearby shared weapons and report successful pickups."""
    pickup_events = []
    for actor in actors:
        if actor["is_player"] or not actor_can_fight(actor):
            continue
        if len(actor["owned_weapon_indices"]) >= MAX_OWNED_WEAPONS:
            continue

        picked_up, weapon_index, _ = try_pickup_shared_weapon(
            actor,
            dropped_weapons,
        )
        if picked_up:
            pickup_events.append((actor, weapon_index))

    return pickup_events


def get_bot_weapon_index(bot, target_distance):
    """Choose a bot firearm from the weapons it actually owns."""
    owned = bot["owned_weapon_indices"]
    if 3 in owned and target_distance <= 420:
        return 3
    if 2 in owned:
        return 2
    if 3 in owned:
        return 3
    return 1


def add_team_rift_energy(team_rift_energy, team, amount):
    """Add shared Rift Energy to one team without exceeding the team cap."""
    before = team_rift_energy[team]
    team_rift_energy[team] = min(
        MAX_TEAM_RIFT_ENERGY,
        before + amount,
    )
    return team_rift_energy[team] - before


def update_team_rift_energy(rift_state, actors, team_rift_energy, delta_time):
    """Award Rift Energy for revives, Anchor breaks, captures, and Rift control."""
    events = []

    # A completed revive benefits the revived actor's team.
    for actor in actors:
        if actor["rift_energy_revive_pending"]:
            gained = add_team_rift_energy(
                team_rift_energy,
                actor["team"],
                RIFT_ENERGY_REVIVE_REWARD,
            )
            actor["rift_energy_revive_pending"] = False
            if gained > 0:
                events.append((actor["team"], gained, "REVIVE"))

    # A second lethal defeat breaks that actor's Rift Anchor. Combat currently
    # has no friendly fire, so the opposing team receives the shared reward.
    for actor in actors:
        if actor["eliminated"] and not actor["anchor_energy_awarded"]:
            scoring_team = "red" if actor["team"] == "blue" else "blue"
            gained = add_team_rift_energy(
                team_rift_energy,
                scoring_team,
                RIFT_ENERGY_ANCHOR_BREAK_REWARD,
            )
            actor["anchor_energy_awarded"] = True
            if gained > 0:
                events.append((scoring_team, gained, "ANCHOR BREAK"))

    # Capturing the active Rift provides an immediate shared reward.
    capture_team = rift_state["rift_energy_capture_pending"]
    if capture_team is not None:
        gained = add_team_rift_energy(
            team_rift_energy,
            capture_team,
            RIFT_ENERGY_CAPTURE_REWARD,
        )
        rift_state["rift_energy_capture_pending"] = None
        if gained > 0:
            events.append((capture_team, gained, "RIFT CAPTURE"))

    owner = rift_state["owner"]
    if owner is None:
        rift_state["rift_energy_control_timer"] = 0.0
        return events

    enemy_team = "red" if owner == "blue" else "blue"
    owner_challenged = (
        rift_state["contested"]
        or rift_state["occupants"][enemy_team] > 0
    )
    if owner_challenged:
        return events

    # Continuous control pays in small pulses rather than every frame, keeping
    # the shared resource readable and easy to balance.
    rift_state["rift_energy_control_timer"] += delta_time
    while (
        rift_state["rift_energy_control_timer"]
        >= RIFT_ENERGY_CONTROL_INTERVAL
    ):
        rift_state["rift_energy_control_timer"] -= RIFT_ENERGY_CONTROL_INTERVAL
        gained = add_team_rift_energy(
            team_rift_energy,
            owner,
            RIFT_ENERGY_CONTROL_REWARD,
        )
        if gained > 0:
            events.append((owner, gained, "RIFT CONTROL"))
        if team_rift_energy[owner] >= MAX_TEAM_RIFT_ENERGY:
            rift_state["rift_energy_control_timer"] = 0.0
            break

    return events


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


def push_actor_safely(actor, direction, distance, obstacles):
    """Push a standing actor in small collision-safe steps so walls cannot be tunneled."""
    if not actor_can_fight(actor):
        return
    direction = pygame.Vector2(direction)
    if direction.length_squared() <= 0 or distance <= 0:
        return
    direction = direction.normalize()
    remaining = float(distance)
    max_step = 12.0
    while remaining > 0:
        step = min(max_step, remaining)
        before = pygame.Vector2(actor["position"])
        move_player(actor["position"], direction * step, obstacles)
        if actor["position"].distance_squared_to(before) < 0.01:
            break
        remaining -= step


def get_weapon_spread(weapon, movement_state):
    """Return the active weapon's spread for the current movement state."""
    if movement_state == "Running":
        return weapon["running_spread"]
    if movement_state == "Walking":
        return weapon["walking_spread"]
    return weapon["standing_spread"]


def aurel_inferno_after_active(actor):
    """Return whether Aurel is in the 15-second post-explosion Inferno state."""
    return (
        actor.get("character_id") == AUREL["id"]
        and actor.get("ability_state", {}).get("inferno_after_remaining", 0.0) > 0
    )


def aurel_inferno_charging(actor):
    """Return whether Aurel is protected and locked in the three-second windup."""
    return (
        actor.get("character_id") == AUREL["id"]
        and actor.get("ability_state", {}).get("inferno_charge_remaining", 0.0) > 0
    )


def get_weapon_damage_multiplier(actor):
    """Return character-specific multipliers that apply to ordinary weapons."""
    if aurel_inferno_after_active(actor):
        return AUREL_INFERNO_WEAPON_DAMAGE_MULTIPLIER
    return 1.0


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

    # Longshot information abilities read recent activity from every actor. A
    # shotgun creates several projectiles, so record_track_event suppresses
    # duplicate fire markers at the same position.
    shooter["fired_recent"] = max(
        shooter.get("fired_recent", 0.0),
        LONGSHOT_FIRE_ACTIVITY_MEMORY,
    )
    record_track_event(shooter, "fire")

    bullet_damage = weapon["damage"] if damage_override is None else damage_override
    bullet_damage *= get_weapon_damage_multiplier(shooter)
    rift_boosted = False
    if shooter.get("character_id") == RELAY["id"]:
        relay_state = shooter.get("ability_state", {})
        boosted_remaining = relay_state.get("rift_boost_bullets_remaining", 0)
        if boosted_remaining > 0:
            bullet_damage *= RELAY_RIFT_BOOST_DAMAGE_MULTIPLIER
            relay_state["rift_boost_bullets_remaining"] = boosted_remaining - 1
            if relay_state["rift_boost_bullets_remaining"] <= 0:
                relay_state["rift_boost_cooldown"] = RELAY_RIFT_BOOST_COOLDOWN
            rift_boosted = True

    return {
        "position": pygame.Vector2(shooter["position"]) + direction * muzzle_distance,
        "velocity": direction * weapon["bullet_speed"],
        "damage": bullet_damage,
        "rift_boosted": rift_boosted,
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


def get_bullet_hit_destructible(bullet, destructible_objects):
    """Return the active destructible object struck by a bullet, if any."""
    radius = bullet["radius"]
    bullet_rect = pygame.Rect(0, 0, radius * 2, radius * 2)
    bullet_rect.center = (
        round(bullet["position"].x),
        round(bullet["position"].y),
    )

    for destructible in destructible_objects:
        if (
            not destructible["destroyed"]
            and bullet_rect.colliderect(destructible["rect"])
        ):
            return destructible

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
    actor["movement_sound_radius"] = 0.0

    # Active character powers stop when the character is downed. Cooldowns and
    # once-per-round ultimate flags remain, so being downed is not a free reset.
    ability_state = actor.get("ability_state", {})
    if "hellstep_windup" in ability_state:
        ability_state["hellstep_windup"] = 0.0
        ability_state["hellstep_target"] = None
        ability_state["silence_remaining"] = 0.0
        ability_state["bloodlust_remaining"] = 0.0
    if "dead_line_active" in ability_state:
        ability_state["resonance_pulse_remaining"] = 0.0
        ability_state["track_remaining"] = 0.0
        ability_state["dead_line_active"] = False
        ability_state["dead_line_charge"] = 0.0
        ability_state["dead_line_recovery"] = 0.0
        ability_state["dead_line_requires_release"] = False
    if "oni_blade_remaining" in ability_state:
        ability_state["oni_blade_remaining"] = 0.0
        ability_state["blade_attack_cooldown"] = 0.0
        ability_state["blade_animation_timer"] = 0.0
        ability_state["breach_effect_remaining"] = 0.0
        ability_state["fury_remaining"] = 0.0
    if "feline_lunge_remaining" in ability_state:
        ability_state["feline_lunge_remaining"] = 0.0
        ability_state["claw_attack_cooldown"] = 0.0
        ability_state["claw_animation_timer"] = 0.0
        ability_state["field_treatment_remaining"] = 0.0
        ability_state["field_treatment_pending"] = False
        ability_state["nine_lives_remaining"] = 0.0
        ability_state["nine_lives_target"] = None
        ability_state["nine_lives_start_position"] = None
    if "rift_boost_charge_progress" in ability_state:
        ability_state["rift_boost_charge_progress"] = 0.0
        ability_state["rift_teleport_selecting"] = False
        ability_state["rift_teleport_quadrant"] = None
        ability_state["rift_teleport_remaining"] = 0.0
        ability_state["rift_overclock_active"] = False
    if "hallucination_cooldown" in ability_state:
        ability_state["silence_remaining"] = 0.0
        ability_state["hallucination"] = None
        ability_state["hallucination_fades"] = []
        ability_state["childs_play_remaining"] = 0.0
        ability_state["childs_play_illusions"] = {}
    if "scent_cooldown" in ability_state:
        ability_state["scent_remaining"] = 0.0
        ability_state["scent_targets"] = []
        ability_state["track_remaining"] = 0.0
        ability_state["wild_hunt_remaining"] = 0.0
        ability_state["wild_hunt_flicker_remaining"] = 0.0
        ability_state["hunt_attack_cooldown"] = 0.0
        ability_state["hunt_attack_animation_timer"] = 0.0
    if "cinderbolt_cooldown" in ability_state:
        ability_state["cinderbolts"] = []
        ability_state["cinderbolt_explosions"] = []
        ability_state["breach_effect_remaining"] = 0.0
        ability_state["inferno_charge_remaining"] = 0.0
        ability_state["inferno_after_remaining"] = 0.0
        ability_state["inferno_explosion_effect_remaining"] = 0.0
        ability_state["fire_trail"] = []
        ability_state["fire_trail_spawn_timer"] = 0.0
        ability_state["fire_trail_last_position"] = None

    actor["burn_remaining"] = 0.0
    actor["burn_fraction_per_second"] = 0.0
    actor["burn_source"] = None

    if actor["times_downed"] >= 2:
        actor["downed"] = False
        actor["eliminated"] = True
    else:
        actor["downed"] = True
        actor["eliminated"] = False


def revive_actor(actor):
    """Return a first-time downed actor with partial health."""
    actor["health"] = min(REVIVE_HEALTH, actor["max_health"])
    actor["alive"] = True
    actor["downed"] = False
    actor["revive_progress"] = 0.0
    actor["revive_source"] = None
    actor["rift_energy_revive_pending"] = True


def malphas_bloodlust_active(actor):
    """Return whether this actor is Malphas with Bloodlust currently active."""
    return (
        actor.get("character_id") == MALPHAS["id"]
        and actor.get("ability_state", {}).get("bloodlust_remaining", 0.0) > 0
    )


def varek_unbound_fury_active(actor):
    """Return whether Varek currently has Unbound Fury active."""
    return (
        actor.get("character_id") == VAREK["id"]
        and actor.get("ability_state", {}).get("fury_remaining", 0.0) > 0
    )


def varek_blade_active(actor):
    """Return whether Varek is currently forced into the Rift-forged katana."""
    if actor.get("character_id") != VAREK["id"]:
        return False
    state = actor.get("ability_state", {})
    return state.get("oni_blade_remaining", 0.0) > 0 or state.get("fury_remaining", 0.0) > 0


def sable_wild_hunt_active(actor):
    """Return whether Sable is currently camouflaged in Wild Hunt."""
    return (
        actor.get("character_id") == SABLE["id"]
        and actor.get("ability_state", {}).get("wild_hunt_remaining", 0.0) > 0
    )


def damage_actor(target, damage, attacker=None):
    """Damage an actor and apply character-specific on-hit/elimination effects."""
    if not target["alive"] or target["downed"] or target["eliminated"]:
        return 0.0, False
    if aurel_inferno_charging(target):
        return 0.0, False

    damage = max(0.0, float(damage))
    damage_done = min(float(target["health"]), damage)
    target["health"] = max(0.0, float(target["health"]) - damage_done)
    if damage_done > 0:
        target["damaged_recent"] = max(
            target.get("damaged_recent", 0.0),
            SABLE_DAMAGE_EVIDENCE_MEMORY,
        )
        if sable_wild_hunt_active(target):
            target["ability_state"]["wild_hunt_flicker_remaining"] = max(
                target["ability_state"].get("wild_hunt_flicker_remaining", 0.0),
                SABLE_WILD_HUNT_REVEAL_ON_HIT,
            )
    eliminated_before = target["eliminated"]

    if target["health"] <= 0:
        down_or_eliminate_actor(target)

    eliminated_now = target["eliminated"] and not eliminated_before

    if (
        attacker is not None
        and attacker is not target
        and attacker.get("alive", False)
        and malphas_bloodlust_active(attacker)
        and damage_done > 0
    ):
        attacker["health"] = min(
            attacker["max_health"],
            attacker["health"]
            + damage_done * MALPHAS_BLOODLUST_HEAL_FRACTION,
        )

        if eliminated_now:
            minimum_health = (
                attacker["max_health"]
                * MALPHAS_BLOODLUST_ELIMINATION_HEALTH_FRACTION
            )
            attacker["health"] = max(attacker["health"], minimum_health)

    if (
        eliminated_now
        and attacker is not None
        and attacker is not target
        and attacker.get("alive", False)
        and varek_unbound_fury_active(attacker)
    ):
        attacker_state = attacker["ability_state"]
        attacker_state["fury_remaining"] = min(
            VAREK_FURY_MAX_REMAINING,
            attacker_state["fury_remaining"] + VAREK_FURY_EXTENSION_PER_ELIMINATION,
        )

    return damage_done, eliminated_now


def apply_burn(target, duration, max_health_fraction_per_second, source=None):
    """Apply one burn; equal burns refresh, stronger burns replace, burns never stack."""
    if not actor_can_fight(target):
        return False

    duration = float(duration)
    new_fraction = float(max_health_fraction_per_second)
    current_fraction = target.get("burn_fraction_per_second", 0.0)
    current_remaining = target.get("burn_remaining", 0.0)

    if current_remaining <= 0 or new_fraction > current_fraction:
        target["burn_remaining"] = duration
        target["burn_fraction_per_second"] = new_fraction
        target["burn_source"] = source
    elif abs(new_fraction - current_fraction) <= 0.000001:
        target["burn_remaining"] = max(duration, current_remaining)
        target["burn_source"] = source
    # A weaker fire source cannot extend a stronger active burn. If the weaker
    # source is still present after the stronger burn expires, it can apply then.
    return True


def update_burn_effects(actors, delta_time):
    """Tick active burns. Repeated fire refreshes the burn instead of stacking it."""
    for actor in actors:
        remaining = actor.get("burn_remaining", 0.0)
        if remaining <= 0:
            continue
        if not actor_can_fight(actor):
            actor["burn_remaining"] = 0.0
            actor["burn_fraction_per_second"] = 0.0
            actor["burn_source"] = None
            continue

        tick_time = min(delta_time, remaining)
        fraction_per_second = actor.get("burn_fraction_per_second", 0.0)
        source = actor.get("burn_source")
        damage_actor(
            actor,
            actor["max_health"] * fraction_per_second * tick_time,
            source,
        )
        if not actor_can_fight(actor):
            actor["burn_remaining"] = 0.0
            actor["burn_fraction_per_second"] = 0.0
            actor["burn_source"] = None
            continue
        actor["burn_remaining"] = max(0.0, remaining - delta_time)
        if actor["burn_remaining"] <= 0:
            actor["burn_fraction_per_second"] = 0.0
            actor["burn_source"] = None


def actor_position_is_clear(position, obstacles):
    """Return whether a character-sized body can safely occupy this world point."""
    radius = PLAYER_SIZE / 2
    if not (
        radius <= position.x <= WORLD_WIDTH - radius
        and radius <= position.y <= WORLD_HEIGHT - radius
    ):
        return False

    body = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)
    body.center = (round(position.x), round(position.y))
    return not any(body.colliderect(obstacle) for obstacle in obstacles)


def try_activate_hellstep(player, target_position, obstacles):
    """Mark a visible, clear point and begin Malphas's delayed teleport."""
    if player.get("character_id") != MALPHAS["id"]:
        return False, "HELLSTEP UNAVAILABLE"

    state = player["ability_state"]
    if state["hellstep_windup"] > 0:
        return False, "HELLSTEP ALREADY CHARGING"
    if state["hellstep_cooldown"] > 0:
        return False, f"HELLSTEP COOLDOWN {state['hellstep_cooldown']:.1f}s"

    target = pygame.Vector2(target_position)
    distance = player["position"].distance_to(target)
    if distance > MALPHAS_HELLSTEP_RANGE:
        return False, "HELLSTEP TARGET TOO FAR"
    if not has_line_of_sight(player["position"], target, obstacles):
        return False, "HELLSTEP NEEDS LINE OF SIGHT"
    if not actor_position_is_clear(target, obstacles):
        return False, "HELLSTEP TARGET BLOCKED"

    state["hellstep_target"] = target
    state["hellstep_windup"] = MALPHAS_HELLSTEP_DELAY
    state["hellstep_cooldown"] = MALPHAS_HELLSTEP_COOLDOWN
    return True, "HELLSTEP MARKED"


def try_activate_silence(player):
    """Activate the shared Phantom class ability that suppresses movement sound."""
    if player.get("character_class") != "Phantom":
        return False, "SILENCE UNAVAILABLE"

    state = player["ability_state"]
    if "silence_remaining" not in state:
        return False, "SILENCE UNAVAILABLE"
    if state["silence_remaining"] > 0:
        return False, "SILENCE ALREADY ACTIVE"
    if state["silence_cooldown"] > 0:
        return False, f"SILENCE COOLDOWN {state['silence_cooldown']:.1f}s"

    state["silence_remaining"] = MALPHAS_SILENCE_DURATION
    state["silence_cooldown"] = MALPHAS_SILENCE_COOLDOWN
    if player.get("character_id") == HAZE["id"]:
        add_haze_spray_mark(player)
    return True, "SILENCE ACTIVE"


def try_activate_bloodlust(player):
    """Activate Malphas's once-per-round Bloodlust ultimate."""
    if player.get("character_id") != MALPHAS["id"]:
        return False, "BLOODLUST UNAVAILABLE"

    state = player["ability_state"]
    if state["bloodlust_remaining"] > 0:
        return False, "BLOODLUST ALREADY ACTIVE"
    if state["bloodlust_used"]:
        return False, "BLOODLUST USED THIS ROUND"

    state["bloodlust_remaining"] = MALPHAS_BLOODLUST_DURATION
    state["bloodlust_used"] = True
    return True, "BLOODLUST ACTIVE"


def update_malphas_abilities(player, actors, obstacles, delta_time):
    """Advance Malphas cooldowns, teleport windup, Silence, and Bloodlust drain."""
    if player.get("character_id") != MALPHAS["id"]:
        return False

    state = player["ability_state"]
    state["hellstep_cooldown"] = max(
        0.0, state["hellstep_cooldown"] - delta_time
    )
    state["silence_cooldown"] = max(
        0.0, state["silence_cooldown"] - delta_time
    )
    state["silence_remaining"] = max(
        0.0, state["silence_remaining"] - delta_time
    )
    state["bloodlust_remaining"] = max(
        0.0, state["bloodlust_remaining"] - delta_time
    )

    teleported = False
    if state["hellstep_windup"] > 0:
        state["hellstep_windup"] = max(
            0.0, state["hellstep_windup"] - delta_time
        )
        if state["hellstep_windup"] == 0 and state["hellstep_target"] is not None:
            target = pygame.Vector2(state["hellstep_target"])
            if actor_position_is_clear(target, obstacles):
                player["position"].update(target)
                teleported = True
            state["hellstep_target"] = None

    if state["bloodlust_remaining"] > 0 and actor_can_fight(player):
        for actor in actors:
            if actor is player or actor["team"] == player["team"]:
                continue
            if not actor_can_fight(actor):
                continue
            if (
                player["position"].distance_to(actor["position"])
                > MALPHAS_BLOODLUST_RADIUS
            ):
                continue
            if not has_line_of_sight(
                player["position"], actor["position"], obstacles
            ):
                continue

            damage_actor(
                actor,
                MALPHAS_BLOODLUST_DRAIN_PER_SECOND * delta_time,
                player,
            )

    return teleported


def add_haze_spray_mark(player):
    """Leave a temporary neon graffiti marker where Haze activated an ability."""
    if player.get("character_id") != HAZE["id"]:
        return
    state = player.get("ability_state", {})
    marks = state.setdefault("spray_marks", [])
    marks.append(
        {
            "position": pygame.Vector2(player["position"]),
            "remaining": HAZE_SPRAY_MARK_DURATION,
            "rotation": random.uniform(0.0, math.tau),
        }
    )
    if len(marks) > 10:
        del marks[:-10]


def haze_hallucination_active(actor):
    """Return whether Haze currently owns a shootable Q duplicate."""
    if actor.get("character_id") != HAZE["id"]:
        return False
    decoy = actor.get("ability_state", {}).get("hallucination")
    return (
        decoy is not None
        and decoy.get("remaining", 0.0) > 0
        and decoy.get("health", 0.0) > 0
    )


def finish_haze_hallucination(player):
    """Turn Haze's active Q duplicate into a short visual fade."""
    state = player.get("ability_state", {})
    decoy = state.get("hallucination")
    if decoy is None:
        return
    faded = dict(decoy)
    faded["position"] = pygame.Vector2(decoy["position"])
    faded["fade_remaining"] = HAZE_HALLUCINATION_FADE_TIME
    state.setdefault("hallucination_fades", []).append(faded)
    state["hallucination_fades"] = state["hallucination_fades"][-3:]
    state["hallucination"] = None


def try_activate_hallucination(player):
    """Create Haze's forward-walking duplicate at his current position."""
    if player.get("character_id") != HAZE["id"]:
        return False, "HALLUCINATION UNAVAILABLE"

    state = player["ability_state"]
    if state["hallucination_cooldown"] > 0:
        return False, f"HALLUCINATION COOLDOWN {state['hallucination_cooldown']:.1f}s"

    if state.get("hallucination") is not None:
        finish_haze_hallucination(player)

    state["hallucination"] = {
        "position": pygame.Vector2(player["position"]),
        "health": float(player["max_health"]),
        "max_health": float(player["max_health"]),
        "remaining": HAZE_HALLUCINATION_DURATION,
        "aim_angle": float(player.get("aim_angle", 0.0)),
        "stopped": False,
    }
    state["hallucination_cooldown"] = HAZE_HALLUCINATION_COOLDOWN
    add_haze_spray_mark(player)
    return True, "HALLUCINATION DEPLOYED"


def damage_haze_hallucination(player, damage):
    """Damage Haze's Q duplicate without creating a down/elimination event."""
    if not haze_hallucination_active(player):
        return False
    state = player["ability_state"]
    decoy = state["hallucination"]
    decoy["health"] = max(0.0, decoy["health"] - max(0.0, float(damage)))
    if decoy["health"] <= 0:
        finish_haze_hallucination(player)
    return True


def get_haze_hallucination_targets(team, actors):
    """Return shootable enemy Q duplicates as lightweight actor-like targets."""
    targets = []
    for actor in actors:
        if actor.get("team") == team or not haze_hallucination_active(actor):
            continue
        decoy = actor["ability_state"]["hallucination"]
        targets.append(
            {
                "position": decoy["position"],
                "team": actor["team"],
                "alive": True,
                "downed": False,
                "eliminated": False,
                "is_haze_hallucination": True,
                "haze_owner": actor,
            }
        )
    return targets


def make_haze_childs_play_illusion(victim, source_actor, obstacles):
    """Create one false living-team target near cover around an affected enemy."""
    victim_position = victim["position"]
    nearby_cover = []
    for obstacle in obstacles:
        cover_center = pygame.Vector2(obstacle.center)
        distance = victim_position.distance_to(cover_center)
        if 120 <= distance <= 650:
            nearby_cover.append(obstacle)

    random.shuffle(nearby_cover)
    for obstacle in nearby_cover[:20]:
        cover_center = pygame.Vector2(obstacle.center)
        away = cover_center - victim_position
        if away.length_squared() == 0:
            continue
        away = away.normalize()
        side = pygame.Vector2(-away.y, away.x)
        half_extent = max(obstacle.width, obstacle.height) * 0.55
        for jitter in (0.0, 32.0, -32.0, 62.0, -62.0):
            candidate = (
                cover_center
                + away * (half_extent + ACTOR_RADIUS + 18)
                + side * jitter
            )
            if actor_position_is_clear(candidate, obstacles):
                move_direction = side * random.choice((-1, 1))
                return {
                    "position": candidate,
                    "anchor": pygame.Vector2(candidate),
                    "move_direction": move_direction,
                    "source_name": source_actor["name"],
                    "source_character_id": source_actor.get("character_id"),
                    "source_character_name": source_actor.get("character_name", source_actor["name"]),
                    "source_character_class": source_actor.get("character_class", "Soldier"),
                    "source_max_health": source_actor.get("max_health", ACTOR_MAX_HEALTH),
                    "source_health": source_actor.get("health", ACTOR_MAX_HEALTH),
                    "aim_angle": math.atan2(
                        victim_position.y - candidate.y,
                        victim_position.x - candidate.x,
                    ),
                    "motion_timer": random.uniform(0.8, 1.6),
                }

    for _ in range(80):
        angle = random.uniform(0.0, math.tau)
        distance = random.uniform(220.0, 520.0)
        candidate = victim_position + pygame.Vector2(
            math.cos(angle), math.sin(angle)
        ) * distance
        if not actor_position_is_clear(candidate, obstacles):
            continue
        move_direction = pygame.Vector2(-math.sin(angle), math.cos(angle))
        return {
            "position": candidate,
            "anchor": pygame.Vector2(candidate),
            "move_direction": move_direction * random.choice((-1, 1)),
            "source_name": source_actor["name"],
            "source_character_id": source_actor.get("character_id"),
            "source_character_name": source_actor.get("character_name", source_actor["name"]),
            "source_character_class": source_actor.get("character_class", "Soldier"),
            "source_max_health": source_actor.get("max_health", ACTOR_MAX_HEALTH),
            "source_health": source_actor.get("health", ACTOR_MAX_HEALTH),
            "aim_angle": math.atan2(
                victim_position.y - candidate.y,
                victim_position.x - candidate.x,
            ),
            "motion_timer": random.uniform(0.8, 1.6),
        }
    return None


def update_haze_child_illusion(illusion, victim, obstacles, delta_time):
    """Make one Child's Play illusion strafe and peek around its nearby cover."""
    illusion["motion_timer"] -= delta_time
    if illusion["motion_timer"] <= 0:
        illusion["move_direction"] *= -1
        illusion["motion_timer"] = random.uniform(0.8, 1.6)

    move_direction = illusion["move_direction"]
    if move_direction.length_squared() > 0:
        movement = move_direction.normalize() * HAZE_CHILD_ILLUSION_MOVE_SPEED * delta_time
        candidate = pygame.Vector2(illusion["position"]) + movement
        if (
            candidate.distance_to(illusion["anchor"]) <= 80
            and actor_position_is_clear(candidate, obstacles)
        ):
            illusion["position"].update(candidate)
        else:
            illusion["move_direction"] *= -1

    aim_vector = victim["position"] - illusion["position"]
    if aim_vector.length_squared() > 0:
        illusion["aim_angle"] = math.atan2(aim_vector.y, aim_vector.x)


def sync_haze_childs_play_illusions(player, actors, obstacles, delta_time):
    """Keep three false targets per living enemy, copied only from living allies."""
    state = player["ability_state"]
    illusion_sets = state.setdefault("childs_play_illusions", {})
    living_sources = [
        actor
        for actor in actors
        if actor["team"] == player["team"] and actor_can_fight(actor)
    ]
    living_names = {actor["name"] for actor in living_sources}
    victims = [
        actor
        for actor in actors
        if actor["team"] != player["team"] and actor_can_fight(actor)
    ]
    victim_names = {actor["name"] for actor in victims}

    for victim_name in list(illusion_sets):
        if victim_name not in victim_names:
            del illusion_sets[victim_name]

    if not living_sources:
        illusion_sets.clear()
        return

    source_by_name = {actor["name"]: actor for actor in living_sources}
    for victim in victims:
        current = [
            illusion
            for illusion in illusion_sets.get(victim["name"], [])
            if illusion.get("source_name") in living_names
        ]

        while len(current) < HAZE_CHILDS_PLAY_ILLUSIONS_PER_ENEMY:
            source = random.choice(living_sources)
            illusion = make_haze_childs_play_illusion(victim, source, obstacles)
            if illusion is None:
                break
            current.append(illusion)

        current = current[:HAZE_CHILDS_PLAY_ILLUSIONS_PER_ENEMY]
        for illusion in current:
            source = source_by_name.get(illusion.get("source_name"))
            if source is not None:
                illusion["source_health"] = source.get("health", illusion["source_health"])
                illusion["source_max_health"] = source.get("max_health", illusion["source_max_health"])
            update_haze_child_illusion(illusion, victim, obstacles, delta_time)
        illusion_sets[victim["name"]] = current


def try_activate_childs_play(player, actors, obstacles):
    """Distort every living enemy's perception with false living-team copies."""
    if player.get("character_id") != HAZE["id"]:
        return False, "CHILD'S PLAY UNAVAILABLE"

    state = player["ability_state"]
    if state["childs_play_remaining"] > 0:
        return False, "CHILD'S PLAY ALREADY ACTIVE"
    if state["childs_play_used"]:
        return False, "CHILD'S PLAY USED THIS ROUND"

    state["childs_play_remaining"] = HAZE_CHILDS_PLAY_DURATION
    state["childs_play_used"] = True
    state["childs_play_illusions"] = {}
    sync_haze_childs_play_illusions(player, actors, obstacles, 0.0)
    add_haze_spray_mark(player)
    return True, "CHILD'S PLAY ACTIVE"


def update_haze_abilities(player, actors, obstacles, delta_time):
    """Advance Haze's Q, shared Silence timers, graffiti, and ultimate illusions."""
    if player.get("character_id") != HAZE["id"]:
        return

    state = player["ability_state"]
    state["hallucination_cooldown"] = max(
        0.0, state["hallucination_cooldown"] - delta_time
    )
    state["silence_cooldown"] = max(0.0, state["silence_cooldown"] - delta_time)
    state["silence_remaining"] = max(0.0, state["silence_remaining"] - delta_time)

    for mark in state.get("spray_marks", []):
        mark["remaining"] -= delta_time
    state["spray_marks"] = [
        mark for mark in state.get("spray_marks", []) if mark["remaining"] > 0
    ]

    for faded in state.get("hallucination_fades", []):
        faded["fade_remaining"] -= delta_time
    state["hallucination_fades"] = [
        faded
        for faded in state.get("hallucination_fades", [])
        if faded["fade_remaining"] > 0
    ]

    decoy = state.get("hallucination")
    if decoy is not None:
        decoy["remaining"] = max(0.0, decoy["remaining"] - delta_time)
        if decoy["remaining"] <= 0 or decoy["health"] <= 0:
            finish_haze_hallucination(player)
        elif not decoy["stopped"]:
            direction = pygame.Vector2(
                math.cos(decoy["aim_angle"]), math.sin(decoy["aim_angle"])
            )
            total_movement = direction * HAZE_HALLUCINATION_SPEED * delta_time
            step_count = max(1, math.ceil(total_movement.length() / 8.0))
            step = total_movement / step_count
            for _ in range(step_count):
                candidate = pygame.Vector2(decoy["position"]) + step
                if not actor_position_is_clear(candidate, obstacles):
                    decoy["stopped"] = True
                    break
                decoy["position"].update(candidate)

    if state["childs_play_remaining"] > 0:
        state["childs_play_remaining"] = max(
            0.0, state["childs_play_remaining"] - delta_time
        )
        if state["childs_play_remaining"] <= 0:
            state["childs_play_illusions"] = {}
        else:
            sync_haze_childs_play_illusions(player, actors, obstacles, delta_time)


def get_haze_false_targets_for_bot(bot, actors, walls):
    """Return Haze Q/X targets that this enemy bot currently believes are real."""
    targets = []
    for target in get_haze_hallucination_targets(bot["team"], actors):
        if is_actor_visible(bot["position"], target, walls):
            targets.append(target)

    for haze_actor in actors:
        if haze_actor.get("character_id") != HAZE["id"] or haze_actor["team"] == bot["team"]:
            continue
        state = haze_actor.get("ability_state", {})
        if state.get("childs_play_remaining", 0.0) <= 0:
            continue
        for illusion in state.get("childs_play_illusions", {}).get(bot["name"], []):
            proxy = {
                "position": illusion["position"],
                "team": haze_actor["team"],
                "alive": True,
                "downed": False,
                "eliminated": False,
                "is_haze_child_illusion": True,
                "haze_owner": haze_actor,
            }
            if is_actor_visible(bot["position"], proxy, walls):
                targets.append(proxy)
    return targets


def update_player_movement_sound(player, movement_state):
    """Expose Phantom movement noise, while Wild Hunt remains fully silent."""
    if sable_wild_hunt_active(player):
        player["movement_sound_radius"] = 0.0
        return
    if player.get("character_class") != "Phantom":
        player["movement_sound_radius"] = 0.0
        return

    state = player["ability_state"]
    if state.get("silence_remaining", 0.0) > 0:
        player["movement_sound_radius"] = 0.0
    elif movement_state == "Running":
        player["movement_sound_radius"] = MALPHAS_RUN_SOUND_RADIUS
    elif movement_state == "Walking":
        player["movement_sound_radius"] = MALPHAS_WALK_SOUND_RADIUS
    else:
        player["movement_sound_radius"] = 0.0


def record_track_event(actor, kind):
    """Store one recent movement or interaction marker for Longshot's Track."""
    events = actor.setdefault("track_events", [])
    position = pygame.Vector2(actor["position"])
    if events:
        newest = events[-1]
        if (
            newest["kind"] == kind
            and position.distance_squared_to(newest["position"]) < 14 * 14
            and newest["remaining"] > LONGSHOT_TRACK_EVENT_LIFETIME - 0.18
        ):
            return

    events.append(
        {
            "position": position,
            "kind": kind,
            "remaining": LONGSHOT_TRACK_EVENT_LIFETIME,
        }
    )
    if len(events) > LONGSHOT_TRACK_MAX_EVENTS_PER_ACTOR:
        del events[: len(events) - LONGSHOT_TRACK_MAX_EVENTS_PER_ACTOR]


def update_actor_activity_tracking(actors, delta_time):
    """Maintain short activity memory and recent trail points for Hunter abilities."""
    for actor in actors:
        actor["movement_recent"] = max(
            0.0, actor.get("movement_recent", 0.0) - delta_time
        )
        actor["fired_recent"] = max(
            0.0, actor.get("fired_recent", 0.0) - delta_time
        )
        actor["damaged_recent"] = max(
            0.0, actor.get("damaged_recent", 0.0) - delta_time
        )
        actor["resonance_echo_remaining"] = max(
            0.0, actor.get("resonance_echo_remaining", 0.0) - delta_time
        )
        actor["track_sample_timer"] = max(
            0.0, actor.get("track_sample_timer", 0.0) - delta_time
        )

        events = actor.setdefault("track_events", [])
        for event in events:
            event["remaining"] -= delta_time
        events[:] = [event for event in events if event["remaining"] > 0]

        previous = actor.get("activity_last_position")
        if previous is None:
            previous = pygame.Vector2(actor["position"])
        moved_distance_sq = actor["position"].distance_squared_to(previous)
        if actor_can_fight(actor) and moved_distance_sq >= 1.0:
            actor["movement_recent"] = LONGSHOT_MOVE_ACTIVITY_MEMORY
            if actor["track_sample_timer"] <= 0:
                record_track_event(actor, "step")
                actor["track_sample_timer"] = LONGSHOT_TRACK_SAMPLE_INTERVAL

        actor["activity_last_position"] = pygame.Vector2(actor["position"])


def try_activate_resonance_sweep(player, actors):
    """Reveal snapshots of moving or firing enemies inside Longshot's scan radius."""
    if player.get("character_id") != LONGSHOT["id"]:
        return False, "RESONANCE SWEEP UNAVAILABLE"

    state = player["ability_state"]
    if state["resonance_cooldown"] > 0:
        return False, f"RESONANCE COOLDOWN {state['resonance_cooldown']:.1f}s"

    echoes = 0
    for actor in actors:
        if actor is player or actor["team"] == player["team"]:
            continue
        if not actor_can_fight(actor):
            continue
        if player["position"].distance_to(actor["position"]) > LONGSHOT_RESONANCE_RADIUS:
            continue
        if actor.get("movement_recent", 0.0) <= 0 and actor.get("fired_recent", 0.0) <= 0:
            continue
        actor["resonance_echo_position"] = pygame.Vector2(actor["position"])
        actor["resonance_echo_remaining"] = LONGSHOT_RESONANCE_ECHO_DURATION
        echoes += 1

    state["resonance_cooldown"] = LONGSHOT_RESONANCE_COOLDOWN
    state["resonance_pulse_remaining"] = LONGSHOT_RESONANCE_PULSE_DURATION
    return True, f"RESONANCE SWEEP - {echoes} ECHO{'ES' if echoes != 1 else ''}"


def try_activate_track(player):
    """Activate the shared Hunter class ability that exposes recent enemy trails."""
    if player.get("character_class") != "Hunter":
        return False, "TRACK UNAVAILABLE"

    state = player["ability_state"]
    if "track_remaining" not in state:
        return False, "TRACK UNAVAILABLE"
    if state["track_remaining"] > 0:
        return False, "TRACK ALREADY ACTIVE"
    if state["track_cooldown"] > 0:
        return False, f"TRACK COOLDOWN {state['track_cooldown']:.1f}s"

    state["track_remaining"] = LONGSHOT_TRACK_DURATION
    state["track_cooldown"] = LONGSHOT_TRACK_COOLDOWN
    return True, "TRACK ACTIVE"


def try_activate_dead_line(player):
    """Enter Longshot's two-shot supernatural sniper ultimate mode."""
    if player.get("character_id") != LONGSHOT["id"]:
        return False, "DEAD LINE UNAVAILABLE"

    state = player["ability_state"]
    if state["dead_line_active"]:
        return False, "DEAD LINE ALREADY ACTIVE"
    if state["dead_line_used"]:
        return False, "DEAD LINE USED THIS ROUND"

    state["dead_line_active"] = True
    state["dead_line_used"] = True
    state["dead_line_shots_remaining"] = LONGSHOT_DEAD_LINE_SHOTS
    state["dead_line_charge"] = 0.0
    state["dead_line_recovery"] = 0.0
    state["dead_line_requires_release"] = True
    return True, "DEAD LINE - RELEASE FIRE, THEN HOLD TO AIM"


def longshot_dead_line_active(actor):
    """Return whether Longshot is currently wielding Dead Line."""
    return (
        actor.get("character_id") == LONGSHOT["id"]
        and actor.get("ability_state", {}).get("dead_line_active", False)
    )


def ray_rect_hit_distance(origin, direction, rectangle, max_distance):
    """Return the entry distance where a ray first crosses an axis-aligned rectangle."""
    t_min = 0.0
    t_max = max_distance
    for origin_value, direction_value, minimum, maximum in (
        (origin.x, direction.x, rectangle.left, rectangle.right),
        (origin.y, direction.y, rectangle.top, rectangle.bottom),
    ):
        if abs(direction_value) < 0.000001:
            if origin_value < minimum or origin_value > maximum:
                return None
            continue
        first = (minimum - origin_value) / direction_value
        second = (maximum - origin_value) / direction_value
        if first > second:
            first, second = second, first
        t_min = max(t_min, first)
        t_max = min(t_max, second)
        if t_min > t_max:
            return None
    if t_max < 0 or t_min > max_distance:
        return None
    return max(0.0, t_min)


def ray_actor_hit_distance(origin, direction, actor, max_distance):
    """Return the first ray distance that enters an actor's circular hit body."""
    to_center = actor["position"] - origin
    projection = to_center.dot(direction)
    if projection < 0 or projection > max_distance:
        return None
    perpendicular_sq = to_center.length_squared() - projection * projection
    radius_sq = ACTOR_RADIUS * ACTOR_RADIUS
    if perpendicular_sq > radius_sq:
        return None
    half_chord = math.sqrt(max(0.0, radius_sq - perpendicular_sq))
    return max(0.0, projection - half_chord)


def fire_dead_line_shot(player, aim_angle, walls, destructible_objects, actors):
    """Fire Dead Line as hitscan, penetrating at most one thin solid obstacle."""
    origin = pygame.Vector2(player["position"])
    direction = pygame.Vector2(math.cos(aim_angle), math.sin(aim_angle))
    candidates = []

    for wall in walls:
        distance = ray_rect_hit_distance(
            origin, direction, wall, LONGSHOT_DEAD_LINE_RANGE
        )
        if distance is not None:
            candidates.append((distance, "wall", wall))

    for destructible in destructible_objects:
        if destructible["destroyed"]:
            continue
        distance = ray_rect_hit_distance(
            origin, direction, destructible["rect"], LONGSHOT_DEAD_LINE_RANGE
        )
        if distance is not None:
            candidates.append((distance, "destructible", destructible))

    for actor in actors:
        if actor is player or actor["team"] == player["team"] or not actor_can_fight(actor):
            continue
        distance = ray_actor_hit_distance(
            origin, direction, actor, LONGSHOT_DEAD_LINE_RANGE
        )
        if distance is not None:
            candidates.append((distance, "actor", actor))

    candidates.sort(key=lambda item: item[0])
    penetrated_obstacle = False
    geometry_changed = False
    impact_distance = LONGSHOT_DEAD_LINE_RANGE

    for distance, target_type, target in candidates:
        if target_type == "actor":
            damage_actor(target, LONGSHOT_DEAD_LINE_DAMAGE, player)
            impact_distance = distance
            break

        if penetrated_obstacle:
            impact_distance = distance
            break

        if target_type == "wall":
            thickness = min(target.width, target.height)
            if thickness > LONGSHOT_DEAD_LINE_MAX_WALL_THICKNESS:
                impact_distance = distance
                break
            penetrated_obstacle = True
            continue

        # Destructible cover counts as the single allowed penetration and takes
        # the supernatural rifle's impact damage at the same time.
        target["health"] = max(
            0.0, target["health"] - LONGSHOT_DEAD_LINE_OBJECT_DAMAGE
        )
        if target["health"] <= 0:
            target["destroyed"] = True
            geometry_changed = True
        penetrated_obstacle = True

    return origin + direction * impact_distance, geometry_changed


def update_longshot_abilities(player, delta_time):
    """Advance Longshot cooldowns, scan pulse, Track duration, and Dead Line timers."""
    if player.get("character_id") != LONGSHOT["id"]:
        return

    state = player["ability_state"]
    state["resonance_cooldown"] = max(
        0.0, state["resonance_cooldown"] - delta_time
    )
    state["resonance_pulse_remaining"] = max(
        0.0, state["resonance_pulse_remaining"] - delta_time
    )
    state["track_cooldown"] = max(0.0, state["track_cooldown"] - delta_time)
    state["track_remaining"] = max(0.0, state["track_remaining"] - delta_time)
    state["dead_line_recovery"] = max(
        0.0, state["dead_line_recovery"] - delta_time
    )
    state["dead_line_tracer_remaining"] = max(
        0.0, state["dead_line_tracer_remaining"] - delta_time
    )


def update_dead_line_weapon(
    player,
    trigger_held,
    aim_angle,
    walls,
    destructible_objects,
    actors,
    delta_time,
):
    """Charge and automatically fire one Dead Line shot after its warning line."""
    if player.get("character_id") != LONGSHOT["id"]:
        return False

    state = player["ability_state"]
    if not state["dead_line_active"]:
        if not trigger_held:
            state["dead_line_requires_release"] = False
        return False

    if not actor_can_fight(player):
        state["dead_line_active"] = False
        state["dead_line_charge"] = 0.0
        return False

    if not trigger_held:
        state["dead_line_requires_release"] = False
        state["dead_line_charge"] = 0.0
        return False

    if state["dead_line_requires_release"] or state["dead_line_recovery"] > 0:
        return False

    state["dead_line_charge"] = min(
        LONGSHOT_DEAD_LINE_AIM_TIME,
        state["dead_line_charge"] + delta_time,
    )
    if state["dead_line_charge"] < LONGSHOT_DEAD_LINE_AIM_TIME:
        return False

    tracer_end, geometry_changed = fire_dead_line_shot(
        player,
        aim_angle,
        walls,
        destructible_objects,
        actors,
    )
    state["dead_line_tracer_start"] = pygame.Vector2(player["position"])
    state["dead_line_tracer_end"] = pygame.Vector2(tracer_end)
    state["dead_line_tracer_remaining"] = LONGSHOT_DEAD_LINE_TRACER_DURATION
    state["dead_line_shots_remaining"] -= 1
    state["dead_line_charge"] = 0.0
    state["dead_line_recovery"] = LONGSHOT_DEAD_LINE_RECOVERY
    state["dead_line_requires_release"] = True
    if state["dead_line_shots_remaining"] <= 0:
        state["dead_line_active"] = False

    return geometry_changed


def sable_scent_evidence_exists(player, actor, obstacles):
    """Require a visible or recently disturbed trail before Scent can find prey."""
    if is_actor_visible(player["position"], actor, obstacles):
        return True
    if actor.get("fired_recent", 0.0) > 0 or actor.get("damaged_recent", 0.0) > 0:
        return True
    return any(event.get("remaining", 0.0) > 0 for event in actor.get("track_events", []))


def sable_injury_label(actor):
    """Return Sable's deliberately approximate wound description."""
    fraction = actor["health"] / max(1.0, actor["max_health"])
    if fraction <= 0.20:
        return "CRITICAL"
    if fraction <= 0.40:
        return "WOUNDED"
    return "INJURED"


def sable_distance_label(distance):
    """Convert exact world distance into a rough hunting-distance band."""
    if distance <= SABLE_SCENT_RADIUS * 0.34:
        return "NEAR"
    if distance <= SABLE_SCENT_RADIUS * 0.67:
        return "MID"
    return "FAR"


def sable_compass_label(vector):
    """Reduce a direction vector to one of eight readable compass directions."""
    if vector.length_squared() <= 0:
        return "HERE"
    angle = (math.degrees(math.atan2(-vector.y, vector.x)) + 360.0) % 360.0
    names = ("E", "NE", "N", "NW", "W", "SW", "S", "SE")
    return names[int((angle + 22.5) // 45.0) % 8]


def try_activate_scent_of_blood(player, actors, obstacles):
    """Sense wounded enemies only when Sable has recent evidence of their passage."""
    if player.get("character_id") != SABLE["id"]:
        return False, "SCENT OF BLOOD UNAVAILABLE"

    state = player["ability_state"]
    if state["scent_remaining"] > 0:
        return False, "SCENT OF BLOOD ALREADY ACTIVE"
    if state["scent_cooldown"] > 0:
        return False, f"SCENT COOLDOWN {state['scent_cooldown']:.1f}s"

    targets = []
    for actor in actors:
        if actor is player or actor["team"] == player["team"] or not actor_can_fight(actor):
            continue
        health_fraction = actor["health"] / max(1.0, actor["max_health"])
        if health_fraction > SABLE_SCENT_HEALTH_THRESHOLD:
            continue
        if player["position"].distance_to(actor["position"]) > SABLE_SCENT_RADIUS:
            continue
        if not sable_scent_evidence_exists(player, actor, obstacles):
            continue
        targets.append(actor)

    state["scent_targets"] = targets
    state["scent_remaining"] = SABLE_SCENT_DURATION
    state["scent_cooldown"] = SABLE_SCENT_COOLDOWN
    return True, f"SCENT OF BLOOD - {len(targets)} PREY FOUND"


def try_activate_wild_hunt(player):
    """Begin Sable's once-per-round camouflage and hunting-knife ultimate."""
    if player.get("character_id") != SABLE["id"]:
        return False, "WILD HUNT UNAVAILABLE"

    state = player["ability_state"]
    if state["wild_hunt_remaining"] > 0:
        return False, "WILD HUNT ALREADY ACTIVE"
    if state["wild_hunt_used"]:
        return False, "WILD HUNT USED THIS ROUND"

    state["wild_hunt_remaining"] = SABLE_WILD_HUNT_DURATION
    state["wild_hunt_used"] = True
    state["wild_hunt_flicker_remaining"] = 0.0
    state["hunt_attack_cooldown"] = 0.0
    state["hunt_attack_animation_timer"] = 0.0
    return True, "WILD HUNT ACTIVE"


def update_sable_abilities(player, delta_time):
    """Advance Sable's Scent, shared Track, camouflage, and knife timers."""
    if player.get("character_id") != SABLE["id"]:
        return

    state = player["ability_state"]
    state["scent_cooldown"] = max(0.0, state["scent_cooldown"] - delta_time)
    state["scent_remaining"] = max(0.0, state["scent_remaining"] - delta_time)
    if state["scent_remaining"] <= 0:
        state["scent_targets"] = []
    state["track_cooldown"] = max(0.0, state["track_cooldown"] - delta_time)
    state["track_remaining"] = max(0.0, state["track_remaining"] - delta_time)
    state["wild_hunt_remaining"] = max(0.0, state["wild_hunt_remaining"] - delta_time)
    state["wild_hunt_flicker_remaining"] = max(
        0.0, state["wild_hunt_flicker_remaining"] - delta_time
    )
    state["hunt_attack_cooldown"] = max(0.0, state["hunt_attack_cooldown"] - delta_time)
    state["hunt_attack_animation_timer"] = max(
        0.0, state["hunt_attack_animation_timer"] - delta_time
    )


def perform_sable_hunting_knife_attack(
    player,
    aim_angle,
    actors,
    obstacles,
    destructible_objects,
    bullet_marks,
):
    """Use the normal melee collision rules while Wild Hunt forces Sable's knife."""
    if not sable_wild_hunt_active(player):
        return False
    state = player["ability_state"]
    if state["hunt_attack_cooldown"] > 0:
        return False

    _, geometry_changed = perform_knife_attack(
        player,
        aim_angle,
        SABLE_HUNTING_KNIFE,
        actors,
        obstacles,
        destructible_objects,
        bullet_marks,
    )
    state["hunt_attack_cooldown"] = SABLE_HUNTING_KNIFE["seconds_per_shot"]
    state["hunt_attack_animation_timer"] = SABLE_HUNTING_KNIFE["attack_animation_time"]
    return geometry_changed


def sable_visible_to_bot(bot, actor, walls):
    """Model Wild Hunt camouflage using each bot's current facing direction."""
    if not sable_wild_hunt_active(actor):
        return is_actor_visible(bot["position"], actor, walls)
    if not is_actor_visible(bot["position"], actor, walls):
        return False

    state = actor.get("ability_state", {})
    if state.get("wild_hunt_flicker_remaining", 0.0) > 0:
        return True

    offset = actor["position"] - bot["position"]
    if offset.length_squared() <= 0:
        return True
    direction_to_sable = offset.normalize()
    bot_forward = pygame.Vector2(math.cos(bot["aim_angle"]), math.sin(bot["aim_angle"]))
    minimum_dot = math.cos(math.radians(SABLE_WILD_HUNT_VIEW_ANGLE_DEGREES))
    return bot_forward.dot(direction_to_sable) >= minimum_dot


def aurel_apply_cinderbolt_explosion(
    player,
    position,
    actors,
    walls,
    destructible_objects,
    bullet_marks,
):
    """Explode Cinderbolt: enemies burn, everyone is pushed, cover takes fire damage."""
    center = pygame.Vector2(position)
    obstacles_before = get_active_obstacle_rects(walls, destructible_objects)
    geometry_changed = False

    # Damage destructible cover first. Cinderbolt weakens cover but does not share
    # Breach Charge's guaranteed-destruction rule.
    for destructible in destructible_objects:
        if destructible["destroyed"]:
            continue
        rectangle = destructible["rect"]
        contact = pygame.Vector2(
            max(rectangle.left, min(center.x, rectangle.right)),
            max(rectangle.top, min(center.y, rectangle.bottom)),
        )
        if center.distance_to(contact) > AUREL_CINDERBOLT_EXPLOSION_RADIUS:
            continue
        if not has_line_of_sight(
            center,
            contact,
            obstacles_before,
            ignored_wall=rectangle,
        ):
            continue
        destructible["health"] = max(
            0.0,
            destructible["health"] - AUREL_CINDERBOLT_OBJECT_DAMAGE,
        )
        if destructible["health"] <= 0:
            destructible["destroyed"] = True
            geometry_changed = True
            bullet_marks[:] = [
                mark for mark in bullet_marks if mark.get("wall") is not rectangle
            ]

    push_obstacles = get_active_obstacle_rects(walls, destructible_objects)
    for actor in actors:
        if not actor_can_fight(actor):
            continue
        offset = actor["position"] - center
        distance = offset.length()
        if distance > AUREL_CINDERBOLT_EXPLOSION_RADIUS:
            continue
        if not has_line_of_sight(center, actor["position"], obstacles_before):
            continue

        # Aurel's fire never damages his team or himself. The physical blast does.
        if actor["team"] != player["team"]:
            damage_actor(actor, AUREL_CINDERBOLT_IMPACT_DAMAGE, player)
            apply_burn(
                actor,
                AUREL_CINDERBOLT_BURN_DURATION,
                AUREL_CINDERBOLT_BURN_MAX_HEALTH_PER_SECOND,
                player,
            )

        if offset.length_squared() > 0:
            push_actor_safely(
                actor,
                offset.normalize(),
                AUREL_CINDERBOLT_PUSH_DISTANCE,
                push_obstacles,
            )

    return geometry_changed


def try_activate_cinderbolt(player, aim_angle):
    """Launch Aurel's visible ranged fireball."""
    if player.get("character_id") != AUREL["id"]:
        return False, "CINDERBOLT UNAVAILABLE"
    if aurel_inferno_charging(player):
        return False, "INFERNO CHARGING"

    state = player["ability_state"]
    if state["cinderbolt_cooldown"] > 0:
        return False, f"CINDERBOLT COOLDOWN {state['cinderbolt_cooldown']:.1f}s"

    direction = pygame.Vector2(math.cos(aim_angle), math.sin(aim_angle))
    muzzle_distance = ACTOR_RADIUS + AUREL_CINDERBOLT_PROJECTILE_RADIUS + 10
    state["cinderbolts"].append(
        {
            "position": pygame.Vector2(player["position"]) + direction * muzzle_distance,
            "velocity": direction * AUREL_CINDERBOLT_SPEED,
            "distance_traveled": 0.0,
        }
    )
    state["cinderbolt_cooldown"] = AUREL_CINDERBOLT_COOLDOWN
    return True, "CINDERBOLT LAUNCHED"


def update_aurel_cinderbolts(
    player,
    actors,
    walls,
    destructible_objects,
    bullet_marks,
    delta_time,
):
    """Move Cinderbolts in small steps and detonate on the first solid contact."""
    state = player["ability_state"]
    surviving = []
    geometry_changed = False

    for bolt in state["cinderbolts"]:
        total_movement = bolt["velocity"] * delta_time
        step_length = max(4.0, AUREL_CINDERBOLT_PROJECTILE_RADIUS * 0.75)
        step_count = max(1, math.ceil(total_movement.length() / step_length))
        movement_step = total_movement / step_count
        exploded = False

        for _ in range(step_count):
            previous_position = pygame.Vector2(bolt["position"])
            bolt["position"] += movement_step
            bolt["distance_traveled"] += movement_step.length()
            center = bolt["position"]
            projectile_rect = pygame.Rect(
                round(center.x - AUREL_CINDERBOLT_PROJECTILE_RADIUS),
                round(center.y - AUREL_CINDERBOLT_PROJECTILE_RADIUS),
                AUREL_CINDERBOLT_PROJECTILE_RADIUS * 2,
                AUREL_CINDERBOLT_PROJECTILE_RADIUS * 2,
            )

            hit_solid = any(projectile_rect.colliderect(wall) for wall in walls)
            if not hit_solid:
                hit_solid = any(
                    not destructible["destroyed"]
                    and projectile_rect.colliderect(destructible["rect"])
                    for destructible in destructible_objects
                )

            hit_actor = False
            if not hit_solid:
                for actor in actors:
                    if actor is player or not actor_can_fight(actor):
                        continue
                    if center.distance_to(actor["position"]) <= (
                        ACTOR_RADIUS + AUREL_CINDERBOLT_PROJECTILE_RADIUS
                    ):
                        hit_actor = True
                        break

            reached_limit = bolt["distance_traveled"] >= AUREL_CINDERBOLT_MAX_RANGE
            if hit_solid or hit_actor or reached_limit:
                explosion_position = previous_position if hit_solid else center
                geometry_changed = (
                    aurel_apply_cinderbolt_explosion(
                        player,
                        explosion_position,
                        actors,
                        walls,
                        destructible_objects,
                        bullet_marks,
                    )
                    or geometry_changed
                )
                state["cinderbolt_explosions"].append(
                    {
                        "position": pygame.Vector2(explosion_position),
                        "remaining": AUREL_CINDERBOLT_EXPLOSION_VISUAL_TIME,
                    }
                )
                exploded = True
                break

        if not exploded:
            surviving.append(bolt)

    state["cinderbolts"] = surviving
    return geometry_changed


def try_activate_explosive_inferno(player):
    """Begin Aurel's once-per-round invulnerable three-second ultimate windup."""
    if player.get("character_id") != AUREL["id"]:
        return False, "EXPLOSIVE INFERNO UNAVAILABLE"

    state = player["ability_state"]
    if state["inferno_charge_remaining"] > 0 or state["inferno_after_remaining"] > 0:
        return False, "EXPLOSIVE INFERNO ALREADY ACTIVE"
    if state["inferno_used"]:
        return False, "EXPLOSIVE INFERNO USED THIS ROUND"

    state["inferno_charge_remaining"] = AUREL_INFERNO_CHARGE_TIME
    state["inferno_used"] = True
    state["fire_trail_last_position"] = pygame.Vector2(player["position"])
    return True, "EXPLOSIVE INFERNO CHARGING"


def aurel_detonate_inferno(
    player,
    actors,
    walls,
    destructible_objects,
    bullet_marks,
):
    """Release the wall-penetrating Inferno blast and start its 15-second aftermath."""
    state = player["ability_state"]
    center = pygame.Vector2(player["position"])
    geometry_changed = False

    # Inferno passes through permanent walls and annihilates every destructible
    # piece of cover whose rectangle reaches the blast radius.
    for destructible in destructible_objects:
        if destructible["destroyed"]:
            continue
        rectangle = destructible["rect"]
        contact = pygame.Vector2(
            max(rectangle.left, min(center.x, rectangle.right)),
            max(rectangle.top, min(center.y, rectangle.bottom)),
        )
        if center.distance_to(contact) > AUREL_INFERNO_RADIUS:
            continue
        destructible["health"] = 0
        destructible["destroyed"] = True
        geometry_changed = True
        bullet_marks[:] = [
            mark for mark in bullet_marks if mark.get("wall") is not rectangle
        ]

    # Destroyed cover no longer blocks the physical displacement, while permanent
    # walls still stop bodies from being shoved through solid architecture.
    push_obstacles = get_active_obstacle_rects(walls, destructible_objects)
    for actor in actors:
        if actor is player or not actor_can_fight(actor):
            continue
        offset = actor["position"] - center
        distance = offset.length()
        if distance > AUREL_INFERNO_RADIUS:
            continue

        # Allies receive only the force. Enemies receive damage + burn + force.
        if actor["team"] != player["team"]:
            damage_actor(actor, AUREL_INFERNO_INITIAL_DAMAGE, player)
            apply_burn(
                actor,
                AUREL_INFERNO_BURN_DURATION,
                AUREL_INFERNO_BURN_MAX_HEALTH_PER_SECOND,
                player,
            )

        if offset.length_squared() > 0:
            push_actor_safely(
                actor,
                offset.normalize(),
                AUREL_INFERNO_PUSH_DISTANCE,
                push_obstacles,
            )

    # Aurel remains precisely at the center: no self-damage, burn, or knockback.
    state["inferno_after_remaining"] = AUREL_INFERNO_AFTEREFFECT_DURATION
    state["inferno_explosion_effect_remaining"] = AUREL_INFERNO_EXPLOSION_VISUAL_TIME
    state["fire_trail_spawn_timer"] = 0.0
    state["fire_trail_last_position"] = pygame.Vector2(player["position"])
    return geometry_changed


def update_aurel_abilities(
    player,
    actors,
    walls,
    destructible_objects,
    bullet_marks,
    delta_time,
):
    """Advance Aurel's fireball, shared Breach timer, Inferno, burns, and fire trail."""
    if player.get("character_id") != AUREL["id"]:
        return None, False

    state = player["ability_state"]
    state["cinderbolt_cooldown"] = max(
        0.0, state["cinderbolt_cooldown"] - delta_time
    )
    state["breach_cooldown"] = max(0.0, state["breach_cooldown"] - delta_time)
    state["breach_effect_remaining"] = max(
        0.0, state["breach_effect_remaining"] - delta_time
    )
    state["inferno_explosion_effect_remaining"] = max(
        0.0, state["inferno_explosion_effect_remaining"] - delta_time
    )

    for explosion in state["cinderbolt_explosions"]:
        explosion["remaining"] -= delta_time
    state["cinderbolt_explosions"] = [
        explosion
        for explosion in state["cinderbolt_explosions"]
        if explosion["remaining"] > 0
    ]

    geometry_changed = update_aurel_cinderbolts(
        player,
        actors,
        walls,
        destructible_objects,
        bullet_marks,
        delta_time,
    )

    message = None
    if state["inferno_charge_remaining"] > 0:
        previous = state["inferno_charge_remaining"]
        state["inferno_charge_remaining"] = max(
            0.0, previous - delta_time
        )
        if previous > 0 and state["inferno_charge_remaining"] <= 0:
            geometry_changed = (
                aurel_detonate_inferno(
                    player,
                    actors,
                    walls,
                    destructible_objects,
                    bullet_marks,
                )
                or geometry_changed
            )
            message = "EXPLOSIVE INFERNO RELEASED"

    if state["inferno_after_remaining"] > 0:
        state["inferno_after_remaining"] = max(
            0.0, state["inferno_after_remaining"] - delta_time
        )
        state["fire_trail_spawn_timer"] = max(
            0.0, state["fire_trail_spawn_timer"] - delta_time
        )

        last_position = state.get("fire_trail_last_position")
        if last_position is None:
            last_position = pygame.Vector2(player["position"])
        moved = player["position"].distance_squared_to(last_position) >= 8 * 8
        if moved and state["fire_trail_spawn_timer"] <= 0:
            state["fire_trail"].append(
                {
                    "position": pygame.Vector2(player["position"]),
                    "remaining": AUREL_FIRE_TRAIL_LIFETIME,
                }
            )
            state["fire_trail_spawn_timer"] = AUREL_FIRE_TRAIL_SPAWN_INTERVAL
        state["fire_trail_last_position"] = pygame.Vector2(player["position"])

    # Fire patches may outlive the 15-second damage buff briefly.
    active_obstacles = get_active_obstacle_rects(walls, destructible_objects)
    for patch in state["fire_trail"]:
        patch["remaining"] -= delta_time
        for actor in actors:
            if (
                actor["team"] == player["team"]
                or not actor_can_fight(actor)
                or actor["position"].distance_to(patch["position"]) > AUREL_FIRE_TRAIL_RADIUS
            ):
                continue
            if not has_line_of_sight(
                patch["position"],
                actor["position"],
                active_obstacles,
            ):
                continue
            apply_burn(
                actor,
                AUREL_TRAIL_BURN_DURATION,
                AUREL_TRAIL_BURN_MAX_HEALTH_PER_SECOND,
                player,
            )
    state["fire_trail"] = [
        patch for patch in state["fire_trail"] if patch["remaining"] > 0
    ]

    return message, geometry_changed


def try_activate_oni_blade(player):
    """Draw Varek's Rift-forged katana for a short close-range attack window."""
    if player.get("character_id") != VAREK["id"]:
        return False, "ONI BLADE UNAVAILABLE"

    state = player["ability_state"]
    if state["fury_remaining"] > 0:
        return False, "ONI BLADE ALREADY DRAWN BY UNBOUND FURY"
    if state["oni_blade_remaining"] > 0:
        return False, "ONI BLADE ALREADY ACTIVE"
    if state["oni_blade_cooldown"] > 0:
        return False, f"ONI BLADE COOLDOWN {state['oni_blade_cooldown']:.1f}s"

    state["oni_blade_remaining"] = VAREK_ONI_BLADE_DURATION
    state["oni_blade_cooldown"] = VAREK_ONI_BLADE_COOLDOWN
    state["blade_attack_cooldown"] = 0.0
    return True, "ONI BLADE DRAWN"


def get_cone_dot_threshold(arc_degrees):
    """Return the facing-dot threshold for a centered cone with this total arc."""
    return math.cos(math.radians(arc_degrees / 2))


def try_activate_breach_charge(
    player,
    aim_angle,
    obstacles,
    destructible_objects,
    actors,
    bullet_marks,
):
    """Use the shared Breaker cone: destroy cover, damage enemies, push everyone."""
    if player.get("character_class") != "Breaker":
        return False, "BREACH CHARGE UNAVAILABLE", False
    if aurel_inferno_charging(player):
        return False, "INFERNO CHARGING", False

    state = player["ability_state"]
    if "breach_cooldown" not in state:
        return False, "BREACH CHARGE UNAVAILABLE", False
    if state["breach_cooldown"] > 0:
        return (
            False,
            f"BREACH CHARGE COOLDOWN {state['breach_cooldown']:.1f}s",
            False,
        )

    forward = pygame.Vector2(math.cos(aim_angle), math.sin(aim_angle))
    minimum_dot = get_cone_dot_threshold(BREAKER_BREACH_ARC_DEGREES)
    geometry_changed = False
    enemies_hit = 0
    allies_pushed = 0
    objects_destroyed = 0

    # The force of Breach Charge affects both teams, but friendly fire is disabled.
    for actor in actors:
        if actor is player or not actor_can_fight(actor):
            continue
        offset = actor["position"] - player["position"]
        distance = offset.length()
        if distance <= 0 or distance > BREAKER_BREACH_RANGE:
            continue
        direction = offset / distance
        if forward.dot(direction) < minimum_dot:
            continue
        if not has_line_of_sight(player["position"], actor["position"], obstacles):
            continue

        if actor["team"] != player["team"]:
            damage_actor(actor, BREAKER_BREACH_DAMAGE, player)
            enemies_hit += 1
        else:
            allies_pushed += 1

        push_actor_safely(
            actor,
            direction,
            BREAKER_BREACH_PUSH_DISTANCE,
            obstacles,
        )

    # Destructible cover no longer has a Breach damage value. If it is inside
    # the class ability's cone and reachable from the caster, it is destroyed.
    for destructible in destructible_objects:
        if destructible["destroyed"]:
            continue
        rectangle = destructible["rect"]
        contact = pygame.Vector2(
            max(rectangle.left, min(player["position"].x, rectangle.right)),
            max(rectangle.top, min(player["position"].y, rectangle.bottom)),
        )
        offset = contact - player["position"]
        distance = offset.length()
        if distance <= 0 or distance > BREAKER_BREACH_RANGE:
            continue
        direction = offset / distance
        if forward.dot(direction) < minimum_dot:
            continue
        if not has_line_of_sight(
            player["position"],
            contact,
            obstacles,
            ignored_wall=rectangle,
        ):
            continue

        destructible["health"] = 0
        destructible["destroyed"] = True
        objects_destroyed += 1
        geometry_changed = True
        bullet_marks[:] = [
            mark for mark in bullet_marks if mark.get("wall") is not rectangle
        ]

    state["breach_cooldown"] = BREAKER_BREACH_COOLDOWN
    state["breach_effect_remaining"] = BREAKER_BREACH_EFFECT_DURATION
    state["breach_angle"] = aim_angle
    return (
        True,
        (
            f"BREACH CHARGE - {enemies_hit} ENEMY / "
            f"{allies_pushed} ALLY PUSHED / {objects_destroyed} COVER DESTROYED"
        ),
        geometry_changed,
    )


def try_activate_unbound_fury(player):
    """Activate Varek's once-per-round pursuit ultimate."""
    if player.get("character_id") != VAREK["id"]:
        return False, "UNBOUND FURY UNAVAILABLE"

    state = player["ability_state"]
    if state["fury_remaining"] > 0:
        return False, "UNBOUND FURY ALREADY ACTIVE"
    if state["fury_used"]:
        return False, "UNBOUND FURY USED THIS ROUND"

    state["fury_remaining"] = VAREK_FURY_DURATION
    state["fury_used"] = True
    state["oni_blade_remaining"] = 0.0
    state["blade_attack_cooldown"] = 0.0
    return True, "UNBOUND FURY ACTIVE"


def update_varek_abilities(player, delta_time):
    """Advance Varek's katana, Breach Charge, and Unbound Fury timers."""
    if player.get("character_id") != VAREK["id"]:
        return

    state = player["ability_state"]
    state["oni_blade_cooldown"] = max(
        0.0, state["oni_blade_cooldown"] - delta_time
    )
    state["oni_blade_remaining"] = max(
        0.0, state["oni_blade_remaining"] - delta_time
    )
    state["blade_attack_cooldown"] = max(
        0.0, state["blade_attack_cooldown"] - delta_time
    )
    state["blade_animation_timer"] = max(
        0.0, state["blade_animation_timer"] - delta_time
    )
    state["breach_cooldown"] = max(0.0, state["breach_cooldown"] - delta_time)
    state["breach_effect_remaining"] = max(
        0.0, state["breach_effect_remaining"] - delta_time
    )
    state["fury_remaining"] = max(0.0, state["fury_remaining"] - delta_time)


def get_character_movement_obstacles(player, walls, destructible_objects, normal_obstacles):
    """Apply character-specific low-cover vaulting while preserving hard walls."""
    if varek_unbound_fury_active(player):
        return walls + [
            destructible["rect"]
            for destructible in destructible_objects
            if not destructible["destroyed"] and destructible["type"] != "crate"
        ]
    return get_miri_movement_obstacles(
        player,
        walls,
        destructible_objects,
        normal_obstacles,
    )


def perform_varek_blade_attack(
    player,
    aim_angle,
    actors,
    obstacles,
    destructible_objects,
    bullet_marks,
):
    """Swing the active Oni Blade and return whether cover geometry changed."""
    if not varek_blade_active(player):
        return False

    state = player["ability_state"]
    if state["blade_attack_cooldown"] > 0:
        return False

    _, geometry_changed = perform_knife_attack(
        player,
        aim_angle,
        VAREK_ONI_BLADE,
        actors,
        obstacles,
        destructible_objects,
        bullet_marks,
    )
    state["blade_attack_cooldown"] = VAREK_ONI_BLADE_SECONDS_PER_SWING
    state["blade_animation_timer"] = VAREK_ONI_BLADE_ANIMATION_TIME
    return geometry_changed



def miri_feline_lunge_active(actor):
    """Return whether Miri currently has her claws drawn for Feline Lunge."""
    return (
        actor.get("character_id") == MIRI["id"]
        and actor.get("ability_state", {}).get("feline_lunge_remaining", 0.0) > 0
    )


def miri_field_treatment_active(actor):
    """Return whether Miri is currently casting her one-second heal."""
    return (
        actor.get("character_id") == MIRI["id"]
        and actor.get("ability_state", {}).get("field_treatment_remaining", 0.0) > 0
    )


def miri_nine_lives_active(actor):
    """Return whether Miri is currently channeling Nine Lives."""
    return (
        actor.get("character_id") == MIRI["id"]
        and actor.get("ability_state", {}).get("nine_lives_remaining", 0.0) > 0
    )


def try_activate_feline_lunge(player):
    """Draw Miri's claws and allow her to vault low crate cover temporarily."""
    if player.get("character_id") != MIRI["id"]:
        return False, "FELINE LUNGE UNAVAILABLE"

    state = player["ability_state"]
    if state["nine_lives_remaining"] > 0:
        return False, "NINE LIVES CHANNEL IN PROGRESS"
    if state["feline_lunge_remaining"] > 0:
        return False, "FELINE LUNGE ALREADY ACTIVE"
    if state["feline_lunge_cooldown"] > 0:
        return False, f"FELINE LUNGE COOLDOWN {state['feline_lunge_cooldown']:.1f}s"

    state["feline_lunge_remaining"] = MIRI_FELINE_LUNGE_DURATION
    state["feline_lunge_cooldown"] = MIRI_FELINE_LUNGE_COOLDOWN
    state["claw_attack_cooldown"] = 0.0
    return True, "FELINE LUNGE ACTIVE"


def try_activate_field_treatment(player):
    """Begin Miri's one-second nearby-ally healing cast."""
    if player.get("character_id") != MIRI["id"]:
        return False, "FIELD TREATMENT UNAVAILABLE"

    state = player["ability_state"]
    if state["nine_lives_remaining"] > 0:
        return False, "NINE LIVES CHANNEL IN PROGRESS"
    if state["field_treatment_remaining"] > 0:
        return False, "FIELD TREATMENT ALREADY CASTING"
    if state["field_treatment_cooldown"] > 0:
        return False, f"FIELD TREATMENT COOLDOWN {state['field_treatment_cooldown']:.1f}s"

    state["field_treatment_remaining"] = MIRI_FIELD_TREATMENT_CAST_TIME
    state["field_treatment_pending"] = True
    state["field_treatment_cooldown"] = MIRI_FIELD_TREATMENT_COOLDOWN
    return True, "FIELD TREATMENT CASTING"


def find_miri_nine_lives_target(player, actors, obstacles):
    """Return the nearest eligible eliminated teammate inside resurrection range."""
    candidates = []
    for actor in actors:
        if actor is player or actor["team"] != player["team"]:
            continue
        if not actor["eliminated"] or actor.get("resurrected_this_round", False):
            continue
        distance = player["position"].distance_to(actor["position"])
        if distance > MIRI_NINE_LIVES_RANGE:
            continue
        if not has_line_of_sight(player["position"], actor["position"], obstacles):
            continue
        candidates.append((distance, actor))

    if not candidates:
        return None
    return min(candidates, key=lambda item: item[0])[1]


def try_activate_nine_lives(player, actors, obstacles):
    """Start Miri's four-second channel beside a fully eliminated teammate."""
    if player.get("character_id") != MIRI["id"]:
        return False, "NINE LIVES UNAVAILABLE"

    state = player["ability_state"]
    if state["nine_lives_remaining"] > 0:
        return False, "NINE LIVES ALREADY CHANNELING"
    if state["nine_lives_used"]:
        return False, "NINE LIVES USED THIS ROUND"

    target = find_miri_nine_lives_target(player, actors, obstacles)
    if target is None:
        return False, "NO ELIMINATED ALLY IN RANGE"

    state["feline_lunge_remaining"] = 0.0
    state["field_treatment_remaining"] = 0.0
    state["field_treatment_pending"] = False
    state["nine_lives_remaining"] = MIRI_NINE_LIVES_CHANNEL_TIME
    state["nine_lives_target"] = target
    state["nine_lives_start_position"] = pygame.Vector2(player["position"])
    return True, f"NINE LIVES - REVIVING {target['name']}"


def cancel_nine_lives(player):
    """Stop an interrupted Nine Lives channel without consuming the ultimate."""
    if player.get("character_id") != MIRI["id"]:
        return
    state = player["ability_state"]
    state["nine_lives_remaining"] = 0.0
    state["nine_lives_target"] = None
    state["nine_lives_start_position"] = None


def resurrect_actor_with_nine_lives(target):
    """Return a fully eliminated ally for one final life this round."""
    target["health"] = min(MIRI_NINE_LIVES_REVIVE_HEALTH, target["max_health"])
    target["alive"] = True
    target["downed"] = False
    target["eliminated"] = False
    target["revive_progress"] = 0.0
    target["revive_source"] = None
    target["movement_sound_radius"] = 0.0
    target["resurrected_this_round"] = True
    # Keep times_downed at 2+. If this resurrected actor is defeated again,
    # they are eliminated immediately instead of receiving another normal down.


def update_miri_abilities(player, actors, obstacles, delta_time):
    """Advance Miri's mobility, healing cast, and resurrection channel."""
    if player.get("character_id") != MIRI["id"]:
        return None

    state = player["ability_state"]
    state["feline_lunge_cooldown"] = max(
        0.0, state["feline_lunge_cooldown"] - delta_time
    )
    state["feline_lunge_remaining"] = max(
        0.0, state["feline_lunge_remaining"] - delta_time
    )
    state["claw_attack_cooldown"] = max(
        0.0, state["claw_attack_cooldown"] - delta_time
    )
    state["claw_animation_timer"] = max(
        0.0, state["claw_animation_timer"] - delta_time
    )
    state["field_treatment_cooldown"] = max(
        0.0, state["field_treatment_cooldown"] - delta_time
    )

    healed_count = None
    if state["field_treatment_remaining"] > 0:
        previous = state["field_treatment_remaining"]
        state["field_treatment_remaining"] = max(0.0, previous - delta_time)
        if state["field_treatment_remaining"] <= 0 and state["field_treatment_pending"]:
            state["field_treatment_pending"] = False
            healed_count = 0
            for actor in actors:
                if actor is player or actor["team"] != player["team"]:
                    continue
                if not actor_can_fight(actor):
                    continue
                if player["position"].distance_to(actor["position"]) > MIRI_FIELD_TREATMENT_RADIUS:
                    continue
                missing_health = max(0.0, actor["max_health"] - actor["health"])
                heal_amount = missing_health * MIRI_FIELD_TREATMENT_MISSING_HEALTH_FRACTION
                if heal_amount <= 0:
                    continue
                actor["health"] = min(actor["max_health"], actor["health"] + heal_amount)
                healed_count += 1

    if state["nine_lives_remaining"] > 0:
        target = state["nine_lives_target"]
        start_position = state["nine_lives_start_position"]
        valid_target = (
            target is not None
            and target.get("eliminated", False)
            and not target.get("resurrected_this_round", False)
            and player["position"].distance_to(target["position"]) <= MIRI_NINE_LIVES_RANGE
            and has_line_of_sight(player["position"], target["position"], obstacles)
        )
        moved_too_far = (
            start_position is None
            or player["position"].distance_to(start_position) > MIRI_NINE_LIVES_MOVE_CANCEL_DISTANCE
        )
        if not valid_target or moved_too_far:
            cancel_nine_lives(player)
            return "NINE LIVES INTERRUPTED"

        state["nine_lives_remaining"] = max(
            0.0, state["nine_lives_remaining"] - delta_time
        )
        if state["nine_lives_remaining"] <= 0:
            resurrect_actor_with_nine_lives(target)
            state["nine_lives_used"] = True
            state["nine_lives_target"] = None
            state["nine_lives_start_position"] = None
            return f"{target['name']} RETURNED TO THE FIGHT"

    if healed_count is not None:
        return f"FIELD TREATMENT HEALED {healed_count} ALLY" if healed_count == 1 else f"FIELD TREATMENT HEALED {healed_count} ALLIES"
    return None


def get_miri_movement_obstacles(player, walls, destructible_objects, normal_obstacles):
    """During Feline Lunge, Miri can vault crates but not walls or doors."""
    if not miri_feline_lunge_active(player):
        return normal_obstacles
    return walls + [
        destructible["rect"]
        for destructible in destructible_objects
        if not destructible["destroyed"] and destructible["type"] != "crate"
    ]


def perform_miri_claw_attack(player, aim_angle, actors, obstacles):
    """Strike the nearest visible enemy in Miri's claw arc; cover is not damaged."""
    if not miri_feline_lunge_active(player):
        return False
    state = player["ability_state"]
    if state["claw_attack_cooldown"] > 0:
        return False

    forward = pygame.Vector2(math.cos(aim_angle), math.sin(aim_angle))
    minimum_dot = get_cone_dot_threshold(MIRI_CLAW_ARC_DEGREES)
    valid_targets = []
    for actor in actors:
        if actor is player or actor["team"] == player["team"] or not actor_can_fight(actor):
            continue
        offset = actor["position"] - player["position"]
        distance = offset.length()
        if distance <= 0 or distance > MIRI_CLAW_RANGE:
            continue
        direction = offset / distance
        if forward.dot(direction) < minimum_dot:
            continue
        if not has_line_of_sight(player["position"], actor["position"], obstacles):
            continue
        valid_targets.append((distance, actor))

    if valid_targets:
        _, target = min(valid_targets, key=lambda item: item[0])
        damage_actor(target, MIRI_CLAW_DAMAGE, player)

    state["claw_attack_cooldown"] = MIRI_CLAW_SECONDS_PER_ATTACK
    state["claw_animation_timer"] = MIRI_CLAW_ANIMATION_TIME
    return True


def relay_inside_rift(player, rift_state):
    """Return whether Relay is close enough to interface with the active Rift."""
    return (
        actor_can_fight(player)
        and player["position"].distance_to(rift_state["position"]) <= RIFT_RADIUS
    )


def relay_teleport_selecting(player):
    """Return whether Relay is waiting for the player to choose a map quadrant."""
    return (
        player.get("character_id") == RELAY["id"]
        and player.get("ability_state", {}).get("rift_teleport_selecting", False)
    )


def relay_teleport_channel_active(player):
    """Return whether Relay is in the three-second teleport channel."""
    return (
        player.get("character_id") == RELAY["id"]
        and player.get("ability_state", {}).get("rift_teleport_remaining", 0.0) > 0
    )


def try_activate_rift_boost(player):
    """Consume Relay's stored Rift charge and empower the next 20 projectiles."""
    if player.get("character_id") != RELAY["id"]:
        return False, "RIFT BOOST UNAVAILABLE"
    state = player["ability_state"]
    if state["rift_boost_bullets_remaining"] > 0:
        return False, f"RIFT BOOST {state['rift_boost_bullets_remaining']} PROJECTILES LEFT"
    if state["rift_boost_cooldown"] > 0:
        return False, f"RIFT BOOST COOLDOWN {state['rift_boost_cooldown']:.1f}s"
    if not state["rift_boost_charged"]:
        return False, "RIFT BOOST NEEDS 3s OF RIFT CHARGE"

    state["rift_boost_charged"] = False
    state["rift_boost_charge_progress"] = 0.0
    state["rift_boost_bullets_remaining"] = RELAY_RIFT_BOOST_PROJECTILES
    return True, f"RIFT BOOST ACTIVE - {RELAY_RIFT_BOOST_PROJECTILES} PROJECTILES"


def try_activate_rift_teleport(player, rift_state):
    """Open Relay's four-quadrant Rift Teleport selector while at the Rift."""
    if player.get("character_id") != RELAY["id"]:
        return False, "RIFT TELEPORT UNAVAILABLE"
    state = player["ability_state"]
    if state["rift_teleport_remaining"] > 0:
        return False, "RIFT TELEPORT ALREADY CHANNELING"
    if state["rift_teleport_cooldown"] > 0:
        return False, f"RIFT TELEPORT COOLDOWN {state['rift_teleport_cooldown']:.1f}s"
    if not relay_inside_rift(player, rift_state):
        return False, "RIFT TELEPORT REQUIRES THE ACTIVE RIFT"

    state["rift_teleport_selecting"] = True
    state["rift_teleport_quadrant"] = None
    return True, "RIFT TELEPORT - CHOOSE A QUADRANT (1-4)"


def begin_relay_rift_teleport(player, quadrant, rift_state):
    """Begin the three-second teleport channel toward a chosen map quadrant."""
    if player.get("character_id") != RELAY["id"]:
        return False, "RIFT TELEPORT UNAVAILABLE"
    state = player["ability_state"]
    if not state.get("rift_teleport_selecting", False):
        return False, "RIFT TELEPORT NOT SELECTING"
    if not relay_inside_rift(player, rift_state):
        state["rift_teleport_selecting"] = False
        return False, "RIFT TELEPORT CANCELLED - LEFT THE RIFT"
    if quadrant not in ("top_left", "top_right", "bottom_left", "bottom_right"):
        return False, "INVALID RIFT TELEPORT QUADRANT"

    state["rift_teleport_selecting"] = False
    state["rift_teleport_quadrant"] = quadrant
    state["rift_teleport_remaining"] = RELAY_RIFT_TELEPORT_CHANNEL
    return True, f"RIFT TELEPORT CHANNELING - {quadrant.replace('_', ' ').upper()}"


def get_relay_quadrant_bounds(quadrant):
    """Return safe random-landing bounds for one of the four map quadrants."""
    margin = RELAY_RIFT_TELEPORT_SAFE_MARGIN
    mid_x = WORLD_WIDTH / 2
    mid_y = WORLD_HEIGHT / 2
    if quadrant == "top_left":
        return margin, mid_x - margin / 2, margin, mid_y - margin / 2
    if quadrant == "top_right":
        return mid_x + margin / 2, WORLD_WIDTH - margin, margin, mid_y - margin / 2
    if quadrant == "bottom_left":
        return margin, mid_x - margin / 2, mid_y + margin / 2, WORLD_HEIGHT - margin
    return mid_x + margin / 2, WORLD_WIDTH - margin, mid_y + margin / 2, WORLD_HEIGHT - margin


def choose_relay_teleport_destination(quadrant, obstacles):
    """Choose a random clear point inside Relay's selected map quadrant."""
    min_x, max_x, min_y, max_y = get_relay_quadrant_bounds(quadrant)
    for _ in range(RELAY_RIFT_TELEPORT_ATTEMPTS):
        candidate = pygame.Vector2(
            random.uniform(min_x, max_x),
            random.uniform(min_y, max_y),
        )
        if actor_position_is_clear(candidate, obstacles):
            return candidate
    return None


def try_activate_rift_overclock(player, rift_state):
    """Overclock a friendly-owned Rift so its 60-second hold timer runs 1.5x."""
    if player.get("character_id") != RELAY["id"]:
        return False, "RIFT OVERCLOCK UNAVAILABLE"
    state = player["ability_state"]
    if state["rift_overclock_active"]:
        return False, "RIFT OVERCLOCK ALREADY ACTIVE"
    if state["rift_overclock_used"]:
        return False, "RIFT OVERCLOCK USED THIS ROUND"
    if rift_state["owner"] != player["team"]:
        return False, "YOUR TEAM MUST CONTROL THE RIFT"
    if rift_state["contested"]:
        return False, "RIFT OVERCLOCK CANNOT START WHILE CONTESTED"
    if not relay_inside_rift(player, rift_state):
        return False, "RIFT OVERCLOCK REQUIRES THE ACTIVE RIFT"

    state["rift_overclock_active"] = True
    state["rift_overclock_used"] = True
    enemy_team = "red" if player["team"] == "blue" else "blue"
    rift_state["overclock_alert_team"] = enemy_team
    rift_state["overclock_alert_remaining"] = 4.0
    return True, "RIFT OVERCLOCK ACTIVE - ENEMY TEAM ALERTED"


def update_relay_abilities(player, rift_state, obstacles, delta_time):
    """Advance Relay charging, teleport channel, and cooldown state."""
    if player.get("character_id") != RELAY["id"]:
        return None, False

    state = player["ability_state"]
    state["rift_boost_cooldown"] = max(0.0, state["rift_boost_cooldown"] - delta_time)
    state["rift_teleport_cooldown"] = max(0.0, state["rift_teleport_cooldown"] - delta_time)

    message = None
    teleported = False

    # A stored charge is personal to Relay; it does not spend the team's shared
    # Rift Energy resource. Leaving the Rift before three seconds resets progress.
    can_charge = (
        relay_inside_rift(player, rift_state)
        and state["rift_boost_cooldown"] <= 0
        and not state["rift_boost_charged"]
        and state["rift_boost_bullets_remaining"] <= 0
    )
    if can_charge:
        old_progress = state["rift_boost_charge_progress"]
        state["rift_boost_charge_progress"] = min(
            RELAY_RIFT_BOOST_CHARGE_TIME, old_progress + delta_time
        )
        if old_progress < RELAY_RIFT_BOOST_CHARGE_TIME <= state["rift_boost_charge_progress"]:
            state["rift_boost_charged"] = True
            message = "RIFT BOOST CHARGED"
    elif not state["rift_boost_charged"] and state["rift_boost_bullets_remaining"] <= 0:
        state["rift_boost_charge_progress"] = 0.0

    if state["rift_teleport_selecting"] and not relay_inside_rift(player, rift_state):
        state["rift_teleport_selecting"] = False
        state["rift_teleport_quadrant"] = None
        message = "RIFT TELEPORT CANCELLED - LEFT THE RIFT"

    if state["rift_teleport_remaining"] > 0:
        if not relay_inside_rift(player, rift_state):
            state["rift_teleport_remaining"] = 0.0
            state["rift_teleport_quadrant"] = None
            message = "RIFT TELEPORT INTERRUPTED"
        else:
            state["rift_teleport_remaining"] = max(
                0.0, state["rift_teleport_remaining"] - delta_time
            )
            if state["rift_teleport_remaining"] <= 0:
                destination = choose_relay_teleport_destination(
                    state["rift_teleport_quadrant"], obstacles
                )
                if destination is None:
                    message = "RIFT TELEPORT FAILED - NO SAFE LANDING"
                else:
                    player["position"].update(destination)
                    state["rift_teleport_cooldown"] = RELAY_RIFT_TELEPORT_COOLDOWN
                    teleported = True
                    message = "RIFT TELEPORT COMPLETE"
                state["rift_teleport_quadrant"] = None

    return message, teleported


def perform_knife_attack(
    attacker,
    aim_angle,
    knife,
    actors,
    obstacles,
    destructible_objects,
    bullet_marks,
):
    """Damage the nearest enemy, crate, or door inside the knife's arc."""
    attack_direction = pygame.Vector2(
        math.cos(aim_angle),
        math.sin(aim_angle),
    )
    minimum_facing_dot = math.cos(
        math.radians(knife["melee_arc_degrees"] / 2)
    )
    valid_targets = []

    for actor in actors:
        if (
            actor is attacker
            or actor["team"] == attacker["team"]
            or not actor_can_fight(actor)
        ):
            continue

        target_vector = actor["position"] - attacker["position"]
        target_distance = target_vector.length()
        if target_distance <= 0 or target_distance > knife["melee_range"]:
            continue

        target_direction = target_vector / target_distance
        if attack_direction.dot(target_direction) < minimum_facing_dot:
            continue
        if not has_line_of_sight(
            attacker["position"],
            actor["position"],
            obstacles,
        ):
            continue

        valid_targets.append((target_distance, "actor", actor))

    for destructible in destructible_objects:
        if destructible["destroyed"]:
            continue

        rectangle = destructible["rect"]
        contact_point = pygame.Vector2(
            max(rectangle.left, min(attacker["position"].x, rectangle.right)),
            max(rectangle.top, min(attacker["position"].y, rectangle.bottom)),
        )
        target_vector = contact_point - attacker["position"]
        target_distance = target_vector.length()
        if target_distance <= 0 or target_distance > knife["melee_range"]:
            continue

        target_direction = target_vector / target_distance
        if attack_direction.dot(target_direction) < minimum_facing_dot:
            continue
        if not has_line_of_sight(
            attacker["position"],
            contact_point,
            obstacles,
            ignored_wall=rectangle,
        ):
            continue

        valid_targets.append(
            (target_distance, "destructible", destructible)
        )

    if not valid_targets:
        return None, False

    _, target_type, target = min(
        valid_targets,
        key=lambda candidate: candidate[0],
    )
    weapon_damage = knife["damage"] * get_weapon_damage_multiplier(attacker)
    if target_type == "actor":
        damage_actor(target, weapon_damage, attacker)
        return target, False

    target["health"] = max(0, target["health"] - weapon_damage)
    if target["health"] == 0:
        target["destroyed"] = True
        target_rect = target["rect"]
        bullet_marks[:] = [
            mark
            for mark in bullet_marks
            if mark.get("wall") is not target_rect
        ]
        return target, True

    return target, False


def update_bullets(
    bullets,
    delta_time,
    walls,
    destructible_objects,
    actors,
    bullet_marks,
):
    """Move bullets and damage the first actor, object, or wall they strike."""
    surviving_bullets = []
    obstacle_geometry_changed = False

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

            hit_destructible = get_bullet_hit_destructible(
                bullet,
                destructible_objects,
            )
            if hit_destructible is not None:
                hit_rect = hit_destructible["rect"]
                hit_destructible["health"] = max(
                    0,
                    hit_destructible["health"]
                    - calculate_bullet_damage(bullet),
                )

                if hit_destructible["health"] == 0:
                    hit_destructible["destroyed"] = True
                    obstacle_geometry_changed = True
                    # Remove marks attached to an object that no longer exists.
                    bullet_marks[:] = [
                        mark
                        for mark in bullet_marks
                        if mark.get("wall") is not hit_rect
                    ]
                else:
                    bullet_marks.append(create_bullet_mark(bullet, hit_rect))
                    if len(bullet_marks) > MAX_BULLET_MARKS:
                        del bullet_marks[0]

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
                    damage_actor(actor, hit_damage, bullet["shooter"])

                    bullet_removed = True
                    break

            if not bullet_removed:
                for decoy_target in get_haze_hallucination_targets(
                    bullet["team"], actors
                ):
                    distance_to_decoy = bullet["position"].distance_to(
                        decoy_target["position"]
                    )
                    if distance_to_decoy <= bullet["radius"] + ACTOR_RADIUS:
                        hit_damage = calculate_bullet_damage(bullet)
                        damage_haze_hallucination(
                            decoy_target["haze_owner"], hit_damage
                        )
                        bullet_removed = True
                        break

            if bullet_removed:
                break

        if not bullet_removed:
            surviving_bullets.append(bullet)

    return surviving_bullets, obstacle_geometry_changed


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


def get_bot_navigation_cell_center(cell):
    """Return the world-space center of one coarse navigation-grid cell."""
    column, row = cell
    half_cell = BOT_NAVIGATION_GRID_SIZE / 2
    return pygame.Vector2(
        min(WORLD_WIDTH - ACTOR_RADIUS, column * BOT_NAVIGATION_GRID_SIZE + half_cell),
        min(WORLD_HEIGHT - ACTOR_RADIUS, row * BOT_NAVIGATION_GRID_SIZE + half_cell),
    )


def build_bot_walkable_grid(walls):
    """Return grid cells whose centers safely fit a full character body."""
    columns = math.ceil(WORLD_WIDTH / BOT_NAVIGATION_GRID_SIZE)
    rows = math.ceil(WORLD_HEIGHT / BOT_NAVIGATION_GRID_SIZE)
    walkable = set()
    for row in range(rows):
        for column in range(columns):
            cell = (column, row)
            if actor_position_is_clear(get_bot_navigation_cell_center(cell), walls):
                walkable.add(cell)
    return walkable


def get_nearest_walkable_bot_cell(position, walkable_cells):
    """Choose the clear navigation cell whose center is nearest a world point."""
    if not walkable_cells:
        return None
    position = pygame.Vector2(position)
    return min(
        walkable_cells,
        key=lambda cell: position.distance_squared_to(
            get_bot_navigation_cell_center(cell)
        ),
    )


def find_bot_navigation_path(start_position, target_position, walls):
    """Find a cached four-direction A* path around the current collision map."""
    walkable = build_bot_walkable_grid(walls)
    start_cell = get_nearest_walkable_bot_cell(start_position, walkable)
    goal_cell = get_nearest_walkable_bot_cell(target_position, walkable)
    if start_cell is None or goal_cell is None:
        return []
    if start_cell == goal_cell:
        return [get_bot_navigation_cell_center(start_cell)]

    frontier = []
    heapq.heappush(frontier, (0, start_cell))
    came_from = {}
    cost_so_far = {start_cell: 0}

    while frontier:
        _, current = heapq.heappop(frontier)
        if current == goal_cell:
            break

        column, row = current
        for neighbor in (
            (column + 1, row),
            (column - 1, row),
            (column, row + 1),
            (column, row - 1),
        ):
            if neighbor not in walkable:
                continue
            new_cost = cost_so_far[current] + 1
            if new_cost >= cost_so_far.get(neighbor, float("inf")):
                continue
            cost_so_far[neighbor] = new_cost
            came_from[neighbor] = current
            heuristic = abs(neighbor[0] - goal_cell[0]) + abs(
                neighbor[1] - goal_cell[1]
            )
            heapq.heappush(frontier, (new_cost + heuristic, neighbor))

    if goal_cell not in cost_so_far:
        return []

    cell_path = [goal_cell]
    while cell_path[-1] != start_cell:
        parent = came_from.get(cell_path[-1])
        if parent is None:
            return []
        cell_path.append(parent)
    cell_path.reverse()
    return [get_bot_navigation_cell_center(cell) for cell in cell_path]


def clear_bot_navigation_path(bot):
    """Forget a cached navigation path without changing the bot's patrol route."""
    bot["navigation_path"] = []
    bot["navigation_path_index"] = 0


def get_bot_navigation_destination(bot, target_position, walls):
    """Return the next cached A* waypoint toward a Rift or downed teammate."""
    target_position = pygame.Vector2(target_position)
    bot_position = bot["position"]

    # Do not abandon the collision-aware route merely because the centers of the
    # bot and target have line of sight. A center ray can squeeze past a corner
    # that a 55-pixel character body cannot, which was another source of stalls.
    # The cached grid route is followed until its final cell, then the bot makes
    # the short direct approach to the exact target position.

    cached_target = bot.get("navigation_target")
    target_changed = (
        cached_target is None
        or pygame.Vector2(cached_target).distance_to(target_position)
        > BOT_NAVIGATION_TARGET_CHANGE_DISTANCE
    )
    path = bot.get("navigation_path", [])
    path_index = bot.get("navigation_path_index", 0)

    # If combat dragged the bot far away from its old next cell, recalculate from
    # the new position instead of trying to return to an obsolete route segment.
    path_stale = False
    if path and path_index < len(path):
        next_position = pygame.Vector2(path[path_index])
        if bot_position.distance_to(next_position) > BOT_NAVIGATION_REPATH_DISTANCE:
            path_stale = True

    if target_changed or not path or path_index >= len(path) or path_stale:
        path = find_bot_navigation_path(bot_position, target_position, walls)
        bot["navigation_path"] = path
        bot["navigation_path_index"] = 0
        bot["navigation_target"] = pygame.Vector2(target_position)
        path_index = 0

    if not path:
        return get_bot_patrol_destination(bot)

    # Move cell-by-cell. Crucially, the completed index is stored on the bot, so it
    # can never repeatedly choose its current position as the next destination.
    while path_index < len(path):
        waypoint = pygame.Vector2(path[path_index])
        if bot_position.distance_to(waypoint) > BOT_NAVIGATION_REACHED_DISTANCE:
            break
        path_index += 1

    bot["navigation_path_index"] = path_index
    if path_index < len(path):
        return pygame.Vector2(path[path_index])

    return target_position


def get_bot_rift_destination(bot, rift_state, walls):
    """Navigate toward the active Rift without getting trapped at a waypoint."""
    return get_bot_navigation_destination(bot, rift_state["position"], walls)


def get_bot_revival_destination(bot, downed_ally, walls):
    """Use the same collision-aware navigation to reach a downed teammate."""
    return get_bot_navigation_destination(bot, downed_ally["position"], walls)


def update_bot(bot, actors, walls, bullets, delta_time, rift_state):
    """Run bot priorities: revive, fight, then contest or defend the Rift."""
    if not actor_can_fight(bot):
        return

    bot["shot_cooldown"] = max(0.0, bot["shot_cooldown"] - delta_time)
    bot["heard_timer"] = max(0.0, bot["heard_timer"] - delta_time)
    if bot["heard_timer"] == 0:
        bot["heard_position"] = None
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
        # A bot no longer has to SEE the downed teammate before volunteering.
        # The nearest standing bot is assigned, then navigates toward the revive.
        possible_revivers = [
            actor
            for actor in actors
            if actor["team"] == bot["team"]
            and not actor["is_player"]
            and actor_can_fight(actor)
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
        ally_visible = has_line_of_sight(
            bot["position"],
            downed_ally["position"],
            walls,
        )
        if ally_distance > REVIVE_RANGE or not ally_visible:
            move_actor_toward(
                bot,
                get_bot_revival_destination(bot, downed_ally, walls),
                BOT_SPEED,
                delta_time,
                walls,
            )
        else:
            try_revive(bot, downed_ally, delta_time, walls)
        return

    enemy_team = "red" if bot["team"] == "blue" else "blue"
    team_has_rift_intel = (
        rift_state["owner"] == bot["team"]
        and rift_state["intel_remaining"] > 0
    )
    visible_enemies = [
        actor
        for actor in actors
        if actor["team"] == enemy_team
        and actor_can_fight(actor)
        and (
            team_has_rift_intel
            or sable_visible_to_bot(bot, actor, walls)
        )
    ]
    # The AI receives Haze's false targets through the same perception list as
    # real enemies, so the deception is useful in the current single-player build.
    visible_enemies.extend(get_haze_false_targets_for_bot(bot, actors, walls))

    if not visible_enemies:
        # Movement sound gives bots only a rough location to investigate. They
        # still require real line of sight before they are allowed to fire.
        heard_enemies = [
            actor
            for actor in actors
            if actor["team"] == enemy_team
            and actor_can_fight(actor)
            and actor.get("movement_sound_radius", 0.0) > 0
            and bot["position"].distance_to(actor["position"])
            <= actor["movement_sound_radius"]
        ]
        if heard_enemies:
            heard_actor = min(
                heard_enemies,
                key=lambda actor: bot["position"].distance_squared_to(
                    actor["position"]
                ),
            )
            bot["heard_position"] = pygame.Vector2(heard_actor["position"])
            bot["heard_timer"] = MALPHAS_SOUND_MEMORY

        if bot["heard_position"] is not None and bot["heard_timer"] > 0:
            sound_vector = bot["heard_position"] - bot["position"]
            if sound_vector.length_squared() > 0:
                bot["aim_angle"] = math.atan2(sound_vector.y, sound_vector.x)
            if sound_vector.length() > 55:
                move_actor_toward(
                    bot,
                    bot["heard_position"],
                    BOT_SPEED,
                    delta_time,
                    walls,
                )
            return

        rift_distance = bot["position"].distance_to(rift_state["position"])
        if rift_distance > RIFT_RADIUS * 0.60:
            move_actor_toward(
                bot,
                get_bot_rift_destination(bot, rift_state, walls),
                BOT_SPEED,
                delta_time,
                walls,
            )
        else:
            # Face outward while holding the site instead of piling into its
            # exact center. Actor separation handles the remaining spacing.
            outward = bot["position"] - rift_state["position"]
            if outward.length_squared() > 0:
                bot["aim_angle"] = math.atan2(outward.y, outward.x)
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
    if (
        target.get("character_id") == SABLE["id"]
        and not team_has_rift_intel
    ):
        target_in_line_of_sight = sable_visible_to_bot(bot, target, walls)
    else:
        target_in_line_of_sight = is_actor_visible(
            bot["position"],
            target,
            walls,
        )

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

    if bot["shot_cooldown"] <= 0 and target_in_line_of_sight:
        bot_weapon_index = get_bot_weapon_index(bot, target_distance)
        bot_weapon = WEAPONS[bot_weapon_index]
        projectile_count = bot_weapon.get("projectiles_per_shot", 1)
        bot_spread = max(BOT_SPREAD, bot_weapon["standing_spread"])
        if projectile_count > 1:
            damage_override = max(1, round(BOT_BULLET_DAMAGE * 0.65))
        else:
            damage_override = BOT_BULLET_DAMAGE

        for _ in range(projectile_count):
            bullets.append(
                create_bullet(
                    bot,
                    bot["aim_angle"],
                    bot_spread,
                    bot_weapon,
                    damage_override=damage_override,
                )
            )

        bot["shot_cooldown"] = max(
            BOT_FIRE_INTERVAL,
            bot_weapon["seconds_per_shot"],
        )


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


def draw_destructible_object(screen, destructible, camera, hidden=False):
    """Draw a crate or door with a material style distinct from concrete."""
    if destructible["destroyed"]:
        return

    rectangle = destructible["rect"]
    screen_rect = rectangle.move(-round(camera.x), -round(camera.y))
    object_type = destructible["type"]

    if object_type == "door":
        fill_color = HIDDEN_DOOR_COLOR if hidden else DOOR_COLOR
        edge_color = HIDDEN_DOOR_EDGE_COLOR if hidden else DOOR_EDGE_COLOR
    else:
        fill_color = HIDDEN_CRATE_COLOR if hidden else CRATE_COLOR
        edge_color = HIDDEN_CRATE_EDGE_COLOR if hidden else CRATE_EDGE_COLOR

    pygame.draw.rect(screen, fill_color, screen_rect, border_radius=4)
    pygame.draw.rect(
        screen,
        edge_color,
        screen_rect,
        width=3,
        border_radius=4,
    )

    inset_rect = screen_rect.inflate(-14, -14)
    if inset_rect.width > 0 and inset_rect.height > 0:
        pygame.draw.rect(screen, edge_color, inset_rect, width=2)

    if object_type == "door":
        # Hinges, inset panels, and a handle make this read as a door instead
        # of another permanent gray wall section.
        panel_gap = max(8, screen_rect.height // 3)
        pygame.draw.line(
            screen,
            edge_color,
            (inset_rect.left, inset_rect.top + panel_gap),
            (inset_rect.right, inset_rect.top + panel_gap),
            width=2,
        )
        pygame.draw.line(
            screen,
            edge_color,
            (inset_rect.left, inset_rect.bottom - panel_gap),
            (inset_rect.right, inset_rect.bottom - panel_gap),
            width=2,
        )
        hinge_x = screen_rect.left + 6
        for hinge_y in (screen_rect.top + 22, screen_rect.bottom - 22):
            pygame.draw.rect(
                screen,
                edge_color,
                (hinge_x, hinge_y - 6, 7, 12),
                border_radius=2,
            )
        pygame.draw.circle(
            screen,
            edge_color,
            (screen_rect.right - 15, screen_rect.centery),
            5,
        )
    else:
        # The large X brace is the visual language for destructible crates.
        pygame.draw.line(
            screen,
            edge_color,
            inset_rect.topleft,
            inset_rect.bottomright,
            width=4,
        )
        pygame.draw.line(
            screen,
            edge_color,
            inset_rect.topright,
            inset_rect.bottomleft,
            width=4,
        )

    if not hidden:
        health_fraction = (
            destructible["health"] / destructible["max_health"]
        )
        crack_color = (54, 37, 30)
        if health_fraction < 0.67:
            pygame.draw.line(
                screen,
                crack_color,
                screen_rect.center,
                (screen_rect.centerx - 15, screen_rect.centery + 18),
                width=3,
            )
        if health_fraction < 0.34:
            pygame.draw.line(
                screen,
                crack_color,
                screen_rect.center,
                (screen_rect.centerx + 18, screen_rect.centery - 20),
                width=3,
            )


def draw_hidden_destructibles(screen, destructible_objects, camera):
    """Keep complete destructible silhouettes readable outside line of sight."""
    for destructible in destructible_objects:
        draw_destructible_object(
            screen,
            destructible,
            camera,
            hidden=True,
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

    is_malphas = actor.get("character_id") == MALPHAS["id"]
    is_longshot = actor.get("character_id") == LONGSHOT["id"]
    is_varek = actor.get("character_id") == VAREK["id"]
    is_miri = actor.get("character_id") == MIRI["id"]
    is_relay = actor.get("character_id") == RELAY["id"]
    is_haze = actor.get("character_id") == HAZE["id"]
    is_sable = actor.get("character_id") == SABLE["id"]
    is_aurel = actor.get("character_id") == AUREL["id"]
    if is_malphas and not actor["downed"] and not actor["eliminated"]:
        fill_color = MALPHAS_BODY_COLOR
        # Keep the blue outer edge so the playable character still reads as
        # a blue-team actor even though his body has unique placeholder art.
        edge_color = PLAYER_EDGE_COLOR if actor["team"] == "blue" else edge_color
    elif is_longshot and not actor["downed"] and not actor["eliminated"]:
        fill_color = LONGSHOT_BODY_COLOR
        edge_color = PLAYER_EDGE_COLOR if actor["team"] == "blue" else edge_color
    elif is_varek and not actor["downed"] and not actor["eliminated"]:
        fill_color = VAREK_BODY_COLOR
        edge_color = PLAYER_EDGE_COLOR if actor["team"] == "blue" else edge_color
    elif is_miri and not actor["downed"] and not actor["eliminated"]:
        fill_color = MIRI_BODY_COLOR
        edge_color = PLAYER_EDGE_COLOR if actor["team"] == "blue" else edge_color
    elif is_relay and not actor["downed"] and not actor["eliminated"]:
        fill_color = RELAY_BODY_COLOR
        edge_color = PLAYER_EDGE_COLOR if actor["team"] == "blue" else edge_color
    elif is_haze and not actor["downed"] and not actor["eliminated"]:
        fill_color = HAZE_BODY_COLOR
        edge_color = PLAYER_EDGE_COLOR if actor["team"] == "blue" else edge_color
    elif is_sable and not actor["downed"] and not actor["eliminated"]:
        fill_color = SABLE_BODY_COLOR
        edge_color = PLAYER_EDGE_COLOR if actor["team"] == "blue" else edge_color
    elif is_aurel and not actor["downed"] and not actor["eliminated"]:
        fill_color = AUREL_BODY_COLOR
        edge_color = PLAYER_EDGE_COLOR if actor["team"] == "blue" else edge_color

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

    if is_malphas:
        # Simple top-down demon placeholder: two swept horns, a Rift-lit core,
        # and a pointed face. This will be replaced by final character artwork.
        horn_left_base = center + facing * 3 + side * 13
        horn_right_base = center + facing * 3 - side * 13
        pygame.draw.polygon(
            screen,
            MALPHAS_HORN_COLOR,
            (
                horn_left_base - facing * 5 - side * 5,
                horn_left_base + facing * 4 + side * 4,
                center + facing * 25 + side * 22,
            ),
        )
        pygame.draw.polygon(
            screen,
            MALPHAS_HORN_COLOR,
            (
                horn_right_base - facing * 5 + side * 5,
                horn_right_base + facing * 4 - side * 4,
                center + facing * 25 - side * 22,
            ),
        )
        pygame.draw.circle(screen, MALPHAS_GLOW_COLOR, center_tuple, 10)
        face_tip = center + facing * 30
        face_left = center + facing * 4 + side * 9
        face_right = center + facing * 4 - side * 9
        pygame.draw.polygon(
            screen,
            MALPHAS_GLOW_COLOR,
            (face_tip, face_left, face_right),
        )
        if malphas_bloodlust_active(actor):
            pulse = 4 + round(3 * math.sin(pygame.time.get_ticks() * 0.012))
            pygame.draw.circle(
                screen,
                MALPHAS_EFFECT_COLOR,
                center_tuple,
                radius + 7 + pulse,
                width=3,
            )
    elif is_longshot:
        # Hunter placeholder: armored body, luminous visor, and a long rifle
        # silhouette aligned with the character's aim direction.
        visor_center = center + facing * 9
        visor_start = visor_center - side * 12
        visor_end = visor_center + side * 12
        pygame.draw.line(
            screen,
            LONGSHOT_VISOR_COLOR,
            visor_start,
            visor_end,
            width=6,
        )
        shoulder_left = center + side * 16 - facing * 4
        shoulder_right = center - side * 16 - facing * 4
        pygame.draw.line(
            screen,
            LONGSHOT_ARMOR_COLOR,
            shoulder_left,
            shoulder_right,
            width=7,
        )
        rifle_start = center - facing * 5 - side * 8
        rifle_end = center + facing * 43 - side * 8
        pygame.draw.line(
            screen,
            LONGSHOT_RIFLE_COLOR,
            rifle_start,
            rifle_end,
            width=5,
        )
        pygame.draw.circle(screen, LONGSHOT_VISOR_COLOR, center_tuple, 5)
    elif is_varek:
        # Breaker placeholder: broad plated shoulders, a pale mask, and a
        # Rift-forged katana carried along the character's dominant side.
        shoulder_left = center + side * 18 - facing * 5
        shoulder_right = center - side * 18 - facing * 5
        pygame.draw.line(
            screen,
            VAREK_ARMOR_COLOR,
            shoulder_left,
            shoulder_right,
            width=9,
        )
        mask_center = center + facing * 9
        pygame.draw.circle(
            screen,
            VAREK_MASK_COLOR,
            (round(mask_center.x), round(mask_center.y)),
            8,
        )
        blade_start = center - facing * 7 - side * 13
        blade_end = center + facing * 36 - side * 13
        pygame.draw.line(
            screen,
            VAREK_BLADE_COLOR,
            blade_start,
            blade_end,
            width=4,
        )
        if varek_unbound_fury_active(actor):
            pulse = 4 + round(3 * math.sin(pygame.time.get_ticks() * 0.014))
            pygame.draw.circle(
                screen,
                VAREK_FURY_COLOR,
                center_tuple,
                radius + 8 + pulse,
                width=3,
            )
    elif is_miri:
        # Top-down placeholder: white lab coat, pink body, and large cat ears.
        ear_forward = center + facing * 16
        left_ear = ear_forward + side * 15
        right_ear = ear_forward - side * 15
        pygame.draw.polygon(
            screen,
            MIRI_EAR_COLOR,
            (left_ear - facing * 8 - side * 7, left_ear + side * 6, left_ear + facing * 19),
        )
        pygame.draw.polygon(
            screen,
            MIRI_EAR_COLOR,
            (right_ear - facing * 8 + side * 7, right_ear - side * 6, right_ear + facing * 19),
        )
        pygame.draw.circle(screen, MIRI_EAR_INNER_COLOR, (round(left_ear.x), round(left_ear.y)), 4)
        pygame.draw.circle(screen, MIRI_EAR_INNER_COLOR, (round(right_ear.x), round(right_ear.y)), 4)
        coat_left = center - facing * 7 + side * 15
        coat_right = center - facing * 7 - side * 15
        pygame.draw.line(screen, MIRI_COAT_COLOR, coat_left, center + facing * 18 + side * 7, width=7)
        pygame.draw.line(screen, MIRI_COAT_COLOR, coat_right, center + facing * 18 - side * 7, width=7)
        pygame.draw.circle(screen, MIRI_HEAL_COLOR, center_tuple, 6)
    elif is_relay:
        # Conduit placeholder: thin silver chassis with exposed joints and
        # purple Rift conduits glowing through hands, feet, and chest.
        shoulder_left = center + side * 11 - facing * 5
        shoulder_right = center - side * 11 - facing * 5
        pygame.draw.line(screen, RELAY_JOINT_COLOR, shoulder_left, shoulder_right, width=5)
        pygame.draw.line(screen, RELAY_BODY_COLOR, center - facing * 15, center + facing * 19, width=8)
        hand_left = center + facing * 5 + side * 20
        hand_right = center + facing * 5 - side * 20
        foot_left = center - facing * 19 + side * 9
        foot_right = center - facing * 19 - side * 9
        pygame.draw.circle(screen, RELAY_RIFT_COLOR, (round(hand_left.x), round(hand_left.y)), 5)
        pygame.draw.circle(screen, RELAY_RIFT_COLOR, (round(hand_right.x), round(hand_right.y)), 5)
        pygame.draw.circle(screen, RELAY_RIFT_COLOR, (round(foot_left.x), round(foot_left.y)), 4)
        pygame.draw.circle(screen, RELAY_RIFT_COLOR, (round(foot_right.x), round(foot_right.y)), 4)
        pygame.draw.circle(screen, RELAY_CORE_COLOR, center_tuple, 7)
        relay_state = actor.get("ability_state", {})
        if relay_state.get("rift_boost_bullets_remaining", 0) > 0:
            pygame.draw.circle(screen, RELAY_RIFT_COLOR, center_tuple, radius + 7, width=2)
    elif is_sable:
        # Wilderness Hunter placeholder: leather gear, short dark hair, green
        # warpaint, and a compact silhouette suited to stalking through cover.
        shoulder_left = center + side * 15 - facing * 4
        shoulder_right = center - side * 15 - facing * 4
        pygame.draw.line(screen, SABLE_LEATHER_COLOR, shoulder_left, shoulder_right, width=8)
        hair_center = center + facing * 10
        pygame.draw.circle(
            screen, SABLE_HAIR_COLOR,
            (round(hair_center.x), round(hair_center.y)), 14,
        )
        paint_center = center + facing * 13
        pygame.draw.line(
            screen, SABLE_WARPAINT_COLOR,
            paint_center + side * 5 - facing * 2,
            paint_center + side * 12 - facing * 2,
            width=3,
        )
        pygame.draw.line(
            screen, SABLE_WARPAINT_COLOR,
            paint_center - side * 5 - facing * 2,
            paint_center - side * 12 - facing * 2,
            width=3,
        )
        if sable_wild_hunt_active(actor):
            pulse = 3 + round(2 * math.sin(pygame.time.get_ticks() * 0.012))
            pygame.draw.circle(
                screen, SABLE_CAMOUFLAGE_COLOR, center_tuple, radius + 6 + pulse, width=2
            )
    elif is_aurel:
        # Sleek elven fire-mage placeholder: pale suit, gold trim, flowing
        # coattails, long white hair, and bright gold eyes.
        shoulder_left = center + side * 14 - facing * 4
        shoulder_right = center - side * 14 - facing * 4
        pygame.draw.line(
            screen, AUREL_SUIT_COLOR, shoulder_left, shoulder_right, width=8
        )
        coat_back = center - facing * 12
        pygame.draw.line(
            screen,
            AUREL_GOLD_COLOR,
            coat_back + side * 13,
            center - facing * 34 + side * 18,
            width=5,
        )
        pygame.draw.line(
            screen,
            AUREL_GOLD_COLOR,
            coat_back - side * 13,
            center - facing * 34 - side * 18,
            width=5,
        )
        hair_center = center + facing * 8
        pygame.draw.circle(
            screen,
            AUREL_HAIR_COLOR,
            (round(hair_center.x), round(hair_center.y)),
            13,
        )
        eye_center = center + facing * 13
        pygame.draw.line(
            screen,
            AUREL_EYE_COLOR,
            eye_center - side * 7,
            eye_center + side * 7,
            width=3,
        )
        pygame.draw.circle(screen, AUREL_GOLD_COLOR, center_tuple, 5)
        if aurel_inferno_charging(actor):
            pygame.draw.circle(
                screen, AUREL_FIRE_GOLD_COLOR, center_tuple, radius + 9, width=3
            )
        elif aurel_inferno_after_active(actor):
            pulse = 3 + round(2 * math.sin(pygame.time.get_ticks() * 0.014))
            pygame.draw.circle(
                screen, AUREL_FIRE_COLOR, center_tuple, radius + 6 + pulse, width=2
            )
    elif is_haze:
        # Torn gray cloak, completely shadowed hood, and Rift-colored core.
        cloak_back = center - facing * 15
        cloak_left = cloak_back + side * 20
        cloak_right = cloak_back - side * 20
        cloak_tip = center - facing * 29
        pygame.draw.polygon(
            screen, HAZE_CLOAK_COLOR,
            (center + facing * 12, cloak_left, cloak_tip, cloak_right),
        )
        hood_center = center + facing * 10
        pygame.draw.circle(
            screen, HAZE_CLOAK_COLOR,
            (round(hood_center.x), round(hood_center.y)), 17,
        )
        hood_shadow = hood_center + facing * 3
        pygame.draw.circle(
            screen, HAZE_SHADOW_COLOR,
            (round(hood_shadow.x), round(hood_shadow.y)), 11,
        )
        pygame.draw.circle(screen, HAZE_PURPLE_COLOR, center_tuple, 6)
        pygame.draw.circle(screen, HAZE_GREEN_COLOR, center_tuple, 3)
    else:
        arrow_tip = center + facing * 34
        arrow_left = center - facing * 5 + side * 10
        arrow_right = center - facing * 5 - side * 10
        pygame.draw.polygon(screen, edge_color, (arrow_tip, arrow_left, arrow_right))

    if actor.get("burn_remaining", 0.0) > 0:
        flicker = 2 + round(2 * math.sin(pygame.time.get_ticks() * 0.025))
        pygame.draw.circle(
            screen,
            AUREL_FIRE_COLOR,
            center_tuple,
            radius + 4 + flicker,
            width=2,
        )
        flame_tip = center - pygame.Vector2(0, radius + 10 + flicker)
        pygame.draw.circle(
            screen,
            AUREL_FIRE_GOLD_COLOR,
            (round(flame_tip.x), round(flame_tip.y)),
            4,
        )

    bar_width = 70
    bar_height = 8
    bar_x = round(center.x - bar_width / 2)
    bar_y = round(center.y - ACTOR_RADIUS - 20)
    health_fraction = actor["health"] / actor["max_health"]
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


def draw_malphas_world_effects(screen, player, camera):
    """Draw temporary visual telegraphs for Malphas's active abilities."""
    if player.get("character_id") != MALPHAS["id"]:
        return

    state = player["ability_state"]
    if state["hellstep_target"] is not None:
        target = pygame.Vector2(state["hellstep_target"]) - camera
        center = (round(target.x), round(target.y))
        progress = 1.0 - min(
            1.0,
            state["hellstep_windup"] / MALPHAS_HELLSTEP_DELAY,
        )
        radius = 24 + round(18 * progress)
        pygame.draw.circle(screen, (48, 16, 28), center, radius + 8)
        pygame.draw.circle(
            screen, MALPHAS_EFFECT_COLOR, center, radius, width=4
        )
        pygame.draw.line(
            screen,
            MALPHAS_HORN_COLOR,
            (center[0] - 14, center[1]),
            (center[0] + 14, center[1]),
            width=3,
        )
        pygame.draw.line(
            screen,
            MALPHAS_HORN_COLOR,
            (center[0], center[1] - 14),
            (center[0], center[1] + 14),
            width=3,
        )

    if state["bloodlust_remaining"] > 0:
        center_world = player["position"] - camera
        center = (round(center_world.x), round(center_world.y))
        pygame.draw.circle(
            screen,
            MALPHAS_EFFECT_COLOR,
            center,
            MALPHAS_BLOODLUST_RADIUS,
            width=2,
        )


def draw_longshot_world_effects(screen, player, actors, camera):
    """Draw Longshot scan echoes, Track trails, and Dead Line telegraphs."""
    if player.get("character_id") != LONGSHOT["id"]:
        return

    state = player["ability_state"]
    player_center = pygame.Vector2(player["position"] - camera)
    center_tuple = (round(player_center.x), round(player_center.y))

    if state["resonance_pulse_remaining"] > 0:
        progress = 1.0 - min(
            1.0,
            state["resonance_pulse_remaining"] / LONGSHOT_RESONANCE_PULSE_DURATION,
        )
        radius = max(8, round(LONGSHOT_RESONANCE_RADIUS * progress))
        pygame.draw.circle(
            screen,
            LONGSHOT_EFFECT_COLOR,
            center_tuple,
            radius,
            width=3,
        )

    # Resonance Sweep creates historical snapshots rather than wall-hack
    # silhouettes that continuously track an enemy's live movement.
    for actor in actors:
        if actor["team"] == player["team"]:
            continue
        if actor.get("resonance_echo_remaining", 0.0) <= 0:
            continue
        echo_position = actor.get("resonance_echo_position")
        if echo_position is None:
            continue
        screen_position = pygame.Vector2(echo_position) - camera
        echo_center = (round(screen_position.x), round(screen_position.y))
        if not screen.get_rect().inflate(100, 100).collidepoint(echo_center):
            continue
        pulse = 4 + round(3 * math.sin(pygame.time.get_ticks() * 0.015))
        pygame.draw.circle(
            screen,
            LONGSHOT_VISOR_COLOR,
            echo_center,
            ACTOR_RADIUS + 7 + pulse,
            width=3,
        )
        pygame.draw.line(
            screen,
            LONGSHOT_VISOR_COLOR,
            (echo_center[0] - 11, echo_center[1]),
            (echo_center[0] + 11, echo_center[1]),
            width=2,
        )

    if state["dead_line_active"] and state["dead_line_charge"] > 0:
        direction = pygame.Vector2(
            math.cos(player["aim_angle"]),
            math.sin(player["aim_angle"]),
        )
        line_end_world = player["position"] + direction * LONGSHOT_DEAD_LINE_RANGE
        line_end = line_end_world - camera
        charge_fraction = min(
            1.0, state["dead_line_charge"] / LONGSHOT_DEAD_LINE_AIM_TIME
        )
        line_width = 1 + round(3 * charge_fraction)
        pygame.draw.line(
            screen,
            LONGSHOT_VISOR_COLOR,
            center_tuple,
            (round(line_end.x), round(line_end.y)),
            width=line_width,
        )

    if (
        state["dead_line_tracer_remaining"] > 0
        and state["dead_line_tracer_start"] is not None
        and state["dead_line_tracer_end"] is not None
    ):
        start = pygame.Vector2(state["dead_line_tracer_start"]) - camera
        end = pygame.Vector2(state["dead_line_tracer_end"]) - camera
        pygame.draw.line(
            screen,
            LONGSHOT_RIFLE_COLOR,
            (round(start.x), round(start.y)),
            (round(end.x), round(end.y)),
            width=7,
        )
        pygame.draw.line(
            screen,
            LONGSHOT_VISOR_COLOR,
            (round(start.x), round(start.y)),
            (round(end.x), round(end.y)),
            width=2,
        )


def draw_hunter_track_effects(screen, player, actors, camera):
    """Draw the shared Hunter Track markers for Longshot or Sable."""
    if player.get("character_class") != "Hunter":
        return
    state = player.get("ability_state", {})
    if state.get("track_remaining", 0.0) <= 0:
        return

    track_color = SABLE_TRACK_COLOR if player.get("character_id") == SABLE["id"] else LONGSHOT_TRACK_COLOR
    fire_color = SABLE_WARPAINT_COLOR if player.get("character_id") == SABLE["id"] else LONGSHOT_VISOR_COLOR
    for actor in actors:
        if actor["team"] == player["team"]:
            continue
        for event in actor.get("track_events", []):
            position = pygame.Vector2(event["position"]) - camera
            center = (round(position.x), round(position.y))
            if not screen.get_rect().inflate(80, 80).collidepoint(center):
                continue
            fraction = min(1.0, event["remaining"] / LONGSHOT_TRACK_EVENT_LIFETIME)
            radius = max(3, round(7 * fraction))
            if event["kind"] == "fire":
                pygame.draw.circle(screen, fire_color, center, radius + 5, width=2)
                pygame.draw.line(screen, fire_color, (center[0] - 6, center[1] - 6), (center[0] + 6, center[1] + 6), width=2)
            else:
                pygame.draw.circle(screen, track_color, center, radius)
                pygame.draw.circle(screen, (21, 40, 35), center, max(1, radius - 3))


def draw_sable_world_effects(screen, font, player, actors, camera):
    """Draw Scent hints, Wild Hunt leaves, camouflage aura, and hunting knife."""
    if player.get("character_id") != SABLE["id"]:
        return

    state = player["ability_state"]
    center = pygame.Vector2(player["position"] - camera)

    if state.get("scent_remaining", 0.0) > 0:
        valid_targets = []
        for actor in state.get("scent_targets", []):
            if not actor_can_fight(actor) or actor["team"] == player["team"]:
                continue
            health_fraction = actor["health"] / max(1.0, actor["max_health"])
            if health_fraction > SABLE_SCENT_HEALTH_THRESHOLD:
                continue
            offset = actor["position"] - player["position"]
            distance = offset.length()
            if distance > SABLE_SCENT_RADIUS:
                continue
            valid_targets.append(actor)
            direction = offset.normalize() if distance > 0 else pygame.Vector2(1, 0)
            marker = center + direction * 145
            marker_center = (round(marker.x), round(marker.y))
            pygame.draw.circle(screen, SABLE_TRACK_COLOR, marker_center, 15, width=3)
            tip = marker + direction * 17
            perpendicular = pygame.Vector2(-direction.y, direction.x)
            left = marker - direction * 6 + perpendicular * 8
            right = marker - direction * 6 - perpendicular * 8
            pygame.draw.polygon(screen, SABLE_TRACK_COLOR, (tip, left, right))
            label = font.render(
                f"{sable_injury_label(actor)} | {sable_compass_label(offset)} | {sable_distance_label(distance)}",
                True,
                SABLE_TRACK_COLOR,
            )
            screen.blit(label, label.get_rect(center=(marker_center[0], marker_center[1] - 28)))
            for event in actor.get("track_events", [])[-3:]:
                event_center = pygame.Vector2(event["position"] - camera)
                if screen.get_rect().inflate(60, 60).collidepoint(event_center):
                    pygame.draw.circle(screen, SABLE_WARPAINT_COLOR, (round(event_center.x), round(event_center.y)), 5, width=2)
        state["scent_targets"] = valid_targets

    if sable_wild_hunt_active(player):
        ticks = pygame.time.get_ticks()
        for index in range(16):
            x = (index * 173 + ticks * (0.018 + 0.003 * (index % 4))) % (screen.get_width() + 80) - 40
            y = (index * 109 + ticks * (0.030 + 0.004 * (index % 3))) % (screen.get_height() + 100) - 50
            size = 4 + index % 4
            pygame.draw.ellipse(screen, SABLE_CAMOUFLAGE_COLOR, (round(x), round(y), size * 2, size))
        draw_knife(screen, player, camera, player["aim_angle"], state.get("hunt_attack_animation_timer", 0.0))


def draw_varek_world_effects(screen, player, camera):
    """Draw Varek's active katana, Breach cone, and Unbound Fury aura."""
    if player.get("character_id") != VAREK["id"]:
        return

    state = player["ability_state"]
    center = pygame.Vector2(player["position"] - camera)
    center_tuple = (round(center.x), round(center.y))

    if varek_blade_active(player):
        swing_progress = 0.0
        if state["blade_animation_timer"] > 0:
            swing_progress = 1.0 - min(
                1.0,
                state["blade_animation_timer"] / VAREK_ONI_BLADE_ANIMATION_TIME,
            )
        swing_offset = math.radians(-42 + 84 * swing_progress)
        blade_angle = player["aim_angle"] + swing_offset
        direction = pygame.Vector2(math.cos(blade_angle), math.sin(blade_angle))
        side = pygame.Vector2(-direction.y, direction.x)
        handle = center + direction * 11
        tip = center + direction * 72
        pygame.draw.line(
            screen,
            (45, 52, 61),
            handle - side * 7,
            handle + side * 7,
            width=5,
        )
        pygame.draw.line(
            screen,
            VAREK_BLADE_COLOR,
            handle,
            tip,
            width=7,
        )
        pygame.draw.line(
            screen,
            (225, 247, 255),
            handle,
            tip,
            width=2,
        )

    if state["breach_effect_remaining"] > 0:
        fraction = min(
            1.0,
            state["breach_effect_remaining"] / BREAKER_BREACH_EFFECT_DURATION,
        )
        forward = pygame.Vector2(
            math.cos(state["breach_angle"]), math.sin(state["breach_angle"])
        )
        half_arc = math.radians(BREAKER_BREACH_ARC_DEGREES / 2)
        left = pygame.Vector2(
            math.cos(state["breach_angle"] - half_arc),
            math.sin(state["breach_angle"] - half_arc),
        )
        right = pygame.Vector2(
            math.cos(state["breach_angle"] + half_arc),
            math.sin(state["breach_angle"] + half_arc),
        )
        distance = BREAKER_BREACH_RANGE * (1.0 - 0.25 * fraction)
        points = [
            center_tuple,
            (round((center + left * distance).x), round((center + left * distance).y)),
            (round((center + forward * distance).x), round((center + forward * distance).y)),
            (round((center + right * distance).x), round((center + right * distance).y)),
        ]
        effect_layer = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        pygame.draw.polygon(
            effect_layer,
            (*VAREK_EFFECT_COLOR, round(75 * fraction)),
            points,
        )
        pygame.draw.lines(
            effect_layer,
            (*VAREK_EFFECT_COLOR, round(210 * fraction)),
            False,
            points,
            width=3,
        )
        screen.blit(effect_layer, (0, 0))

    if state["fury_remaining"] > 0:
        pulse = 7 + round(5 * math.sin(pygame.time.get_ticks() * 0.018))
        pygame.draw.circle(
            screen,
            VAREK_FURY_COLOR,
            center_tuple,
            ACTOR_RADIUS + 12 + pulse,
            width=3,
        )



def draw_aurel_world_effects(screen, player, camera):
    """Draw Aurel's fireballs, shared Breach cone, Inferno charge, blast, and trail."""
    if player.get("character_id") != AUREL["id"]:
        return

    state = player["ability_state"]
    center = pygame.Vector2(player["position"] - camera)
    center_tuple = (round(center.x), round(center.y))

    # Cinderbolt projectile and its bright traveling wake.
    for bolt in state.get("cinderbolts", []):
        bolt_center = pygame.Vector2(bolt["position"] - camera)
        velocity = pygame.Vector2(bolt["velocity"])
        direction = velocity.normalize() if velocity.length_squared() > 0 else pygame.Vector2(1, 0)
        for trail_index in range(1, 5):
            trail_center = bolt_center - direction * (trail_index * 10)
            radius = max(2, AUREL_CINDERBOLT_PROJECTILE_RADIUS - trail_index * 2)
            pygame.draw.circle(
                screen,
                AUREL_FIRE_COLOR,
                (round(trail_center.x), round(trail_center.y)),
                radius,
            )
        pygame.draw.circle(
            screen,
            AUREL_FIRE_GOLD_COLOR,
            (round(bolt_center.x), round(bolt_center.y)),
            AUREL_CINDERBOLT_PROJECTILE_RADIUS,
        )
        pygame.draw.circle(
            screen,
            (255, 240, 178),
            (round(bolt_center.x), round(bolt_center.y)),
            max(3, AUREL_CINDERBOLT_PROJECTILE_RADIUS // 2),
        )

    for explosion in state.get("cinderbolt_explosions", []):
        fraction = max(
            0.0,
            min(1.0, explosion["remaining"] / AUREL_CINDERBOLT_EXPLOSION_VISUAL_TIME),
        )
        explosion_center = pygame.Vector2(explosion["position"] - camera)
        radius = round(AUREL_CINDERBOLT_EXPLOSION_RADIUS * (1.0 - 0.35 * fraction))
        layer = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        pygame.draw.circle(
            layer,
            (*AUREL_FIRE_COLOR, round(70 * fraction)),
            (round(explosion_center.x), round(explosion_center.y)),
            radius,
        )
        pygame.draw.circle(
            layer,
            (*AUREL_FIRE_GOLD_COLOR, round(235 * fraction)),
            (round(explosion_center.x), round(explosion_center.y)),
            radius,
            width=5,
        )
        screen.blit(layer, (0, 0))

    # Shared Breach Charge gets Aurel's fire-gold visual language.
    if state.get("breach_effect_remaining", 0.0) > 0:
        fraction = min(
            1.0,
            state["breach_effect_remaining"] / BREAKER_BREACH_EFFECT_DURATION,
        )
        half_arc = math.radians(BREAKER_BREACH_ARC_DEGREES / 2)
        left = pygame.Vector2(
            math.cos(state["breach_angle"] - half_arc),
            math.sin(state["breach_angle"] - half_arc),
        )
        forward = pygame.Vector2(
            math.cos(state["breach_angle"]),
            math.sin(state["breach_angle"]),
        )
        right = pygame.Vector2(
            math.cos(state["breach_angle"] + half_arc),
            math.sin(state["breach_angle"] + half_arc),
        )
        distance = BREAKER_BREACH_RANGE * (1.0 - 0.25 * fraction)
        points = [
            center_tuple,
            (round((center + left * distance).x), round((center + left * distance).y)),
            (round((center + forward * distance).x), round((center + forward * distance).y)),
            (round((center + right * distance).x), round((center + right * distance).y)),
        ]
        layer = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        pygame.draw.polygon(
            layer,
            (*AUREL_FIRE_COLOR, round(75 * fraction)),
            points,
        )
        pygame.draw.lines(
            layer,
            (*AUREL_FIRE_GOLD_COLOR, round(220 * fraction)),
            False,
            points,
            width=3,
        )
        screen.blit(layer, (0, 0))

    if state.get("inferno_charge_remaining", 0.0) > 0:
        progress = 1.0 - min(
            1.0,
            state["inferno_charge_remaining"] / AUREL_INFERNO_CHARGE_TIME,
        )
        layer = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        for ring_index in range(3):
            radius = round(55 + progress * 110 + ring_index * 24)
            pygame.draw.circle(
                layer,
                (*AUREL_FIRE_GOLD_COLOR, 100 + ring_index * 35),
                center_tuple,
                radius,
                width=4,
            )
        pygame.draw.circle(
            layer,
            (*AUREL_INFERNO_COLOR, round(45 + progress * 70)),
            center_tuple,
            round(45 + progress * 65),
        )
        screen.blit(layer, (0, 0))

    if state.get("inferno_explosion_effect_remaining", 0.0) > 0:
        fraction = min(
            1.0,
            state["inferno_explosion_effect_remaining"] / AUREL_INFERNO_EXPLOSION_VISUAL_TIME,
        )
        radius = round(AUREL_INFERNO_RADIUS * (1.0 - 0.72 * fraction))
        layer = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        pygame.draw.circle(
            layer,
            (*AUREL_INFERNO_COLOR, round(55 * fraction)),
            center_tuple,
            radius,
        )
        pygame.draw.circle(
            layer,
            (*AUREL_FIRE_GOLD_COLOR, round(235 * fraction)),
            center_tuple,
            radius,
            width=8,
        )
        screen.blit(layer, (0, 0))

    for patch in state.get("fire_trail", []):
        patch_center = pygame.Vector2(patch["position"] - camera)
        fade = max(0.0, min(1.0, patch["remaining"] / AUREL_FIRE_TRAIL_LIFETIME))
        layer = pygame.Surface((AUREL_FIRE_TRAIL_RADIUS * 2 + 12, AUREL_FIRE_TRAIL_RADIUS * 2 + 12), pygame.SRCALPHA)
        local_center = (layer.get_width() // 2, layer.get_height() // 2)
        pygame.draw.circle(
            layer,
            (*AUREL_INFERNO_COLOR, round(75 * fade)),
            local_center,
            AUREL_FIRE_TRAIL_RADIUS,
        )
        pygame.draw.circle(
            layer,
            (*AUREL_FIRE_GOLD_COLOR, round(150 * fade)),
            local_center,
            max(5, AUREL_FIRE_TRAIL_RADIUS // 2),
        )
        screen.blit(
            layer,
            (
                round(patch_center.x - layer.get_width() / 2),
                round(patch_center.y - layer.get_height() / 2),
            ),
        )


def draw_miri_world_effects(screen, player, camera):
    """Draw Miri's claws, healing pulse, and Nine Lives resurrection channel."""
    if player.get("character_id") != MIRI["id"]:
        return

    state = player["ability_state"]
    center = pygame.Vector2(player["position"] - camera)
    center_tuple = (round(center.x), round(center.y))

    if state["feline_lunge_remaining"] > 0:
        pulse = 4 + round(2 * math.sin(pygame.time.get_ticks() * 0.016))
        pygame.draw.circle(
            screen,
            MIRI_EAR_COLOR,
            center_tuple,
            ACTOR_RADIUS + 7 + pulse,
            width=2,
        )
        direction = pygame.Vector2(math.cos(player["aim_angle"]), math.sin(player["aim_angle"]))
        side = pygame.Vector2(-direction.y, direction.x)
        swing = 0.0
        if state["claw_animation_timer"] > 0:
            swing = math.radians(30) * (1.0 - state["claw_animation_timer"] / MIRI_CLAW_ANIMATION_TIME)
        for side_sign in (-1, 1):
            claw_dir = direction.rotate_rad(swing * side_sign)
            start = center + claw_dir * 20 + side * 7 * side_sign
            end = center + claw_dir * 43 + side * 10 * side_sign
            pygame.draw.line(screen, MIRI_COAT_COLOR, start, end, width=3)

    if state["field_treatment_remaining"] > 0:
        progress = 1.0 - min(
            1.0,
            state["field_treatment_remaining"] / MIRI_FIELD_TREATMENT_CAST_TIME,
        )
        radius = round(MIRI_FIELD_TREATMENT_RADIUS * (0.35 + 0.65 * progress))
        pygame.draw.circle(screen, MIRI_HEAL_COLOR, center_tuple, radius, width=3)

    if state["nine_lives_remaining"] > 0 and state["nine_lives_target"] is not None:
        target = state["nine_lives_target"]
        target_center = pygame.Vector2(target["position"] - camera)
        target_tuple = (round(target_center.x), round(target_center.y))
        progress = 1.0 - min(
            1.0,
            state["nine_lives_remaining"] / MIRI_NINE_LIVES_CHANNEL_TIME,
        )
        pygame.draw.line(screen, MIRI_EFFECT_COLOR, center_tuple, target_tuple, width=4)
        pygame.draw.circle(screen, MIRI_EFFECT_COLOR, target_tuple, ACTOR_RADIUS + 14, width=4)
        pygame.draw.arc(
            screen,
            MIRI_COAT_COLOR,
            pygame.Rect(target_center.x - 42, target_center.y - 42, 84, 84),
            -math.pi / 2,
            -math.pi / 2 + math.tau * progress,
            width=6,
        )


def draw_relay_world_effects(screen, player, rift_state, camera):
    """Draw Relay charging, teleport-channel, and Overclock placeholder effects."""
    if player.get("character_id") != RELAY["id"]:
        return
    state = player["ability_state"]
    center = pygame.Vector2(player["position"] - camera)
    center_tuple = (round(center.x), round(center.y))

    if 0 < state.get("rift_boost_charge_progress", 0.0) < RELAY_RIFT_BOOST_CHARGE_TIME:
        progress = state["rift_boost_charge_progress"] / RELAY_RIFT_BOOST_CHARGE_TIME
        pygame.draw.arc(
            screen, RELAY_RIFT_COLOR,
            pygame.Rect(center.x - 38, center.y - 38, 76, 76),
            -math.pi / 2, -math.pi / 2 + math.tau * progress, width=5,
        )

    if state.get("rift_teleport_remaining", 0.0) > 0:
        progress = 1.0 - state["rift_teleport_remaining"] / RELAY_RIFT_TELEPORT_CHANNEL
        radius = round(34 + 20 * progress)
        pygame.draw.circle(screen, RELAY_RIFT_COLOR, center_tuple, radius, width=4)
        pygame.draw.circle(screen, RELAY_CORE_COLOR, center_tuple, max(5, radius // 3), width=2)

    if state.get("rift_overclock_active", False):
        pulse = 7 + round(4 * math.sin(pygame.time.get_ticks() * 0.015))
        pygame.draw.circle(screen, RELAY_RIFT_COLOR, center_tuple, ACTOR_RADIUS + 10 + pulse, width=3)


def draw_relay_teleport_selector(screen, font, player):
    """Overlay the four map quadrants while Relay chooses a teleport region."""
    if not relay_teleport_selecting(player):
        return
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((8, 9, 18, 145))
    screen.blit(overlay, (0, 0))
    mid_x = screen.get_width() // 2
    mid_y = screen.get_height() // 2
    pygame.draw.line(screen, RELAY_RIFT_COLOR, (mid_x, 0), (mid_x, screen.get_height()), width=3)
    pygame.draw.line(screen, RELAY_RIFT_COLOR, (0, mid_y), (screen.get_width(), mid_y), width=3)
    labels = [
        ("1  TOP LEFT", (mid_x // 2, mid_y // 2)),
        ("2  TOP RIGHT", (mid_x + mid_x // 2, mid_y // 2)),
        ("3  BOTTOM LEFT", (mid_x // 2, mid_y + mid_y // 2)),
        ("4  BOTTOM RIGHT", (mid_x + mid_x // 2, mid_y + mid_y // 2)),
    ]
    for label, position in labels:
        surface = font.render(label, True, TEXT_COLOR)
        screen.blit(surface, surface.get_rect(center=position))
    title = font.render("RIFT TELEPORT - CHOOSE REGION (1-4 OR CLICK)", True, RELAY_RIFT_COLOR)
    screen.blit(title, title.get_rect(center=(mid_x, 42)))


def format_ability_timer(seconds):
    """Return a short HUD label for a cooldown timer."""
    return "READY" if seconds <= 0 else f"{seconds:.1f}s"


def draw_haze_spray_mark(screen, mark, camera):
    """Draw a small neon graffiti mark at one Haze ability activation point."""
    center = pygame.Vector2(mark["position"] - camera)
    if not (-50 <= center.x <= screen.get_width() + 50 and -50 <= center.y <= screen.get_height() + 50):
        return
    fade_fraction = min(1.0, mark["remaining"] / 2.0)
    radius = 14
    forward = pygame.Vector2(math.cos(mark["rotation"]), math.sin(mark["rotation"]))
    side = pygame.Vector2(-forward.y, forward.x)
    purple = tuple(round(channel * fade_fraction) for channel in HAZE_PURPLE_COLOR)
    green = tuple(round(channel * fade_fraction) for channel in HAZE_GREEN_COLOR)
    pygame.draw.line(screen, purple, center - forward * radius, center + forward * radius, width=4)
    pygame.draw.line(screen, green, center - side * radius, center + side * radius, width=3)


def draw_haze_decoy_sprite(screen, font, decoy, camera, allied=True, alpha=255):
    """Draw Haze's Q double, including its ally-only outline and fade."""
    center = pygame.Vector2(decoy["position"] - camera)
    if not (-90 <= center.x <= screen.get_width() + 90 and -90 <= center.y <= screen.get_height() + 90):
        return

    size = 100
    sprite = pygame.Surface((size, size), pygame.SRCALPHA)
    local_center = pygame.Vector2(size / 2, size / 2)
    facing = pygame.Vector2(math.cos(decoy.get("aim_angle", 0.0)), math.sin(decoy.get("aim_angle", 0.0)))
    side = pygame.Vector2(-facing.y, facing.x)

    def rgba(color, local_alpha=255):
        return (*color, round(local_alpha * alpha / 255))

    pygame.draw.circle(sprite, rgba(HAZE_BODY_COLOR), (50, 50), ACTOR_RADIUS)
    cloak_back = local_center - facing * 15
    pygame.draw.polygon(
        sprite, rgba(HAZE_CLOAK_COLOR),
        (local_center + facing * 12, cloak_back + side * 20, local_center - facing * 29, cloak_back - side * 20),
    )
    hood = local_center + facing * 10
    pygame.draw.circle(sprite, rgba(HAZE_CLOAK_COLOR), (round(hood.x), round(hood.y)), 17)
    shadow = hood + facing * 3
    pygame.draw.circle(sprite, rgba(HAZE_SHADOW_COLOR), (round(shadow.x), round(shadow.y)), 11)
    pygame.draw.circle(sprite, rgba(HAZE_PURPLE_COLOR), (50, 50), 6)
    pygame.draw.circle(sprite, rgba(HAZE_GREEN_COLOR), (50, 50), 3)
    if allied:
        pygame.draw.circle(sprite, rgba(HAZE_GREEN_COLOR), (50, 50), ACTOR_RADIUS + 5, width=3)
    screen.blit(sprite, (round(center.x - size / 2), round(center.y - size / 2)))

    if alpha >= 220:
        bar_width = 64
        maximum = max(1.0, decoy.get("max_health", 1.0))
        health_fraction = max(0.0, min(1.0, decoy.get("health", 0.0) / maximum))
        bar_rect = pygame.Rect(round(center.x - bar_width / 2), round(center.y - 48), bar_width, 7)
        pygame.draw.rect(screen, (26, 29, 36), bar_rect)
        pygame.draw.rect(screen, HEALTH_COLOR, (bar_rect.x, bar_rect.y, round(bar_width * health_fraction), bar_rect.height))
        if allied:
            label = font.render("DECOY", True, HAZE_GREEN_COLOR)
            screen.blit(label, label.get_rect(center=(round(center.x), round(center.y + 46))))


def draw_haze_world_effects(screen, font, player, camera):
    """Draw the Haze player's graffiti and friendly-readable Q duplicate."""
    if player.get("character_id") != HAZE["id"]:
        return
    state = player.get("ability_state", {})
    for mark in state.get("spray_marks", []):
        draw_haze_spray_mark(screen, mark, camera)
    decoy = state.get("hallucination")
    if decoy is not None:
        draw_haze_decoy_sprite(screen, font, decoy, camera, allied=True, alpha=255)
    for faded in state.get("hallucination_fades", []):
        fraction = max(0.0, min(1.0, faded["fade_remaining"] / HAZE_HALLUCINATION_FADE_TIME))
        draw_haze_decoy_sprite(screen, font, faded, camera, allied=True, alpha=round(255 * fraction))


def make_haze_child_visual_actor(illusion, haze_team):
    """Build an actor-like drawing proxy for a Child's Play illusion."""
    return {
        "position": illusion["position"],
        "team": haze_team,
        "is_player": False,
        "character_id": illusion.get("source_character_id"),
        "character_name": illusion.get("source_character_name", illusion.get("source_name", "Illusion")),
        "character_class": illusion.get("source_character_class", "Soldier"),
        "max_health": max(1, illusion.get("source_max_health", ACTOR_MAX_HEALTH)),
        "health": max(1, illusion.get("source_health", ACTOR_MAX_HEALTH)),
        "alive": True,
        "downed": False,
        "eliminated": False,
        "revive_progress": 0.0,
        "aim_angle": illusion.get("aim_angle", 0.0),
        "ability_state": {},
    }


def draw_haze_enemy_perception(screen, font, local_player, actors, camera, obstacles):
    """Draw the enemy-facing versions of Hallucination and Child's Play."""
    enemy_hazes = [
        actor
        for actor in actors
        if actor.get("character_id") == HAZE["id"]
        and actor["team"] != local_player["team"]
    ]
    if not enemy_hazes:
        return

    # Q has no enemy-facing tell: an opposing player sees the decoy as Haze.
    for haze_actor in enemy_hazes:
        decoy = haze_actor.get("ability_state", {}).get("hallucination")
        if decoy is None:
            continue
        proxy = {"position": decoy["position"]}
        if is_actor_visible(local_player["position"], proxy, obstacles):
            draw_haze_decoy_sprite(
                screen, font, decoy, camera, allied=False, alpha=255
            )

    active_enemy_haze = next(
        (
            actor
            for actor in enemy_hazes
            if actor.get("ability_state", {}).get("childs_play_remaining", 0.0) > 0
        ),
        None,
    )
    if active_enemy_haze is None:
        return

    # Child's Play keeps the real map geometry but makes the world feel dreamlike.
    tint = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    tint.fill((62, 20, 78, 24))
    screen.blit(tint, (0, 0))

    illusion_list = active_enemy_haze["ability_state"].get("childs_play_illusions", {}).get(
        local_player["name"], []
    )
    for index, illusion in enumerate(illusion_list):
        proxy = make_haze_child_visual_actor(illusion, active_enemy_haze["team"])
        if not is_actor_visible(local_player["position"], proxy, obstacles):
            continue
        draw_actor(screen, font, proxy, camera)
        center = pygame.Vector2(illusion["position"] - camera)
        overlay = pygame.Surface((76, 76), pygame.SRCALPHA)
        color = HAZE_GREEN_COLOR if index % 2 == 0 else HAZE_PURPLE_COLOR
        pygame.draw.circle(overlay, (*color, 38), (38, 38), 34)
        screen.blit(overlay, (round(center.x - 38), round(center.y - 38)))


def draw_character_panel(screen, font, player, status_message):
    """Show the selected character's unique statistics, abilities, and timers."""
    character_id = player.get("character_id")
    if character_id not in (
        MALPHAS["id"],
        LONGSHOT["id"],
        VAREK["id"],
        MIRI["id"],
        RELAY["id"],
        HAZE["id"],
        SABLE["id"],
        AUREL["id"],
    ):
        return

    state = player["ability_state"]
    panel_width = 530
    panel_height = 158
    panel_x = 18
    panel_y = screen.get_height() - panel_height - 112

    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel.fill((10, 13, 18, 220))
    screen.blit(panel, (panel_x, panel_y))

    if character_id == MALPHAS["id"]:
        title_color = MALPHAS_HORN_COLOR
    elif character_id == LONGSHOT["id"]:
        title_color = LONGSHOT_VISOR_COLOR
    elif character_id == VAREK["id"]:
        title_color = VAREK_BLADE_COLOR
    elif character_id == MIRI["id"]:
        title_color = MIRI_HEAL_COLOR
    elif character_id == RELAY["id"]:
        title_color = RELAY_RIFT_COLOR
    elif character_id == HAZE["id"]:
        title_color = HAZE_GREEN_COLOR
    elif character_id == SABLE["id"]:
        title_color = SABLE_TRACK_COLOR
    else:
        title_color = AUREL_FIRE_GOLD_COLOR
    title = font.render(
        f"{player['character_name'].upper()} - {player['character_class'].upper()}",
        True,
        title_color,
    )
    screen.blit(title, (panel_x + 16, panel_y + 10))

    stats = font.render(
        f"{player['max_health']} HP | {player['move_speed']:.0f} MOVE | "
        f"{player['sprint_multiplier']:.2f}x SPRINT",
        True,
        (182, 198, 218),
    )
    screen.blit(stats, (panel_x + 16, panel_y + 34))

    if character_id == MALPHAS["id"]:
        if state["hellstep_windup"] > 0:
            signature_status = f"MARKED {state['hellstep_windup']:.1f}s"
        else:
            signature_status = format_ability_timer(state["hellstep_cooldown"])

        if state["silence_remaining"] > 0:
            class_status = f"ACTIVE {state['silence_remaining']:.1f}s"
        else:
            class_status = format_ability_timer(state["silence_cooldown"])

        if state["bloodlust_remaining"] > 0:
            ultimate_status = f"ACTIVE {state['bloodlust_remaining']:.1f}s"
        elif state["bloodlust_used"]:
            ultimate_status = "USED THIS ROUND"
        else:
            ultimate_status = "READY"

        lines = [
            f"Q  HELLSTEP  - {signature_status}",
            f"C  SILENCE   - {class_status}",
            f"X  BLOODLUST - {ultimate_status}",
        ]
        status_color = MALPHAS_GLOW_COLOR
    elif character_id == LONGSHOT["id"]:
        signature_status = format_ability_timer(state["resonance_cooldown"])
        if state["track_remaining"] > 0:
            class_status = f"ACTIVE {state['track_remaining']:.1f}s"
        else:
            class_status = format_ability_timer(state["track_cooldown"])

        if state["dead_line_active"]:
            if state["dead_line_recovery"] > 0:
                ultimate_status = (
                    f"{state['dead_line_shots_remaining']} SHOT(S) | "
                    f"RECOVER {state['dead_line_recovery']:.1f}s"
                )
            elif state["dead_line_charge"] > 0:
                ultimate_status = (
                    f"{state['dead_line_shots_remaining']} SHOT(S) | "
                    f"AIM {state['dead_line_charge']:.1f}/{LONGSHOT_DEAD_LINE_AIM_TIME:.1f}s"
                )
            else:
                ultimate_status = f"{state['dead_line_shots_remaining']} SHOT(S) READY"
        elif state["dead_line_used"]:
            ultimate_status = "USED THIS ROUND"
        else:
            ultimate_status = "READY"

        lines = [
            f"Q  RESONANCE SWEEP - {signature_status}",
            f"C  TRACK           - {class_status}",
            f"X  DEAD LINE       - {ultimate_status}",
        ]
        status_color = LONGSHOT_VISOR_COLOR
    elif character_id == VAREK["id"]:
        if state["oni_blade_remaining"] > 0:
            signature_status = f"ACTIVE {state['oni_blade_remaining']:.1f}s"
        elif state["fury_remaining"] > 0:
            signature_status = "DRAWN BY FURY"
        else:
            signature_status = format_ability_timer(state["oni_blade_cooldown"])

        class_status = format_ability_timer(state["breach_cooldown"])
        if state["fury_remaining"] > 0:
            ultimate_status = f"ACTIVE {state['fury_remaining']:.1f}s"
        elif state["fury_used"]:
            ultimate_status = "USED THIS ROUND"
        else:
            ultimate_status = "READY"

        lines = [
            f"Q  ONI BLADE      - {signature_status}",
            f"C  BREACH CHARGE  - {class_status}",
            f"X  UNBOUND FURY   - {ultimate_status}",
        ]
        status_color = VAREK_BLADE_COLOR
    elif character_id == MIRI["id"]:
        if state["feline_lunge_remaining"] > 0:
            signature_status = f"ACTIVE {state['feline_lunge_remaining']:.1f}s"
        else:
            signature_status = format_ability_timer(state["feline_lunge_cooldown"])

        if state["field_treatment_remaining"] > 0:
            class_status = f"CASTING {state['field_treatment_remaining']:.1f}s"
        else:
            class_status = format_ability_timer(state["field_treatment_cooldown"])

        if state["nine_lives_remaining"] > 0:
            ultimate_status = f"CHANNEL {state['nine_lives_remaining']:.1f}s"
        elif state["nine_lives_used"]:
            ultimate_status = "USED THIS ROUND"
        else:
            ultimate_status = "READY"

        lines = [
            f"Q  FELINE LUNGE    - {signature_status}",
            f"C  FIELD TREATMENT - {class_status}",
            f"X  NINE LIVES      - {ultimate_status}",
        ]
        status_color = MIRI_HEAL_COLOR
    elif character_id == RELAY["id"]:
        if state["rift_boost_bullets_remaining"] > 0:
            signature_status = f"{state['rift_boost_bullets_remaining']} PROJECTILES"
        elif state["rift_boost_cooldown"] > 0:
            signature_status = f"COOLDOWN {state['rift_boost_cooldown']:.1f}s"
        elif state["rift_boost_charged"]:
            signature_status = "READY"
        elif state["rift_boost_charge_progress"] > 0:
            signature_status = (
                f"CHARGING {state['rift_boost_charge_progress']:.1f}/"
                f"{RELAY_RIFT_BOOST_CHARGE_TIME:.1f}s"
            )
        else:
            signature_status = "NEEDS RIFT CHARGE"

        if state["rift_teleport_selecting"]:
            class_status = "CHOOSE 1-4"
        elif state["rift_teleport_remaining"] > 0:
            class_status = f"CHANNEL {state['rift_teleport_remaining']:.1f}s"
        else:
            class_status = format_ability_timer(state["rift_teleport_cooldown"])

        if state["rift_overclock_active"]:
            ultimate_status = "ACTIVE - HOLD 1.5x"
        elif state["rift_overclock_used"]:
            ultimate_status = "USED THIS ROUND"
        else:
            ultimate_status = "READY AT OWNED RIFT"

        lines = [
            f"Q  RIFT BOOST     - {signature_status}",
            f"C  RIFT TELEPORT  - {class_status}",
            f"X  RIFT OVERCLOCK - {ultimate_status}",
        ]
        status_color = RELAY_RIFT_COLOR
    elif character_id == HAZE["id"]:
        decoy = state.get("hallucination")
        if decoy is not None:
            signature_status = f"ACTIVE {decoy['remaining']:.1f}s | {decoy['health']:.0f} HP"
        else:
            signature_status = format_ability_timer(state["hallucination_cooldown"])

        if state["silence_remaining"] > 0:
            class_status = f"ACTIVE {state['silence_remaining']:.1f}s"
        else:
            class_status = format_ability_timer(state["silence_cooldown"])

        if state["childs_play_remaining"] > 0:
            ultimate_status = f"ACTIVE {state['childs_play_remaining']:.1f}s"
        elif state["childs_play_used"]:
            ultimate_status = "USED THIS ROUND"
        else:
            ultimate_status = "READY"

        lines = [
            f"Q  HALLUCINATION - {signature_status}",
            f"C  SILENCE       - {class_status}",
            f"X  CHILD'S PLAY  - {ultimate_status}",
        ]
        status_color = HAZE_GREEN_COLOR
    elif character_id == SABLE["id"]:
        if state["scent_remaining"] > 0:
            signature_status = f"ACTIVE {state['scent_remaining']:.1f}s | {len(state['scent_targets'])} PREY"
        else:
            signature_status = format_ability_timer(state["scent_cooldown"])
        if state["track_remaining"] > 0:
            class_status = f"ACTIVE {state['track_remaining']:.1f}s"
        else:
            class_status = format_ability_timer(state["track_cooldown"])
        if state["wild_hunt_remaining"] > 0:
            ultimate_status = f"ACTIVE {state['wild_hunt_remaining']:.1f}s"
        elif state["wild_hunt_used"]:
            ultimate_status = "USED THIS ROUND"
        else:
            ultimate_status = "READY"
        lines = [
            f"Q  SCENT OF BLOOD - {signature_status}",
            f"C  TRACK          - {class_status}",
            f"X  WILD HUNT      - {ultimate_status}",
        ]
        status_color = SABLE_TRACK_COLOR
    else:
        signature_status = format_ability_timer(state["cinderbolt_cooldown"])
        class_status = format_ability_timer(state["breach_cooldown"])
        if state["inferno_charge_remaining"] > 0:
            ultimate_status = f"CHARGING {state['inferno_charge_remaining']:.1f}s"
        elif state["inferno_after_remaining"] > 0:
            ultimate_status = f"INFERNO {state['inferno_after_remaining']:.1f}s"
        elif state["inferno_used"]:
            ultimate_status = "USED THIS ROUND"
        else:
            ultimate_status = "READY"
        lines = [
            f"Q  CINDERBOLT        - {signature_status}",
            f"C  BREACH CHARGE     - {class_status}",
            f"X  EXPLOSIVE INFERNO - {ultimate_status}",
        ]
        status_color = AUREL_FIRE_GOLD_COLOR

    for index, line in enumerate(lines):
        rendered = font.render(line, True, TEXT_COLOR)
        screen.blit(rendered, (panel_x + 16, panel_y + 62 + index * 23))

    if status_message:
        status = font.render(status_message, True, status_color)
        screen.blit(status, (panel_x + 16, panel_y + 132))


def draw_knife(screen, player, camera, aim_angle, animation_timer):
    """Draw the equipped knife and visibly sweep it during an attack."""
    center = pygame.Vector2(player["position"] - camera)

    if animation_timer > 0:
        swing_progress = 1.0 - min(
            1.0,
            animation_timer / KNIFE["attack_animation_time"],
        )
        angle_offset = math.radians(-55 + 110 * swing_progress)
    else:
        angle_offset = math.radians(-15)

    knife_angle = aim_angle + angle_offset
    forward = pygame.Vector2(
        math.cos(knife_angle),
        math.sin(knife_angle),
    )
    sideways = pygame.Vector2(-forward.y, forward.x)

    handle_start = center + forward * 20
    guard_center = center + forward * 35
    blade_base = center + forward * 39
    blade_tip = center + forward * 67

    pygame.draw.line(
        screen,
        (48, 36, 28),
        handle_start,
        guard_center,
        width=8,
    )
    pygame.draw.line(
        screen,
        (221, 174, 78),
        guard_center - sideways * 8,
        guard_center + sideways * 8,
        width=4,
    )
    pygame.draw.polygon(
        screen,
        (218, 226, 235),
        (
            blade_base - sideways * 4,
            blade_base + sideways * 4,
            blade_tip,
        ),
    )
    pygame.draw.line(
        screen,
        (255, 255, 255),
        blade_base - sideways * 2,
        blade_tip,
        width=2,
    )


def get_rift_color(rift_state):
    """Return the active Rift color for its current control state."""
    if rift_state["contested"]:
        return RIFT_CONTESTED_COLOR
    if rift_state["owner"] == "blue":
        return RIFT_BLUE_COLOR
    if rift_state["owner"] == "red":
        return RIFT_RED_COLOR
    if rift_state["capture_team"] == "blue":
        return RIFT_BLUE_COLOR
    if rift_state["capture_team"] == "red":
        return RIFT_RED_COLOR
    return RIFT_NEUTRAL_COLOR


def get_screen_edge_indicator(screen, target_position, margin=70):
    """Clamp an off-screen target toward the nearest readable screen edge."""
    screen_rect = screen.get_rect().inflate(-margin * 2, -margin * 2)
    if screen_rect.collidepoint(target_position):
        return pygame.Vector2(target_position), False

    center = pygame.Vector2(screen.get_rect().center)
    direction = pygame.Vector2(target_position) - center
    if direction.length_squared() == 0:
        return center, False

    scale_x = (
        (screen_rect.right - center.x) / direction.x
        if direction.x > 0
        else (screen_rect.left - center.x) / direction.x
        if direction.x < 0
        else float("inf")
    )
    scale_y = (
        (screen_rect.bottom - center.y) / direction.y
        if direction.y > 0
        else (screen_rect.top - center.y) / direction.y
        if direction.y < 0
        else float("inf")
    )
    scale = min(scale_x, scale_y)
    return center + direction * scale, True


def draw_rift(screen, font, rift_state, player_position, camera):
    """Draw the active Rift or an edge marker pointing toward it."""
    world_position = rift_state["position"]
    screen_position = world_position - camera
    color = get_rift_color(rift_state)
    indicator_position, is_offscreen = get_screen_edge_indicator(
        screen,
        screen_position,
    )

    if is_offscreen:
        screen_center = pygame.Vector2(screen.get_rect().center)
        direction = screen_position - screen_center
        if direction.length_squared() > 0:
            direction = direction.normalize()
        side = pygame.Vector2(-direction.y, direction.x)
        tip = indicator_position + direction * 18
        left = indicator_position - direction * 12 + side * 12
        right = indicator_position - direction * 12 - side * 12
        pygame.draw.polygon(screen, color, (tip, left, right))
        distance = round(player_position.distance_to(world_position))
        label = font.render(
            f"RIFT {rift_state['site_name']}  {distance}",
            True,
            color,
        )
        label_rect = label.get_rect(
            center=(
                round(indicator_position.x),
                round(indicator_position.y + 30),
            )
        )
        screen.blit(label, label_rect)
        return

    center = (round(screen_position.x), round(screen_position.y))
    pulse = 5 + round(4 * math.sin(pygame.time.get_ticks() * 0.006))
    pygame.draw.circle(
        screen,
        color,
        center,
        RIFT_RADIUS,
        width=4,
    )
    pygame.draw.circle(
        screen,
        color,
        center,
        38 + pulse,
        width=5,
    )
    pygame.draw.circle(screen, (22, 18, 35), center, 24)
    pygame.draw.polygon(
        screen,
        color,
        (
            (center[0], center[1] - 22),
            (center[0] + 18, center[1]),
            (center[0], center[1] + 22),
            (center[0] - 18, center[1]),
        ),
    )

    if rift_state.get("overclock_team") is not None:
        tick = pygame.time.get_ticks() * 0.014
        for bolt_index in range(7):
            angle = tick + bolt_index * (math.tau / 7)
            direction = pygame.Vector2(math.cos(angle), math.sin(angle))
            side = pygame.Vector2(-direction.y, direction.x)
            start = pygame.Vector2(center) + direction * 48
            middle = pygame.Vector2(center) + direction * (78 + 7 * math.sin(tick * 1.7 + bolt_index)) + side * 9
            end = pygame.Vector2(center) + direction * (RIFT_RADIUS - 8)
            pygame.draw.lines(screen, RELAY_RIFT_COLOR, False, (start, middle, end), width=3)

    label = font.render(
        f"RIFT {rift_state['site_name']}",
        True,
        color,
    )
    screen.blit(
        label,
        label.get_rect(center=(center[0], center[1] - RIFT_RADIUS - 22)),
    )

    bar_width = 180
    bar_height = 12
    bar_x = center[0] - bar_width // 2
    bar_y = center[1] + RIFT_RADIUS + 16
    if rift_state["capture_team"] is not None:
        progress = min(
            1.0,
            rift_state["capture_progress"] / RIFT_CAPTURE_TIME,
        )
    elif rift_state["owner"] is not None:
        progress = min(
            1.0,
            rift_state["hold_progress"][rift_state["owner"]]
            / RIFT_HOLD_TIME_TO_WIN,
        )
    else:
        progress = 0.0

    pygame.draw.rect(
        screen,
        (22, 26, 34),
        (bar_x, bar_y, bar_width, bar_height),
    )
    pygame.draw.rect(
        screen,
        color,
        (bar_x, bar_y, round(bar_width * progress), bar_height),
    )
    pygame.draw.rect(
        screen,
        TEXT_COLOR,
        (bar_x, bar_y, bar_width, bar_height),
        width=2,
    )
    if rift_state.get("overclock_team") is not None:
        overclock_text = font.render("OVERCLOCK 1.5x", True, RELAY_RIFT_COLOR)
        screen.blit(overclock_text, overclock_text.get_rect(center=(center[0], bar_y + 30)))


def draw_rift_intel(screen, font, actors, camera, rift_state):
    """Reveal enemy positions and health during a blue Rift intel pulse."""
    if (
        rift_state["owner"] != "blue"
        or rift_state["intel_remaining"] <= 0
    ):
        return

    for actor in actors:
        if actor["team"] != "red" or actor["eliminated"]:
            continue

        screen_position = actor["position"] - camera
        marker_position, is_offscreen = get_screen_edge_indicator(
            screen,
            screen_position,
            margin=55,
        )
        center = (round(marker_position.x), round(marker_position.y))
        marker_radius = 12 if is_offscreen else ACTOR_RADIUS + 8
        pygame.draw.circle(
            screen,
            RIFT_RED_COLOR,
            center,
            marker_radius,
            width=3,
        )
        pygame.draw.line(
            screen,
            RIFT_RED_COLOR,
            (center[0] - 7, center[1]),
            (center[0] + 7, center[1]),
            width=2,
        )
        pygame.draw.line(
            screen,
            RIFT_RED_COLOR,
            (center[0], center[1] - 7),
            (center[0], center[1] + 7),
            width=2,
        )
        status = "DOWN" if actor["downed"] else f"{actor['health']} HP"
        label = font.render(status, True, RIFT_RED_COLOR)
        screen.blit(
            label,
            label.get_rect(center=(center[0], center[1] - marker_radius - 12)),
        )


def make_vision_render_buffers(screen_size, obstacle_rects):
    """Allocate masks for permanent and potentially destructible obstacles."""
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
                    max(1, math.ceil(obstacle.width * VISION_MASK_SCALE) + 2),
                    max(1, math.ceil(obstacle.height * VISION_MASK_SCALE) + 2),
                ),
                pygame.SRCALPHA,
            )
            for obstacle in obstacle_rects
        ],
        "wall_detail_layers": [
            pygame.Surface(
                (obstacle.width, obstacle.height),
                pygame.SRCALPHA,
            )
            for obstacle in obstacle_rects
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
    active_obstacles,
    all_obstacle_indices,
    camera,
    buffers,
):
    """Build whole-section visibility for every active blocking object."""
    wall_mask = buffers["wall_mask"]
    wall_mask_low = buffers["wall_mask_low"]
    wall_occlusion = buffers["wall_occlusion_low"]
    wall_piece_masks = buffers["wall_piece_masks"]
    mask_rect = wall_mask_low.get_rect()
    wall_mask_low.fill((255, 255, 255, 0))
    wall_occlusion.fill((0, 0, 0, 0))

    ordered_wall_indices = sorted(
        range(len(active_obstacles)),
        key=lambda active_index: get_wall_distance_squared(
            player_position,
            active_obstacles[active_index],
        ),
    )

    for active_index in ordered_wall_indices:
        wall = active_obstacles[active_index]
        piece_index = all_obstacle_indices[id(wall)]
        wall_piece_mask = wall_piece_masks[piece_index]
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
    active_obstacles,
    all_obstacle_indices,
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
            active_obstacles,
            all_obstacle_indices,
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


def draw_visible_destructible_details(
    screen,
    destructible_objects,
    bullet_marks,
    camera,
    visibility_mask,
    detail_layers,
    first_layer_index,
):
    """Restore the visible material colors of active crates and doors."""
    for object_index, destructible in enumerate(destructible_objects):
        if destructible["destroyed"]:
            continue

        rectangle = destructible["rect"]
        destination = (
            round(rectangle.left - camera.x),
            round(rectangle.top - camera.y),
        )
        destination_rect = pygame.Rect(
            destination,
            (rectangle.width, rectangle.height),
        )
        if not destination_rect.colliderect(screen.get_rect()):
            continue

        detail_layer = detail_layers[first_layer_index + object_index]
        detail_layer.fill((0, 0, 0, 0))
        draw_destructible_object(
            detail_layer,
            destructible,
            pygame.Vector2(rectangle.topleft),
            hidden=False,
        )
        draw_bullet_marks(
            detail_layer,
            bullet_marks,
            pygame.Vector2(rectangle.topleft),
            only_wall=rectangle,
        )
        blit_surface_through_mask(
            screen,
            detail_layer,
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
        if bullet.get("rift_boosted", False):
            bullet_color = RELAY_BOOST_BULLET_COLOR
        else:
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
    """Show normal revive or Miri resurrection prompts when an ally is in reach."""
    if not actor_can_fight(player):
        return

    downed_ally = find_nearest_actor(
        player,
        actors,
        team="blue",
        downed_only=True,
    )
    if (
        downed_ally is not None
        and player["position"].distance_to(downed_ally["position"]) <= REVIVE_RANGE
        and has_line_of_sight(
            player["position"],
            downed_ally["position"],
            walls,
        )
    ):
        center = downed_ally["position"] - camera
        prompt = font.render("HOLD E TO REVIVE", True, TEXT_COLOR)
        background = prompt.get_rect(center=(round(center.x), round(center.y + 55)))
        background.inflate_ip(18, 10)
        pygame.draw.rect(screen, (10, 13, 18), background, border_radius=5)
        screen.blit(prompt, prompt.get_rect(center=background.center))
        return

    if player.get("character_id") != MIRI["id"]:
        return
    state = player.get("ability_state", {})
    if state.get("nine_lives_used", False) or state.get("nine_lives_remaining", 0.0) > 0:
        return

    eliminated_ally = find_miri_nine_lives_target(player, actors, walls)
    if eliminated_ally is None:
        return

    center = eliminated_ally["position"] - camera
    prompt = font.render("PRESS X FOR NINE LIVES", True, MIRI_HEAL_COLOR)
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


def draw_stamina_panel(
    screen, font, stamina, sprinting, sprint_exhausted, max_stamina
):
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
    stamina_fraction = stamina / max_stamina

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
    max_stamina,
):
    """Show the values that matter while testing movement."""
    if active_weapon["fire_mode"] == "melee":
        weapon_detail = (
            f"Knife: {active_weapon['damage']} damage | "
            f"{active_weapon['melee_range']} pixel reach"
        )
    else:
        weapon_detail = (
            f"{active_weapon['name']} spread: {spread_percent * 100:.0f}%"
        )

    lines = [
        "RIFT HUNT 0.8 - CHARACTERS",
        "WASD Move | SHIFT Run | LMB Attack | Q Signature | C Class | X Ultimate | E Revive | ESC Pause",
        f"Position: ({player_position.x:.1f}, {player_position.y:.1f})",
        f"Facing: {math.degrees(aim_angle):.1f} degrees",
        f"Movement: {movement_state}",
        f"Current speed: {actual_speed:.0f} pixels/second",
        weapon_detail,
        f"Stamina: {stamina:.0f} / {max_stamina:.0f}",
        f"FPS: {current_fps:.0f} / target {FPS}",
    ]

    panel = pygame.Surface((700, 253), pygame.SRCALPHA)
    panel.fill((10, 13, 18, 205))
    screen.blit(panel, (18, 18))

    for index, line in enumerate(lines):
        rendered_text = font.render(line, True, TEXT_COLOR)
        screen.blit(rendered_text, (34, 32 + index * 25))


def draw_dropped_weapons(screen, font, dropped_weapons, player, obstacles, camera):
    """Draw nearby shared weapons only when the local player can actually see them."""
    for dropped_weapon in dropped_weapons:
        if dropped_weapon["team"] != player["team"]:
            continue

        world_position = dropped_weapon["position"]
        distance = player["position"].distance_to(world_position)
        if distance > WEAPON_SHARE_DRAW_DISTANCE:
            continue
        if not has_line_of_sight(player["position"], world_position, obstacles):
            continue

        screen_position = world_position - camera
        center = (round(screen_position.x), round(screen_position.y))
        if not screen.get_rect().inflate(100, 100).collidepoint(center):
            continue

        weapon = WEAPONS[dropped_weapon["weapon_index"]]
        pygame.draw.circle(
            screen,
            (22, 26, 34),
            center,
            DROPPED_WEAPON_RADIUS + 5,
        )
        pygame.draw.circle(
            screen,
            BULLET_COLOR,
            center,
            DROPPED_WEAPON_RADIUS,
            width=3,
        )
        pygame.draw.line(
            screen,
            BULLET_COLOR,
            (center[0] - 10, center[1] + 6),
            (center[0] + 10, center[1] - 6),
            width=5,
        )

        if distance <= WEAPON_SHARE_RANGE:
            label_text = f"F - PICK UP {weapon['name'].upper()}"
        else:
            label_text = weapon["name"].upper()
        label = font.render(label_text, True, TEXT_COLOR)
        label_rect = label.get_rect(center=(center[0], center[1] - 36))
        background = label_rect.inflate(14, 8)
        pygame.draw.rect(screen, (10, 13, 18), background, border_radius=4)
        screen.blit(label, label_rect)


def draw_weapon_panel(
    screen,
    regular_font,
    large_font,
    active_weapon,
    weapon_state,
    player,
):
    """Display ammunition and the local player's combat condition."""
    panel_width = 470
    panel_height = 252
    panel_x = screen.get_width() - panel_width - 18
    panel_y = screen.get_height() - panel_height - 18

    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel.fill((10, 13, 18, 220))
    screen.blit(panel, (panel_x, panel_y))

    if active_weapon["fire_mode"] == "automatic":
        fire_mode_label = "AUTO"
    elif active_weapon["fire_mode"] == "melee":
        fire_mode_label = "MELEE"
    else:
        fire_mode_label = "SEMI"
    weapon_name = regular_font.render(
        f"SLOT {active_weapon['slot']}: {active_weapon['name'].upper()} [{fire_mode_label}]",
        True,
        TEXT_COLOR,
    )
    screen.blit(weapon_name, (panel_x + 18, panel_y + 14))

    if active_weapon["fire_mode"] == "melee":
        ammunition_label = "MELEE"
    else:
        ammunition_label = (
            f"{weapon_state['magazine_ammo']} / "
            f"{weapon_state['reserve_ammo']}"
        )
    ammunition = large_font.render(ammunition_label, True, BULLET_COLOR)
    screen.blit(ammunition, (panel_x + 18, panel_y + 38))

    if active_weapon["fire_mode"] == "melee":
        weapon_status = (
            "RECOVERING"
            if weapon_state["shot_cooldown"] > 0
            else "READY"
        )
    elif weapon_state["reloading"]:
        weapon_status = f"RELOADING: {weapon_state['reload_timer']:.1f}s"
    elif weapon_state["magazine_ammo"] == 0:
        weapon_status = "OUT OF AMMO"
    else:
        weapon_status = "READY"

    status_text = regular_font.render(weapon_status, True, TEXT_COLOR)
    screen.blit(status_text, (panel_x + 18, panel_y + 87))

    owned_slots = "   ".join(
        f"{WEAPONS[index]['slot']}: {WEAPONS[index]['name']}"
        for index in player["owned_weapon_indices"]
    )
    slots_text = regular_font.render(
        f"Owned: {owned_slots}",
        True,
        (166, 180, 198),
    )
    screen.blit(slots_text, (panel_x + 18, panel_y + 113))

    if player["eliminated"]:
        player_status = "YOU: ELIMINATED"
    elif player["downed"]:
        player_status = "YOU: DOWNED - WAIT FOR AN ALLY"
    else:
        player_status = (
            f"Health: {round(player['health'])} / {player['max_health']}"
        )

    player_text = regular_font.render(player_status, True, TEXT_COLOR)
    life_text = regular_font.render(
        f"Downs used: {player['times_downed']} / 2",
        True,
        TEXT_COLOR,
    )
    credits_text = regular_font.render(
        f"Credits: {player['credits']} / {MAX_CREDITS}",
        True,
        BULLET_COLOR,
    )
    share_text = regular_font.render(
        "G: Drop bought weapon   F: Pick up shared weapon",
        True,
        (166, 180, 198),
    )
    screen.blit(player_text, (panel_x + 18, panel_y + 142))
    screen.blit(life_text, (panel_x + 18, panel_y + 168))
    screen.blit(credits_text, (panel_x + 18, panel_y + 194))
    screen.blit(share_text, (panel_x + 18, panel_y + 220))


def count_team_states(actors, team):
    """Return standing, downed, and eliminated counts for one team."""
    team_actors = [actor for actor in actors if actor["team"] == team]
    standing = sum(actor_can_fight(actor) for actor in team_actors)
    downed = sum(actor["downed"] for actor in team_actors)
    eliminated = sum(actor["eliminated"] for actor in team_actors)
    return standing, downed, eliminated


def draw_match_panel(
    screen,
    font,
    scores,
    round_number,
    actors,
    rift_state,
    team_rift_energy,
):
    """Show the score, team conditions, active Rift, and shared team resource."""
    blue_state = count_team_states(actors, "blue")
    red_state = count_team_states(actors, "red")
    if rift_state["contested"]:
        rift_status = "CONTESTED"
    elif rift_state["capture_team"] is not None:
        capture_percent = round(
            100 * rift_state["capture_progress"] / RIFT_CAPTURE_TIME
        )
        rift_status = (
            f"{rift_state['capture_team'].upper()} CAPTURING {capture_percent}%"
        )
    elif rift_state["owner"] is not None:
        owner = rift_state["owner"]
        rift_status = (
            f"{owner.upper()} CONTROL "
            f"{rift_state['hold_progress'][owner]:.1f}/"
            f"{RIFT_HOLD_TIME_TO_WIN:.0f}s"
        )
    else:
        rift_status = "NEUTRAL"

    if rift_state["owner"] == "blue":
        if rift_state["intel_remaining"] > 0:
            intel_status = (
                f"INTEL ACTIVE {rift_state['intel_remaining']:.1f}s"
            )
        else:
            intel_status = (
                f"NEXT INTEL IN "
                f"{max(0.0, RIFT_INTEL_INTERVAL - rift_state['intel_timer']):.1f}s"
            )
    elif rift_state["owner"] == "red":
        intel_status = "RED HAS INTEL ADVANTAGE"
    else:
        intel_status = "CAPTURE FOR ENEMY INTEL"

    lines = [
        f"BLUE  {scores['blue']}  -  {scores['red']}  RED",
        f"ROUND {round_number}    FIRST TO {ROUNDS_TO_WIN}",
        f"Up {blue_state[0]}-{red_state[0]}   "
        f"Down {blue_state[1]}-{red_state[1]}   "
        f"Out {blue_state[2]}-{red_state[2]}",
        f"RIFT {rift_state['site_name']}: {rift_status}",
        intel_status,
        f"TEAM RIFT ENERGY: {team_rift_energy['blue']} / {MAX_TEAM_RIFT_ENERGY}",
    ]

    panel = pygame.Surface((500, 167), pygame.SRCALPHA)
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


def get_main_menu_buttons(screen):
    """Return the clickable controls for the title screen."""
    center_x = screen.get_width() // 2
    button_width = 330
    button_height = 64
    return [
        UIButton(
            (center_x - button_width // 2, screen.get_height() // 2 + 65,
             button_width, button_height),
            "PLAY",
            "play",
        ),
        UIButton(
            (center_x - button_width // 2, screen.get_height() // 2 + 145,
             button_width, button_height),
            "QUIT",
            "quit",
        ),
    ]


def get_pause_menu_buttons(screen):
    """Return the clickable controls shown while the match is paused."""
    center_x = screen.get_width() // 2
    button_width = 330
    button_height = 58
    start_y = screen.get_height() // 2 - 10
    return [
        UIButton(
            (center_x - button_width // 2, start_y, button_width, button_height),
            "RESUME",
            "resume",
        ),
        UIButton(
            (center_x - button_width // 2, start_y + 72, button_width, button_height),
            "MAIN MENU",
            "main_menu",
        ),
        UIButton(
            (center_x - button_width // 2, start_y + 144, button_width, button_height),
            "QUIT",
            "quit",
        ),
    ]


def get_character_card_rects(screen):
    """Return evenly spaced character cards that still fit as the roster grows."""
    gap = 20
    card_count = len(CHARACTER_ROSTER)
    available_width = max(900, screen.get_width() - 70)
    card_width = min(260, max(190, (available_width - gap * (card_count - 1)) // card_count))
    card_height = 360
    total_width = card_width * card_count + gap * (card_count - 1)
    left = screen.get_width() // 2 - total_width // 2
    top = screen.get_height() // 2 - 155
    return [
        pygame.Rect(left + index * (card_width + gap), top, card_width, card_height)
        for index in range(card_count)
    ]


def handle_character_select_click(match_state, player, click_position):
    """Select an implemented character card and report locked choices."""
    for character, rectangle in zip(CHARACTER_ROSTER, get_character_card_rects(pygame.display.get_surface())):
        if not rectangle.collidepoint(click_position):
            continue
        if not character.get("implemented", False):
            match_state["character_status"] = (
                f"{character['name'].upper()} IS NOT IMPLEMENTED YET"
            )
            return False
        selected = get_playable_character(character["id"])
        if selected is None:
            return False
        apply_character_to_actor(player, selected)
        match_state["selected_character_id"] = selected["id"]
        match_state["character_status"] = f"{selected['name'].upper()} SELECTED"
        return True
    return False


def draw_main_menu(screen, regular_font, large_font, title_font):
    """Draw the title screen using the reusable button system."""
    screen.fill((14, 18, 26))
    center = (screen.get_width() // 2, screen.get_height() // 2 - 145)

    # Temporary Rift emblem behind the logo.
    pulse = 14 + round(8 * math.sin(pygame.time.get_ticks() * 0.0025))
    pygame.draw.circle(screen, (31, 44, 61), center, 116 + pulse, width=3)
    pygame.draw.circle(screen, RIFT_BLUE_COLOR, center, 74 + pulse // 2, width=4)
    pygame.draw.circle(screen, (22, 18, 35), center, 44)
    pygame.draw.polygon(
        screen,
        RIFT_NEUTRAL_COLOR,
        (
            (center[0], center[1] - 38),
            (center[0] + 31, center[1]),
            (center[0], center[1] + 38),
            (center[0] - 31, center[1]),
        ),
    )

    title = title_font.render("RIFTBOUND", True, TEXT_COLOR)
    subtitle = large_font.render("RIFT HUNT", True, RIFT_BLUE_COLOR)
    screen.blit(title, title.get_rect(center=(center[0], center[1] - 175)))
    screen.blit(subtitle, subtitle.get_rect(center=(center[0], center[1] + 150)))

    mouse_position = pygame.mouse.get_pos()
    for button in get_main_menu_buttons(screen):
        button.draw(screen, large_font, mouse_position)

    version = regular_font.render(
        "Version 0.8 - Characters Prototype", True, (154, 167, 184)
    )
    screen.blit(
        version,
        version.get_rect(center=(screen.get_width() // 2, screen.get_height() - 42)),
    )


def draw_pause_menu(screen, regular_font, large_font, title_font):
    """Darken the game and draw pause controls without advancing simulation."""
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((4, 6, 10, 205))
    screen.blit(overlay, (0, 0))

    title = title_font.render("PAUSED", True, TEXT_COLOR)
    screen.blit(
        title,
        title.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 150)),
    )
    subtitle = regular_font.render(
        "Press ESC to resume", True, (176, 190, 207)
    )
    screen.blit(
        subtitle,
        subtitle.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 92)),
    )

    mouse_position = pygame.mouse.get_pos()
    for button in get_pause_menu_buttons(screen):
        button.draw(screen, large_font, mouse_position)


def draw_character_select(screen, regular_font, large_font, match_state):
    """Draw the timed character-selection phase before the weapon shop."""
    if match_state["phase"] != "character_select":
        return

    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((7, 9, 14, 232))
    screen.blit(overlay, (0, 0))

    heading = large_font.render("CHOOSE YOUR CHARACTER", True, TEXT_COLOR)
    screen.blit(
        heading,
        heading.get_rect(center=(screen.get_width() // 2, 76)),
    )
    timer = large_font.render(
        f"{max(0.0, match_state['timer']):.1f}s",
        True,
        BULLET_COLOR,
    )
    screen.blit(timer, timer.get_rect(center=(screen.get_width() // 2, 125)))

    selected_id = match_state.get("selected_character_id")
    mouse_position = pygame.mouse.get_pos()
    for character, rectangle in zip(CHARACTER_ROSTER, get_character_card_rects(screen)):
        implemented = character.get("implemented", False)
        selected = character["id"] == selected_id
        hovered = rectangle.collidepoint(mouse_position) and implemented

        if selected:
            fill = (42, 72, 91)
            edge = RIFT_BLUE_COLOR
        elif hovered:
            fill = (38, 48, 62)
            edge = PLAYER_EDGE_COLOR
        elif implemented:
            fill = (25, 31, 41)
            edge = (100, 120, 145)
        else:
            fill = (29, 31, 37)
            edge = (68, 72, 82)

        pygame.draw.rect(screen, fill, rectangle, border_radius=12)
        pygame.draw.rect(screen, edge, rectangle, width=3, border_radius=12)

        portrait_center = (rectangle.centerx, rectangle.top + 104)
        if character["id"] == "malphas":
            pygame.draw.circle(screen, MALPHAS_BODY_COLOR, portrait_center, 54)
            pygame.draw.polygon(
                screen,
                MALPHAS_HORN_COLOR,
                (
                    (portrait_center[0] - 42, portrait_center[1] - 32),
                    (portrait_center[0] - 64, portrait_center[1] - 72),
                    (portrait_center[0] - 18, portrait_center[1] - 48),
                ),
            )
            pygame.draw.polygon(
                screen,
                MALPHAS_HORN_COLOR,
                (
                    (portrait_center[0] + 42, portrait_center[1] - 32),
                    (portrait_center[0] + 64, portrait_center[1] - 72),
                    (portrait_center[0] + 18, portrait_center[1] - 48),
                ),
            )
            pygame.draw.circle(screen, MALPHAS_GLOW_COLOR, portrait_center, 16)
        elif character["id"] == "longshot":
            pygame.draw.circle(screen, LONGSHOT_BODY_COLOR, portrait_center, 52)
            pygame.draw.circle(screen, LONGSHOT_ARMOR_COLOR, portrait_center, 52, width=7)
            pygame.draw.line(
                screen,
                LONGSHOT_VISOR_COLOR,
                (portrait_center[0] - 20, portrait_center[1] - 10),
                (portrait_center[0] + 20, portrait_center[1] - 10),
                width=8,
            )
            pygame.draw.line(
                screen,
                LONGSHOT_RIFLE_COLOR,
                (portrait_center[0] - 50, portrait_center[1] + 42),
                (portrait_center[0] + 58, portrait_center[1] - 48),
                width=10,
            )
        elif character["id"] == "varek":
            pygame.draw.circle(screen, VAREK_BODY_COLOR, portrait_center, 52)
            pygame.draw.circle(screen, VAREK_ARMOR_COLOR, portrait_center, 52, width=8)
            pygame.draw.rect(
                screen,
                VAREK_MASK_COLOR,
                (portrait_center[0] - 18, portrait_center[1] - 22, 36, 28),
                border_radius=8,
            )
            pygame.draw.line(
                screen,
                VAREK_BLADE_COLOR,
                (portrait_center[0] - 46, portrait_center[1] + 48),
                (portrait_center[0] + 52, portrait_center[1] - 52),
                width=9,
            )
        elif character["id"] == "miri":
            pygame.draw.circle(screen, MIRI_BODY_COLOR, portrait_center, 50)
            pygame.draw.arc(
                screen,
                MIRI_COAT_COLOR,
                (portrait_center[0] - 50, portrait_center[1] - 50, 100, 100),
                math.radians(20),
                math.radians(160),
                width=10,
            )
            pygame.draw.polygon(
                screen,
                MIRI_EAR_COLOR,
                (
                    (portrait_center[0] - 34, portrait_center[1] - 34),
                    (portrait_center[0] - 48, portrait_center[1] - 76),
                    (portrait_center[0] - 12, portrait_center[1] - 48),
                ),
            )
            pygame.draw.polygon(
                screen,
                MIRI_EAR_COLOR,
                (
                    (portrait_center[0] + 34, portrait_center[1] - 34),
                    (portrait_center[0] + 48, portrait_center[1] - 76),
                    (portrait_center[0] + 12, portrait_center[1] - 48),
                ),
            )
            pygame.draw.circle(screen, MIRI_HEAL_COLOR, portrait_center, 12)
        elif character["id"] == "relay":
            # Relay: slender silver maintenance chassis with a purple Rift core.
            pygame.draw.ellipse(
                screen, RELAY_BODY_COLOR,
                (portrait_center[0] - 28, portrait_center[1] - 58, 56, 116),
            )
            pygame.draw.line(
                screen, RELAY_JOINT_COLOR,
                (portrait_center[0] - 42, portrait_center[1] - 4),
                (portrait_center[0] + 42, portrait_center[1] - 4), width=7,
            )
            pygame.draw.circle(screen, RELAY_RIFT_COLOR, portrait_center, 15)
            pygame.draw.circle(screen, RELAY_CORE_COLOR, portrait_center, 7)
            pygame.draw.circle(screen, RELAY_RIFT_COLOR, (portrait_center[0] - 43, portrait_center[1] - 4), 7)
            pygame.draw.circle(screen, RELAY_RIFT_COLOR, (portrait_center[0] + 43, portrait_center[1] - 4), 7)
        elif character["id"] == "haze":
            # Haze: torn cloak over a hood with no visible face.
            pygame.draw.circle(screen, HAZE_BODY_COLOR, portrait_center, 50)
            pygame.draw.polygon(
                screen, HAZE_CLOAK_COLOR,
                (
                    (portrait_center[0], portrait_center[1] - 58),
                    (portrait_center[0] - 52, portrait_center[1] + 48),
                    (portrait_center[0], portrait_center[1] + 34),
                    (portrait_center[0] + 52, portrait_center[1] + 48),
                ),
            )
            pygame.draw.circle(screen, HAZE_CLOAK_COLOR, (portrait_center[0], portrait_center[1] - 17), 28)
            pygame.draw.circle(screen, HAZE_SHADOW_COLOR, (portrait_center[0], portrait_center[1] - 13), 18)
            pygame.draw.circle(screen, HAZE_PURPLE_COLOR, portrait_center, 10)
            pygame.draw.circle(screen, HAZE_GREEN_COLOR, portrait_center, 4)
        elif character["id"] == "sable":
            pygame.draw.circle(screen, SABLE_BODY_COLOR, portrait_center, 50)
            pygame.draw.circle(screen, SABLE_HAIR_COLOR, (portrait_center[0], portrait_center[1] - 22), 28)
            pygame.draw.line(screen, SABLE_WARPAINT_COLOR, (portrait_center[0] - 31, portrait_center[1] - 7), (portrait_center[0] - 12, portrait_center[1] - 7), width=5)
            pygame.draw.line(screen, SABLE_WARPAINT_COLOR, (portrait_center[0] + 12, portrait_center[1] - 7), (portrait_center[0] + 31, portrait_center[1] - 7), width=5)
            pygame.draw.line(screen, SABLE_KNIFE_COLOR, (portrait_center[0] - 43, portrait_center[1] + 43), (portrait_center[0] + 46, portrait_center[1] - 45), width=7)
        else:
            # Aurel: pale elven fire mage in a white-and-gold tailored suit.
            pygame.draw.circle(screen, AUREL_BODY_COLOR, portrait_center, 50)
            pygame.draw.circle(
                screen,
                AUREL_SUIT_COLOR,
                portrait_center,
                47,
                width=10,
            )
            pygame.draw.arc(
                screen,
                AUREL_GOLD_COLOR,
                (
                    portrait_center[0] - 49,
                    portrait_center[1] - 49,
                    98,
                    98,
                ),
                math.radians(25),
                math.radians(155),
                width=6,
            )
            pygame.draw.circle(
                screen,
                AUREL_HAIR_COLOR,
                (portrait_center[0], portrait_center[1] - 23),
                29,
            )
            pygame.draw.line(
                screen,
                AUREL_EYE_COLOR,
                (portrait_center[0] - 16, portrait_center[1] - 11),
                (portrait_center[0] + 16, portrait_center[1] - 11),
                width=5,
            )
            pygame.draw.circle(
                screen,
                AUREL_FIRE_COLOR,
                (portrait_center[0], portrait_center[1] + 12),
                14,
            )
            pygame.draw.circle(
                screen,
                AUREL_FIRE_GOLD_COLOR,
                (portrait_center[0], portrait_center[1] + 12),
                7,
            )

        name = large_font.render(
            character["name"].upper(),
            True,
            TEXT_COLOR if implemented else (126, 130, 140),
        )
        role = regular_font.render(
            character["class"].upper(),
            True,
            RIFT_BLUE_COLOR if implemented else (105, 109, 119),
        )
        screen.blit(name, name.get_rect(center=(rectangle.centerx, rectangle.top + 190)))
        screen.blit(role, role.get_rect(center=(rectangle.centerx, rectangle.top + 226)))

        if character["id"] == "malphas":
            detail_lines = [
                "110 HP | Fast movement",
                "Q Hellstep",
                "C Silence",
                "X Bloodlust",
            ]
        elif character["id"] == "longshot":
            detail_lines = [
                "95 HP | Precision hunter",
                "Q Resonance Sweep",
                "C Track",
                "X Dead Line",
            ]
        elif character["id"] == "varek":
            detail_lines = [
                "105 HP | Close-range breaker",
                "Q Oni Blade",
                "C Breach Charge",
                "X Unbound Fury",
            ]
        elif character["id"] == "miri":
            detail_lines = [
                "80 HP | Mobile combat medic",
                "Q Feline Lunge",
                "C Field Treatment",
                "X Nine Lives",
            ]
        elif character["id"] == "relay":
            detail_lines = [
                "100 HP | Rift objective specialist",
                "Q Rift Boost",
                "C Rift Teleport",
                "X Rift Overclock",
            ]
        elif character["id"] == "haze":
            detail_lines = [
                "95 HP | Deception Phantom",
                "Q Hallucination",
                "C Silence",
                "X Child's Play",
            ]
        elif character["id"] == "sable":
            detail_lines = [
                "100 HP | Endurance hunter",
                "Q Scent of Blood",
                "C Track",
                "X Wild Hunt",
            ]
        else:
            detail_lines = [
                "95 HP | Ranged fire breaker",
                "Q Cinderbolt",
                "C Breach Charge",
                "X Explosive Inferno",
            ]

        for line_index, line in enumerate(detail_lines):
            line_surface = regular_font.render(
                line,
                True,
                TEXT_COLOR if implemented else (115, 119, 129),
            )
            screen.blit(
                line_surface,
                line_surface.get_rect(
                    center=(rectangle.centerx, rectangle.top + 270 + line_index * 25)
                ),
            )

        if selected:
            lock_text = regular_font.render("SELECTED", True, BULLET_COLOR)
            screen.blit(
                lock_text,
                lock_text.get_rect(center=(rectangle.centerx, rectangle.bottom - 24)),
            )

    status = match_state.get("character_status", "")
    if status:
        status_surface = regular_font.render(status, True, BULLET_COLOR)
        screen.blit(
            status_surface,
            status_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() - 62)),
        )
    else:
        instruction = regular_font.render(
            "Click a character or press 1-8. If time expires, Malphas is selected automatically.",
            True,
            (176, 190, 207),
        )
        screen.blit(
            instruction,
            instruction.get_rect(center=(screen.get_width() // 2, screen.get_height() - 62)),
        )


def draw_buy_phase(
    screen,
    regular_font,
    large_font,
    match_state,
    player,
    actors,
    team_rift_energy,
    status_message,
):
    """Show the 15-second weapon shop and the blue team's current economy."""
    if match_state["phase"] != "buying":
        return

    panel_width = 760
    panel_height = 455
    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel.fill((8, 10, 15, 238))
    panel_rect = panel.get_rect(center=screen.get_rect().center)
    screen.blit(panel, panel_rect)

    title = large_font.render(
        f"BUY PHASE - {player['character_name'].upper()}", True, TEXT_COLOR
    )
    screen.blit(
        title,
        title.get_rect(center=(screen.get_width() // 2, panel_rect.top + 48)),
    )

    timer_text = large_font.render(
        f"{max(0.0, match_state['timer']):.1f}s",
        True,
        BULLET_COLOR,
    )
    screen.blit(
        timer_text,
        timer_text.get_rect(center=(screen.get_width() // 2, panel_rect.top + 92)),
    )

    credits = regular_font.render(
        f"Credits: {player['credits']} / {MAX_CREDITS}    "
        f"Team Rift Energy: {team_rift_energy[player['team']]} / {MAX_TEAM_RIFT_ENERGY}",
        True,
        BULLET_COLOR,
    )
    screen.blit(credits, (panel_rect.left + 34, panel_rect.top + 130))

    owned_names = ", ".join(
        WEAPONS[index]["name"] for index in player["owned_weapon_indices"]
    )
    inventory = regular_font.render(
        f"Inventory ({len(player['owned_weapon_indices'])}/{MAX_OWNED_WEAPONS}): {owned_names}",
        True,
        TEXT_COLOR,
    )
    screen.blit(inventory, (panel_rect.left + 34, panel_rect.top + 160))

    purchase_y = panel_rect.top + 205
    for weapon_index in (2, 3):
        weapon = WEAPONS[weapon_index]
        if actor_owns_weapon(player, weapon_index):
            availability = "OWNED"
        elif len(player["owned_weapon_indices"]) >= MAX_OWNED_WEAPONS:
            availability = "INVENTORY FULL"
        elif player["credits"] < weapon["price"]:
            availability = "NOT ENOUGH CREDITS"
        else:
            availability = "AVAILABLE"

        option = regular_font.render(
            f"Press {weapon['slot']} - {weapon['name']} - {weapon['price']} credits - {availability}",
            True,
            TEXT_COLOR,
        )
        screen.blit(option, (panel_rect.left + 54, purchase_y))
        purchase_y += 36

    team_heading = regular_font.render("TEAM ECONOMY", True, BULLET_COLOR)
    screen.blit(team_heading, (panel_rect.left + 34, panel_rect.top + 290))

    allies = [
        actor
        for actor in actors
        if actor["team"] == player["team"] and not actor["is_player"]
    ]
    ally_y = panel_rect.top + 320
    for ally in allies:
        loadout_names = " + ".join(
            WEAPONS[index]["name"] for index in ally["owned_weapon_indices"]
        )
        ally_line = regular_font.render(
            f"{ally['name']}: {ally['credits']} credits | {loadout_names}",
            True,
            TEXT_COLOR,
        )
        screen.blit(ally_line, (panel_rect.left + 54, ally_y))
        ally_y += 28

    if status_message:
        status = regular_font.render(status_message, True, BULLET_COLOR)
        screen.blit(
            status,
            status.get_rect(center=(screen.get_width() // 2, panel_rect.bottom - 55)),
        )

    instruction = regular_font.render(
        "Combat begins at 0. During combat: G drops, F picks up shared weapons.",
        True,
        (182, 198, 218),
    )
    screen.blit(
        instruction,
        instruction.get_rect(center=(screen.get_width() // 2, panel_rect.bottom - 25)),
    )


def draw_round_banner(screen, regular_font, large_font, match_state):
    """Display round and match results during the transition pause."""
    if match_state["phase"] in ("playing", "buying", "character_select"):
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


def reset_round(
    actors,
    weapon_states,
    bullets,
    bullet_marks,
    destructible_objects,
    rift_state,
    dropped_weapons,
):
    """Reset combat state and select the next round's active Rift."""
    for actor in actors:
        reset_actor_for_round(actor)
    for index, weapon in enumerate(WEAPONS):
        weapon_states[index] = make_weapon_state(weapon)
    bullets.clear()
    clear_bullet_marks(bullet_marks)
    reset_destructible_objects(destructible_objects)
    reset_rift_state(rift_state)
    dropped_weapons.clear()


def begin_new_match(
    match_state,
    scores,
    actors,
    weapon_states,
    bullets,
    bullet_marks,
    destructible_objects,
    rift_state,
    dropped_weapons,
    team_rift_energy,
):
    """Restore the score, team economy, and begin round one."""
    scores["blue"] = 0
    scores["red"] = 0
    team_rift_energy["blue"] = STARTING_TEAM_RIFT_ENERGY
    team_rift_energy["red"] = STARTING_TEAM_RIFT_ENERGY
    for actor in actors:
        actor["credits"] = STARTING_CREDITS
        actor["last_buy_round"] = 0
        reset_actor_loadout(actor)
    match_state["phase"] = "character_select"
    match_state["timer"] = CHARACTER_SELECT_DURATION
    match_state["message"] = ""
    match_state["round_number"] = 1
    match_state["selected_character_id"] = None
    match_state["character_status"] = ""
    reset_round(
        actors,
        weapon_states,
        bullets,
        bullet_marks,
        destructible_objects,
        rift_state,
        dropped_weapons,
    )


def finish_round(
    match_state,
    scores,
    actors,
    team_rift_energy,
    winner,
    round_message,
):
    """Award round score, personal credits, and the winning team's Rift Energy."""
    if winner is not None:
        scores[winner] += 1
        add_team_rift_energy(
            team_rift_energy,
            winner,
            RIFT_ENERGY_ROUND_WIN_REWARD,
        )

    for actor in actors:
        if winner is None:
            reward = ROUND_DRAW_CREDITS
        elif actor["team"] == winner:
            reward = ROUND_WIN_CREDITS
        else:
            reward = ROUND_LOSS_CREDITS

        actor["credits"] = min(MAX_CREDITS, actor["credits"] + reward)

        # A purchased weapon survives only if the actor is alive when the
        # round ends. Being downed and never revived therefore loses it too.
        if not actor["alive"]:
            reset_actor_loadout(actor)

    if winner is not None and scores[winner] >= ROUNDS_TO_WIN:
        match_state["phase"] = "match_over"
        match_state["message"] = f"{winner.upper()} WINS THE MATCH"
    else:
        match_state["phase"] = "round_over"
        match_state["timer"] = ROUND_END_DELAY
        match_state["message"] = round_message


def main():
    pygame.init()

    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Riftbound - Version 0.8 Characters - Aurel Breaker")
    pygame.mouse.set_visible(True)

    clock = pygame.time.Clock()
    debug_font = pygame.font.Font(None, 26)
    ammunition_font = pygame.font.Font(None, 48)
    title_font = pygame.font.Font(None, 96)
    walls = make_walls()
    destructible_objects = make_destructible_objects()
    all_obstacle_rects = walls + [
        destructible["rect"] for destructible in destructible_objects
    ]
    all_obstacle_indices = {
        id(obstacle): index
        for index, obstacle in enumerate(all_obstacle_rects)
    }
    active_obstacles = get_active_obstacle_rects(
        walls,
        destructible_objects,
    )
    active_obstacle_signature = tuple(
        not destructible["destroyed"]
        for destructible in destructible_objects
    )
    vision_buffers = make_vision_render_buffers(
        screen.get_size(),
        all_obstacle_rects,
    )
    wall_segments = get_wall_segments(active_obstacles)
    wall_corners = get_wall_corners(active_obstacles)
    actors = make_match_actors()
    player = actors[0]
    rift_state = make_rift_state()

    aim_angle = 0.0
    bullets = []
    bullet_marks = []
    dropped_weapons = []

    weapon_states = [make_weapon_state(weapon) for weapon in WEAPONS]
    active_weapon_index = 0
    camera_recoil_offset = pygame.Vector2()
    camera_recoil_velocity = pygame.Vector2()
    camera_shake_strength = 0.0
    recoil_sway_direction = 1
    stamina = player["max_stamina"]
    sprint_exhausted = False
    scores = {"blue": 0, "red": 0}
    team_rift_energy = {
        "blue": STARTING_TEAM_RIFT_ENERGY,
        "red": STARTING_TEAM_RIFT_ENERGY,
    }
    match_state = {
        "phase": "character_select",
        "timer": CHARACTER_SELECT_DURATION,
        "message": "",
        "round_number": 1,
        "selected_character_id": None,
        "character_status": "",
    }
    vision_frames_since_update = VISION_RENDER_FRAMES_PER_UPDATE
    cached_world_polygon = []
    cached_vision_camera = pygame.Vector2()
    active_vision_mask_camera = pygame.Vector2(-999999, -999999)
    cached_vision_player_position = pygame.Vector2(player["position"])
    buy_status_message = ""
    share_status_timer = 0.0
    ability_status_message = ""
    ability_status_timer = 0.0
    ui_state = "main_menu"
    paused = False
    game_running = True

    while game_running:
        # Delta time keeps movement, bullets, and timers consistent at any frame rate.
        delta_time = min(clock.tick(FPS) / 1000.0, 0.05)
        reload_requested = False
        weapon_switch_requested = None
        purchase_weapon_requested = None
        drop_weapon_requested = False
        pickup_weapon_requested = False
        signature_requested = False
        class_ability_requested = False
        ultimate_requested = False
        character_select_requested = None
        relay_teleport_quadrant_requested = None
        trigger_just_pressed = False
        restart_requested = False
        start_game_requested = False
        ui_click_position = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if ui_state == "main_menu":
                        game_running = False
                    else:
                        paused = not paused
                    continue

                if ui_state == "main_menu":
                    if event.key == pygame.K_RETURN:
                        start_game_requested = True
                    continue

                if paused:
                    continue

                if match_state["phase"] == "character_select":
                    if event.key == pygame.K_1:
                        character_select_requested = "malphas"
                    elif event.key == pygame.K_2:
                        character_select_requested = "longshot"
                    elif event.key == pygame.K_3:
                        character_select_requested = "varek"
                    elif event.key == pygame.K_4:
                        character_select_requested = "miri"
                    elif event.key == pygame.K_5:
                        character_select_requested = "relay"
                    elif event.key == pygame.K_6:
                        character_select_requested = "haze"
                    elif event.key == pygame.K_7:
                        character_select_requested = "sable"
                    elif event.key == pygame.K_8:
                        character_select_requested = "aurel"
                    continue

                if match_state["phase"] == "playing" and relay_teleport_selecting(player):
                    quadrant_keys = {
                        pygame.K_1: "top_left",
                        pygame.K_2: "top_right",
                        pygame.K_3: "bottom_left",
                        pygame.K_4: "bottom_right",
                    }
                    if event.key in quadrant_keys:
                        relay_teleport_quadrant_requested = quadrant_keys[event.key]
                        continue

                if event.key == pygame.K_r:
                    reload_requested = True
                elif event.key == pygame.K_g:
                    drop_weapon_requested = True
                elif event.key == pygame.K_f:
                    pickup_weapon_requested = True
                elif event.key == pygame.K_q:
                    signature_requested = True
                elif event.key == pygame.K_c:
                    class_ability_requested = True
                elif event.key == pygame.K_x:
                    ultimate_requested = True
                elif event.key == pygame.K_1:
                    weapon_switch_requested = 0
                elif event.key == pygame.K_2:
                    weapon_switch_requested = 1
                elif event.key == pygame.K_3:
                    if match_state["phase"] == "buying":
                        purchase_weapon_requested = 2
                    else:
                        weapon_switch_requested = 2
                elif event.key == pygame.K_4:
                    if match_state["phase"] == "buying":
                        purchase_weapon_requested = 3
                    else:
                        weapon_switch_requested = 3
                elif event.key == pygame.K_RETURN:
                    restart_requested = True
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                ui_click_position = event.pos
                if (
                    ui_state == "game"
                    and not paused
                    and match_state["phase"] == "playing"
                    and relay_teleport_selecting(player)
                ):
                    mid_x = screen.get_width() // 2
                    mid_y = screen.get_height() // 2
                    if event.pos[0] < mid_x and event.pos[1] < mid_y:
                        relay_teleport_quadrant_requested = "top_left"
                    elif event.pos[0] >= mid_x and event.pos[1] < mid_y:
                        relay_teleport_quadrant_requested = "top_right"
                    elif event.pos[0] < mid_x and event.pos[1] >= mid_y:
                        relay_teleport_quadrant_requested = "bottom_left"
                    else:
                        relay_teleport_quadrant_requested = "bottom_right"
                elif (
                    ui_state == "game"
                    and not paused
                    and match_state["phase"] == "playing"
                ):
                    trigger_just_pressed = True

        # Main menu interaction is kept outside the match simulation.
        if ui_state == "main_menu":
            if ui_click_position is not None:
                for button in get_main_menu_buttons(screen):
                    if button.contains(ui_click_position):
                        if button.action == "play":
                            start_game_requested = True
                        elif button.action == "quit":
                            game_running = False

            if not game_running:
                break

            if start_game_requested:
                begin_new_match(
                    match_state,
                    scores,
                    actors,
                    weapon_states,
                    bullets,
                    bullet_marks,
                    destructible_objects,
                    rift_state,
                    dropped_weapons,
                    team_rift_energy,
                )
                ui_state = "game"
                paused = False
                active_weapon_index = 0
                buy_status_message = ""
                share_status_timer = 0.0
                ability_status_message = ""
                ability_status_timer = 0.0
                cached_world_polygon = []
                active_vision_mask_camera.update(-999999, -999999)
                cached_vision_player_position.update(player["position"])
                stamina = player["max_stamina"]
                sprint_exhausted = False
                camera_recoil_offset.update(0, 0)
                camera_recoil_velocity.update(0, 0)
                camera_shake_strength = 0.0
                vision_frames_since_update = VISION_RENDER_FRAMES_PER_UPDATE
            else:
                pygame.mouse.set_visible(True)
                draw_main_menu(screen, debug_font, ammunition_font, title_font)
                pygame.display.flip()
                continue

        # Pause-menu clicks are handled before any phase logic.
        if paused and ui_click_position is not None:
            for button in get_pause_menu_buttons(screen):
                if not button.contains(ui_click_position):
                    continue
                if button.action == "resume":
                    paused = False
                elif button.action == "main_menu":
                    paused = False
                    ui_state = "main_menu"
                elif button.action == "quit":
                    game_running = False
                break

        if not game_running:
            break

        if ui_state == "main_menu":
            pygame.mouse.set_visible(True)
            draw_main_menu(screen, debug_font, ammunition_font, title_font)
            pygame.display.flip()
            continue

        # A paused frame still renders the current scene, but all simulation
        # timers and actions use a zero delta so absolutely nothing advances.
        if paused:
            delta_time = 0.0
            reload_requested = False
            weapon_switch_requested = None
            purchase_weapon_requested = None
            drop_weapon_requested = False
            pickup_weapon_requested = False
            signature_requested = False
            class_ability_requested = False
            ultimate_requested = False
            character_select_requested = None
            trigger_just_pressed = False

        pygame.mouse.set_visible(
            paused or match_state["phase"] == "character_select"
        )

        if not paused and match_state["phase"] == "character_select":
            if ui_click_position is not None:
                selected = handle_character_select_click(
                    match_state,
                    player,
                    ui_click_position,
                )
                if selected:
                    stamina = player["max_stamina"]
                    sprint_exhausted = False

            if character_select_requested is not None:
                selected_character = get_playable_character(character_select_requested)
                if selected_character is None:
                    locked_name = character_select_requested.upper()
                    match_state["character_status"] = (
                        f"{locked_name} IS NOT IMPLEMENTED YET"
                    )
                else:
                    apply_character_to_actor(player, selected_character)
                    match_state["selected_character_id"] = selected_character["id"]
                    match_state["character_status"] = (
                        f"{selected_character['name'].upper()} SELECTED"
                    )
                    stamina = player["max_stamina"]
                    sprint_exhausted = False

        if restart_requested and match_state["phase"] == "match_over":
            begin_new_match(
                match_state,
                scores,
                actors,
                weapon_states,
                bullets,
                bullet_marks,
                destructible_objects,
                rift_state,
                dropped_weapons,
                team_rift_energy,
            )
            active_weapon_index = 0
            buy_status_message = ""
            share_status_timer = 0.0
            ability_status_message = ""
            ability_status_timer = 0.0
            cached_world_polygon = []
            active_vision_mask_camera.update(-999999, -999999)
            cached_vision_player_position.update(player["position"])
            stamina = player["max_stamina"]
            sprint_exhausted = False
            camera_recoil_offset.update(0, 0)
            camera_recoil_velocity.update(0, 0)
            camera_shake_strength = 0.0
            vision_frames_since_update = VISION_RENDER_FRAMES_PER_UPDATE

        if match_state["phase"] == "round_over":
            match_state["timer"] -= delta_time
            if match_state["timer"] <= 0:
                match_state["round_number"] += 1
                reset_round(
                    actors,
                    weapon_states,
                    bullets,
                    bullet_marks,
                    destructible_objects,
                    rift_state,
                    dropped_weapons,
                )
                match_state["phase"] = "buying"
                match_state["timer"] = BUY_PHASE_DURATION
                match_state["message"] = ""
                buy_status_message = ""
                share_status_timer = 0.0
                ability_status_message = ""
                ability_status_timer = 0.0
                cached_world_polygon = []
                active_vision_mask_camera.update(-999999, -999999)
                cached_vision_player_position.update(player["position"])
                if not actor_owns_weapon(player, active_weapon_index):
                    active_weapon_index = 1
                stamina = player["max_stamina"]
                sprint_exhausted = False
                camera_recoil_offset.update(0, 0)
                camera_recoil_velocity.update(0, 0)
                camera_shake_strength = 0.0
                vision_frames_since_update = VISION_RENDER_FRAMES_PER_UPDATE

        if (
            not paused
            and match_state["phase"] == "buying"
            and purchase_weapon_requested is not None
        ):
            purchased, buy_status_message = try_buy_weapon(
                player,
                purchase_weapon_requested,
            )
            if actor_owns_weapon(player, purchase_weapon_requested):
                active_weapon_index = purchase_weapon_requested

        if match_state["phase"] == "playing" and drop_weapon_requested:
            dropped, buy_status_message = drop_player_weapon(
                player,
                active_weapon_index,
                weapon_states,
                dropped_weapons,
            )
            if dropped:
                active_weapon_index = 1
                share_status_timer = SHARE_STATUS_DURATION

        if match_state["phase"] == "playing" and pickup_weapon_requested:
            picked_up, picked_weapon_index, buy_status_message = try_pickup_shared_weapon(
                player,
                dropped_weapons,
                weapon_states,
            )
            if picked_up:
                active_weapon_index = picked_weapon_index
                share_status_timer = SHARE_STATUS_DURATION

        if match_state["phase"] == "character_select" and not paused:
            match_state["timer"] = max(0.0, match_state["timer"] - delta_time)
            if match_state["timer"] <= 0:
                if match_state.get("selected_character_id") is None:
                    apply_character_to_actor(player, MALPHAS)
                    match_state["selected_character_id"] = MALPHAS["id"]
                    match_state["character_status"] = "MALPHAS AUTO-SELECTED"
                stamina = player["max_stamina"]
                sprint_exhausted = False
                match_state["phase"] = "buying"
                match_state["timer"] = BUY_PHASE_DURATION
                match_state["message"] = ""
                buy_status_message = ""
                share_status_timer = 0.0

        if match_state["phase"] == "buying" and not paused:
            # Bots decide once per Buy Phase. Surviving bots with a purchased
            # third weapon naturally keep it and therefore skip another purchase.
            update_bot_buying(actors, match_state["round_number"])

            match_state["timer"] = max(0.0, match_state["timer"] - delta_time)
            if match_state["timer"] <= 0:
                match_state["phase"] = "playing"
                match_state["message"] = ""
                buy_status_message = ""
                share_status_timer = 0.0

        if match_state["phase"] == "playing" and share_status_timer > 0:
            share_status_timer = max(0.0, share_status_timer - delta_time)
            if share_status_timer == 0:
                buy_status_message = ""

        if match_state["phase"] == "playing" and ability_status_timer > 0:
            ability_status_timer = max(0.0, ability_status_timer - delta_time)
            if ability_status_timer == 0:
                ability_status_message = ""

        current_obstacle_signature = tuple(
            not destructible["destroyed"]
            for destructible in destructible_objects
        )
        if current_obstacle_signature != active_obstacle_signature:
            active_obstacles = get_active_obstacle_rects(
                walls,
                destructible_objects,
            )
            wall_segments = get_wall_segments(active_obstacles)
            wall_corners = get_wall_corners(active_obstacles)
            active_obstacle_signature = current_obstacle_signature
            cached_world_polygon = []
            vision_frames_since_update = VISION_RENDER_FRAMES_PER_UPDATE

        if (
            weapon_switch_requested is not None
            and weapon_switch_requested != active_weapon_index
            and actor_owns_weapon(player, weapon_switch_requested)
        ):
            # Switching weapons cancels, rather than completes, the current reload.
            old_weapon_state = weapon_states[active_weapon_index]
            old_weapon_state["reloading"] = False
            old_weapon_state["reload_timer"] = 0.0
            old_weapon_state["sustained_shots"] = 0
            old_weapon_state["attack_animation_timer"] = 0.0
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

        if match_state["phase"] == "playing":
            teleported = update_malphas_abilities(
                player,
                actors,
                active_obstacles,
                delta_time,
            )
            update_longshot_abilities(player, delta_time)
            update_varek_abilities(player, delta_time)
            miri_update_message = update_miri_abilities(
                player,
                actors,
                active_obstacles,
                delta_time,
            )
            if miri_update_message:
                ability_status_message = miri_update_message
                ability_status_timer = 2.0
            relay_update_message, relay_teleported = update_relay_abilities(
                player,
                rift_state,
                active_obstacles,
                delta_time,
            )
            if relay_update_message:
                ability_status_message = relay_update_message
                ability_status_timer = 2.0
            update_haze_abilities(player, actors, active_obstacles, delta_time)
            update_sable_abilities(player, delta_time)
            aurel_update_message, aurel_geometry_changed = update_aurel_abilities(
                player,
                actors,
                walls,
                destructible_objects,
                bullet_marks,
                delta_time,
            )
            if aurel_update_message:
                ability_status_message = aurel_update_message
                ability_status_timer = 2.0
            if aurel_geometry_changed:
                active_obstacles = get_active_obstacle_rects(
                    walls,
                    destructible_objects,
                )
                active_obstacle_signature = tuple(
                    not destructible["destroyed"]
                    for destructible in destructible_objects
                )
                wall_segments = get_wall_segments(active_obstacles)
                wall_corners = get_wall_corners(active_obstacles)
                cached_world_polygon = []
                vision_frames_since_update = VISION_RENDER_FRAMES_PER_UPDATE
            if teleported or relay_teleported:
                cached_world_polygon = []
                vision_frames_since_update = VISION_RENDER_FRAMES_PER_UPDATE

        if (
            player_can_act
            and relay_teleport_quadrant_requested is not None
            and player.get("character_id") == RELAY["id"]
        ):
            _, ability_status_message = begin_relay_rift_teleport(
                player, relay_teleport_quadrant_requested, rift_state
            )
            ability_status_timer = 2.0

        if player_can_act and class_ability_requested:
            if player.get("character_id") in (MALPHAS["id"], HAZE["id"]):
                _, ability_status_message = try_activate_silence(player)
            elif player.get("character_class") == "Hunter":
                _, ability_status_message = try_activate_track(player)
            elif player.get("character_id") == MIRI["id"]:
                _, ability_status_message = try_activate_field_treatment(player)
            elif player.get("character_id") == RELAY["id"]:
                _, ability_status_message = try_activate_rift_teleport(player, rift_state)
            elif player.get("character_class") == "Breaker":
                breach_mouse_world = (
                    pygame.Vector2(pygame.mouse.get_pos())
                    + calculate_camera(player["position"], screen.get_size())
                )
                breach_vector = breach_mouse_world - player["position"]
                breach_angle = (
                    math.atan2(breach_vector.y, breach_vector.x)
                    if breach_vector.length_squared() > 0
                    else player["aim_angle"]
                )
                _, ability_status_message, breach_geometry_changed = try_activate_breach_charge(
                    player,
                    breach_angle,
                    active_obstacles,
                    destructible_objects,
                    actors,
                    bullet_marks,
                )
                if breach_geometry_changed:
                    active_obstacles = get_active_obstacle_rects(
                        walls,
                        destructible_objects,
                    )
                    active_obstacle_signature = tuple(
                        not destructible["destroyed"]
                        for destructible in destructible_objects
                    )
                    wall_segments = get_wall_segments(active_obstacles)
                    wall_corners = get_wall_corners(active_obstacles)
                    cached_world_polygon = []
                    vision_frames_since_update = VISION_RENDER_FRAMES_PER_UPDATE
            ability_status_timer = 2.0

        if player_can_act and ultimate_requested:
            if player.get("character_id") == MALPHAS["id"]:
                _, ability_status_message = try_activate_bloodlust(player)
            elif player.get("character_id") == LONGSHOT["id"]:
                _, ability_status_message = try_activate_dead_line(player)
            elif player.get("character_id") == VAREK["id"]:
                _, ability_status_message = try_activate_unbound_fury(player)
            elif player.get("character_id") == MIRI["id"]:
                _, ability_status_message = try_activate_nine_lives(
                    player,
                    actors,
                    active_obstacles,
                )
            elif player.get("character_id") == RELAY["id"]:
                _, ability_status_message = try_activate_rift_overclock(
                    player, rift_state
                )
            elif player.get("character_id") == HAZE["id"]:
                _, ability_status_message = try_activate_childs_play(
                    player, actors, active_obstacles
                )
            elif player.get("character_id") == SABLE["id"]:
                _, ability_status_message = try_activate_wild_hunt(player)
            elif player.get("character_id") == AUREL["id"]:
                _, ability_status_message = try_activate_explosive_inferno(player)
            ability_status_timer = 2.0

        if aurel_inferno_charging(player):
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
                player["max_stamina"],
                stamina + SPRINT_STAMINA_REGEN_PER_SECOND * delta_time,
            )

            # Releasing Shift after recovering prevents rapid run/walk stuttering.
            if (
                sprint_exhausted
                and not sprint_key_held
                and stamina >= SPRINT_RECOVERY_THRESHOLD
            ):
                sprint_exhausted = False

        fury_speed_multiplier = (
            VAREK_FURY_SPEED_MULTIPLIER
            if varek_unbound_fury_active(player)
            else 1.0
        )
        treatment_move_multiplier = (
            MIRI_FIELD_TREATMENT_MOVE_MULTIPLIER
            if miri_field_treatment_active(player)
            else 1.0
        )
        wild_hunt_speed_multiplier = (
            SABLE_WILD_HUNT_SPEED_MULTIPLIER
            if sable_wild_hunt_active(player)
            else 1.0
        )
        base_character_speed = (
            player["move_speed"] * fury_speed_multiplier * treatment_move_multiplier * wild_hunt_speed_multiplier
        )
        selected_speed = (
            base_character_speed * player["sprint_multiplier"]
            if sprinting
            else base_character_speed
        )
        movement = movement_direction * selected_speed * delta_time
        player_movement_obstacles = get_character_movement_obstacles(
            player,
            walls,
            destructible_objects,
            active_obstacles,
        )
        move_player(player["position"], movement, player_movement_obstacles)

        if movement_direction.length_squared() == 0:
            movement_state = "Idle"
            actual_speed = 0
        elif sprinting:
            movement_state = "Running"
            actual_speed = selected_speed
        else:
            movement_state = "Walking"
            actual_speed = selected_speed

        update_player_movement_sound(player, movement_state)

        base_spread = get_weapon_spread(active_weapon, movement_state)
        sustained_spread = min(
            active_weapon_state["sustained_shots"]
            * active_weapon["sustained_spread_per_shot"],
            active_weapon["maximum_sustained_spread"],
        )
        current_spread = base_spread + sustained_spread
        if varek_blade_active(player):
            current_spread = 0.0

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

        if player_can_act and signature_requested:
            if player.get("character_id") == MALPHAS["id"]:
                _, ability_status_message = try_activate_hellstep(
                    player,
                    mouse_world_position,
                    active_obstacles,
                )
            elif player.get("character_id") == LONGSHOT["id"]:
                _, ability_status_message = try_activate_resonance_sweep(
                    player,
                    actors,
                )
            elif player.get("character_id") == VAREK["id"]:
                _, ability_status_message = try_activate_oni_blade(player)
            elif player.get("character_id") == MIRI["id"]:
                _, ability_status_message = try_activate_feline_lunge(player)
            elif player.get("character_id") == RELAY["id"]:
                _, ability_status_message = try_activate_rift_boost(player)
            elif player.get("character_id") == HAZE["id"]:
                _, ability_status_message = try_activate_hallucination(player)
            elif player.get("character_id") == SABLE["id"]:
                _, ability_status_message = try_activate_scent_of_blood(
                    player, actors, active_obstacles
                )
            elif player.get("character_id") == AUREL["id"]:
                _, ability_status_message = try_activate_cinderbolt(
                    player,
                    aim_angle,
                )
            ability_status_timer = 2.0

        for weapon_state in weapon_states:
            weapon_state["shot_cooldown"] = max(
                0.0,
                weapon_state["shot_cooldown"] - delta_time,
            )
            weapon_state["attack_animation_timer"] = max(
                0.0,
                weapon_state["attack_animation_timer"] - delta_time,
            )

        miri_blocks_weapon = (
            miri_feline_lunge_active(player)
            or miri_field_treatment_active(player)
            or miri_nine_lives_active(player)
        )
        relay_blocks_weapon = (
            relay_teleport_selecting(player)
            or relay_teleport_channel_active(player)
        )
        sable_blocks_weapon = sable_wild_hunt_active(player)
        aurel_blocks_weapon = aurel_inferno_charging(player)
        if (
            active_weapon["fire_mode"] != "melee"
            and reload_requested
            and not active_weapon_state["reloading"]
            and not miri_blocks_weapon
            and not relay_blocks_weapon
            and not sable_blocks_weapon
            and not aurel_blocks_weapon
        ):
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

        dead_line_blocks_weapon = (
            player.get("character_id") == LONGSHOT["id"]
            and (
                player["ability_state"].get("dead_line_active", False)
                or player["ability_state"].get("dead_line_requires_release", False)
            )
        )
        dead_line_geometry_changed = False
        if player_can_act and player.get("character_id") == LONGSHOT["id"]:
            dead_line_geometry_changed = update_dead_line_weapon(
                player,
                trigger_held,
                aim_angle,
                walls,
                destructible_objects,
                actors,
                delta_time,
            )
            if dead_line_geometry_changed:
                active_obstacles = get_active_obstacle_rects(
                    walls,
                    destructible_objects,
                )
                active_obstacle_signature = tuple(
                    not destructible["destroyed"]
                    for destructible in destructible_objects
                )
                wall_segments = get_wall_segments(active_obstacles)
                wall_corners = get_wall_corners(active_obstacles)
                cached_world_polygon = []
                vision_frames_since_update = VISION_RENDER_FRAMES_PER_UPDATE

        if active_weapon["fire_mode"] in ("semi", "melee"):
            firing = trigger_just_pressed
        else:
            firing = trigger_held or trigger_just_pressed

        varek_blade_is_active = player_can_act and varek_blade_active(player)
        miri_claws_are_active = player_can_act and miri_feline_lunge_active(player)
        sable_hunt_is_active = player_can_act and sable_wild_hunt_active(player)
        if miri_claws_are_active and trigger_held and not miri_field_treatment_active(player):
            perform_miri_claw_attack(
                player,
                aim_angle,
                actors,
                active_obstacles,
            )
        if sable_hunt_is_active and trigger_held:
            sable_geometry_changed = perform_sable_hunting_knife_attack(
                player, aim_angle, actors, active_obstacles, destructible_objects, bullet_marks
            )
            if sable_geometry_changed:
                active_obstacles = get_active_obstacle_rects(walls, destructible_objects)
                active_obstacle_signature = tuple(not destructible["destroyed"] for destructible in destructible_objects)
                wall_segments = get_wall_segments(active_obstacles)
                wall_corners = get_wall_corners(active_obstacles)
                cached_world_polygon = []
                vision_frames_since_update = VISION_RENDER_FRAMES_PER_UPDATE
        if varek_blade_is_active and trigger_held:
            blade_geometry_changed = perform_varek_blade_attack(
                player,
                aim_angle,
                actors,
                active_obstacles,
                destructible_objects,
                bullet_marks,
            )
            if blade_geometry_changed:
                active_obstacles = get_active_obstacle_rects(
                    walls,
                    destructible_objects,
                )
                active_obstacle_signature = tuple(
                    not destructible["destroyed"]
                    for destructible in destructible_objects
                )
                wall_segments = get_wall_segments(active_obstacles)
                wall_corners = get_wall_corners(active_obstacles)
                cached_world_polygon = []
                vision_frames_since_update = VISION_RENDER_FRAMES_PER_UPDATE

        weapon_has_attack = (
            active_weapon["fire_mode"] == "melee"
            or active_weapon_state["magazine_ammo"] > 0
        )

        can_fire = (
            player_can_act
            and match_state["phase"] == "playing"
            and firing
            and not active_weapon_state["reloading"]
            and weapon_has_attack
            and active_weapon_state["shot_cooldown"] <= 0
            and not dead_line_blocks_weapon
            and not varek_blade_is_active
            and not miri_blocks_weapon
            and not relay_blocks_weapon
            and not sable_blocks_weapon
            and not aurel_blocks_weapon
        )
        if can_fire:
            if active_weapon["fire_mode"] == "melee":
                _, knife_geometry_changed = perform_knife_attack(
                    player,
                    aim_angle,
                    active_weapon,
                    actors,
                    active_obstacles,
                    destructible_objects,
                    bullet_marks,
                )
                if knife_geometry_changed:
                    active_obstacles = get_active_obstacle_rects(
                        walls,
                        destructible_objects,
                    )
                    active_obstacle_signature = tuple(
                        not destructible["destroyed"]
                        for destructible in destructible_objects
                    )
                    wall_segments = get_wall_segments(active_obstacles)
                    wall_corners = get_wall_corners(active_obstacles)
                    cached_world_polygon = []
                    vision_frames_since_update = (
                        VISION_RENDER_FRAMES_PER_UPDATE
                    )
                active_weapon_state["shot_cooldown"] = (
                    active_weapon["seconds_per_shot"]
                )
                active_weapon_state["attack_animation_timer"] = (
                    active_weapon["attack_animation_time"]
                )
            else:
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
                active_weapon_state["shot_cooldown"] = (
                    active_weapon["seconds_per_shot"]
                )
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
            active_weapon["fire_mode"] != "melee"
            and not active_weapon_state["reloading"]
            and active_weapon_state["magazine_ammo"] == 0
            and active_weapon_state["reserve_ammo"] > 0
            and not miri_blocks_weapon
            and not relay_blocks_weapon
            and not sable_blocks_weapon
            and not aurel_blocks_weapon
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
                try_revive(
                    player,
                    downed_ally,
                    delta_time,
                    active_obstacles,
                )

            bot_pickups = update_bot_weapon_pickups(actors, dropped_weapons)
            if bot_pickups:
                pickup_actor, pickup_weapon_index = bot_pickups[0]
                buy_status_message = (
                    f"{pickup_actor['name']} PICKED UP "
                    f"{WEAPONS[pickup_weapon_index]['name'].upper()}"
                )
                share_status_timer = SHARE_STATUS_DURATION

            for actor in actors:
                if not actor["is_player"]:
                    update_bot(
                        actor,
                        actors,
                        active_obstacles,
                        bullets,
                        delta_time,
                        rift_state,
                    )

            separate_standing_actors(actors, active_obstacles)
            finish_unattended_revives(actors)
            bullets, obstacle_geometry_changed = update_bullets(
                bullets,
                delta_time,
                walls,
                destructible_objects,
                actors,
                bullet_marks,
            )

            if obstacle_geometry_changed:
                active_obstacles = get_active_obstacle_rects(
                    walls,
                    destructible_objects,
                )
                active_obstacle_signature = tuple(
                    not destructible["destroyed"]
                    for destructible in destructible_objects
                )
                wall_segments = get_wall_segments(active_obstacles)
                wall_corners = get_wall_corners(active_obstacles)
                cached_world_polygon = []
                vision_frames_since_update = VISION_RENDER_FRAMES_PER_UPDATE

            update_actor_activity_tracking(actors, delta_time)
            update_burn_effects(actors, delta_time)

            rift_winner = update_rift_state(
                rift_state,
                actors,
                delta_time,
            )
            update_team_rift_energy(
                rift_state,
                actors,
                team_rift_energy,
                delta_time,
            )
            blue_standing = team_has_standing_actor(actors, "blue")
            red_standing = team_has_standing_actor(actors, "red")

            if rift_winner is not None:
                bullets.clear()
                clear_bullet_marks(bullet_marks)
                finish_round(
                    match_state,
                    scores,
                    actors,
                    team_rift_energy,
                    rift_winner,
                    f"{rift_winner.upper()} WINS BY RIFT CONTROL",
                )
            elif not blue_standing or not red_standing:
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

                finish_round(
                    match_state,
                    scores,
                    actors,
                    team_rift_energy,
                    winner,
                    round_message,
                )

        update_bullet_marks(bullet_marks, delta_time)
        # Only the local player's line of sight controls the world. Teammates
        # are shown separately as always-readable blue position/health markers.
        # Visibility geometry updates every second moving frame. While the
        # player is stationary, cached geometry is reused instead of rebuilding
        # full-screen masks that have not changed.
        vision_frames_since_update += 1
        player_moved_for_vision = (
            player["position"].distance_squared_to(cached_vision_player_position)
            >= 0.25
        )
        refresh_visibility = (
            not cached_world_polygon
            or (
                player_moved_for_vision
                and vision_frames_since_update >= VISION_RENDER_FRAMES_PER_UPDATE
            )
        )
        if refresh_visibility:
            vision_frames_since_update = 0
            cached_vision_player_position.update(player["position"])
            world_camera = pygame.Vector2()
            cached_world_polygon = calculate_vision_polygon(
                player["position"],
                active_obstacles,
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
            active_obstacles,
            all_obstacle_indices,
            camera,
            vision_buffers,
            refresh_visibility=refresh_visibility,
        )
        if refresh_visibility:
            save_visibility_cache(vision_buffers)
            cached_vision_camera.update(camera)
            active_vision_mask_camera.update(camera)
        else:
            active_mask_pixel = (
                round(active_vision_mask_camera.x),
                round(active_vision_mask_camera.y),
            )
            current_camera_pixel = (round(camera.x), round(camera.y))
            if active_mask_pixel != current_camera_pixel:
                restore_visibility_cache(
                    vision_buffers,
                    cached_vision_camera,
                    camera,
                )
                active_vision_mask_camera.update(camera)

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
        draw_hidden_destructibles(
            screen,
            destructible_objects,
            camera,
        )

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
        draw_visible_destructible_details(
            screen,
            destructible_objects,
            bullet_marks,
            camera,
            vision_buffers["wall_mask"],
            vision_buffers["wall_detail_layers"],
            len(walls),
        )

        # The active objective marker remains readable through the terrain
        # shading, while an edge arrow points toward off-screen Rift sites.
        draw_rift(
            screen,
            debug_font,
            rift_state,
            player["position"],
            camera,
        )

        draw_dropped_weapons(
            screen,
            debug_font,
            dropped_weapons,
            player,
            active_obstacles,
            camera,
        )
        draw_malphas_world_effects(screen, player, camera)
        draw_longshot_world_effects(screen, player, actors, camera)
        draw_varek_world_effects(screen, player, camera)
        draw_miri_world_effects(screen, player, camera)
        draw_relay_world_effects(screen, player, rift_state, camera)
        draw_haze_world_effects(screen, debug_font, player, camera)
        draw_hunter_track_effects(screen, player, actors, camera)
        draw_sable_world_effects(screen, debug_font, player, actors, camera)
        draw_aurel_world_effects(screen, player, camera)

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
        draw_haze_enemy_perception(
            screen, debug_font, player, actors, camera, active_obstacles
        )
        if (
            active_weapon["fire_mode"] == "melee"
            and actor_can_fight(player)
            and not varek_blade_active(player)
            and not miri_feline_lunge_active(player)
            and not sable_wild_hunt_active(player)
        ):
            draw_knife(
                screen,
                player,
                camera,
                aim_angle,
                active_weapon_state["attack_animation_timer"],
            )
        draw_rift_intel(
            screen,
            debug_font,
            actors,
            camera,
            rift_state,
        )
        if match_state["phase"] == "playing":
            draw_revive_prompt(
                screen,
                debug_font,
                player,
                actors,
                active_obstacles,
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
            player["max_stamina"],
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
            player["max_stamina"],
        )
        draw_character_panel(
            screen,
            debug_font,
            player,
            ability_status_message,
        )
        draw_match_panel(
            screen,
            debug_font,
            scores,
            match_state["round_number"],
            actors,
            rift_state,
            team_rift_energy,
        )
        if match_state["phase"] == "playing" and buy_status_message:
            share_status = debug_font.render(
                buy_status_message,
                True,
                BULLET_COLOR,
            )
            screen.blit(
                share_status,
                share_status.get_rect(
                    center=(screen.get_width() // 2, screen.get_height() - 52)
                ),
            )

        if (
            player_can_act
            and not miri_field_treatment_active(player)
            and not miri_nine_lives_active(player)
            and not relay_blocks_weapon
            and not aurel_blocks_weapon
        ):
            draw_crosshair(screen, pygame.mouse.get_pos(), current_spread)
        draw_buy_phase(
            screen,
            debug_font,
            ammunition_font,
            match_state,
            player,
            actors,
            team_rift_energy,
            buy_status_message,
        )
        draw_round_banner(
            screen,
            debug_font,
            ammunition_font,
            match_state,
        )
        draw_character_select(
            screen,
            debug_font,
            ammunition_font,
            match_state,
        )
        draw_relay_teleport_selector(screen, ammunition_font, player)
        if paused:
            draw_pause_menu(
                screen,
                debug_font,
                ammunition_font,
                title_font,
            )

        pygame.display.flip()

    pygame.mouse.set_visible(True)
    pygame.quit()


if __name__ == "__main__":
    main()