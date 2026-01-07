import math
import random
import itertools
import pygame
from typing import Dict, Any, List, Tuple
from config import GameConfig
from physics import update_physics_with_collisions

def spawn_police_near_player(player: Dict[str, Any], map_objects: List[Dict[str, Any]]) -> Dict[str, Any]:
    road_tiles = [obj for obj in map_objects if obj['type'] in ['road', 'terrain' ]]
    if not road_tiles:
        return _create_police_dict(200, 200)

    px, py = player['x'], player['y']
    min_dist_sq = 500 ** 2
    max_dist_sq = 1100 ** 2

    valid_spawns: List[Tuple[int, int]] = [
        (r['rect'].centerx, r['rect'].centery)
        for r in road_tiles
        if min_dist_sq < (r['rect'].centerx - px) ** 2 + (r['rect'].centery - py) ** 2 < max_dist_sq
    ]

    spawn_pos = random.choice(valid_spawns) if valid_spawns else (
        random.choice(road_tiles)['rect'].centerx,
        random.choice(road_tiles)['rect'].centery
    )

    return _create_police_dict(*spawn_pos)


def _create_police_dict(x: float, y: float) -> Dict[str, Any]:
    return {
        'x': x, 'y': y,
        'angle': 0, 'vel_x': 0, 'vel_y': 0,
        'health': 100, 'alive': True,
        'max_speed': GameConfig.POLICE_MAX_SPEED,
        'is_police': True,
        'has_armor': False,
        'stuck_timer': 0.0, 'turn_direction': 1,
        'tree_cooldown': 0.0
    }

def _check_sensor_collision(cx: float, cy: float, angle_rad: float, offset_angle: float, length: float,
                            map_objects: List[Dict[str, Any]]) -> bool:

    sensor_angle = angle_rad + offset_angle
    sx = cx + math.cos(sensor_angle) * length
    sy = cy - math.sin(sensor_angle) * length

    sensor_rect = pygame.Rect(int(sx) - 5, int(sy) - 5, 10, 10)

    return any(
        obj['type'] in ['wall', 'water', 'tree', 'garage'] and sensor_rect.colliderect(obj['rect'])
        for obj in map_objects
        if abs(obj['rect'].x - cx) < length + 100 and abs(obj['rect'].y - cy) < length + 100
    )


def update_police_ai(police: Dict[str, Any], player: Dict[str, Any], map_objects: List[Dict[str, Any]],
                     dt: float) -> None:
    if not player['alive']: return

    if police['stuck_timer'] > 0:
        police['stuck_timer'] -= dt
        police['ai_throttle'] = -GameConfig.REVERSE_ACCELERATION
        police['ai_turn'] = police['turn_direction'] * 0.6
    else:
        dx = player['x'] - police['x']
        dy = player['y'] - police['y']

        target_angle = math.degrees(math.atan2(-dy, dx))
        diff = (target_angle - police['angle'] + 180) % 360 - 180

        police['ai_throttle'] = GameConfig.ACCELERATION

        rad = math.radians(police['angle'])
        sensor_len = 110

        left_blocked = _check_sensor_collision(police['x'], police['y'], rad, 0.6, sensor_len, map_objects)
        right_blocked = _check_sensor_collision(police['x'], police['y'], rad, -0.6, sensor_len, map_objects)

        if left_blocked and not right_blocked:
            police['ai_turn'] = -1
        elif right_blocked and not left_blocked:
            police['ai_turn'] = 1
        elif left_blocked and right_blocked:
            police['ai_turn'] = 1 if diff > 0 else -1
        else:
            if diff > 10:
                police['ai_turn'] = 1
            elif diff < -10:
                police['ai_turn'] = -1
            else:
                police['ai_turn'] = 0

    status = update_physics_with_collisions(police, None, map_objects, dt)

    if status == "wall" and police['stuck_timer'] <= 0:
        police['stuck_timer'] = 0.6
        police['turn_direction'] = random.choice([-1, 1])


def check_police_vs_police_collisions(police_cars: List[Dict[str, Any]]) -> None:
    for p1, p2 in itertools.combinations(police_cars, 2):
        if p1['alive'] and p2['alive']:
            rect1 = pygame.Rect(p1['x'] - 15, p1['y'] - 10, 30, 20)
            rect2 = pygame.Rect(p2['x'] - 15, p2['y'] - 10, 30, 20)

            if rect1.colliderect(rect2):
                p1['vel_x'], p2['vel_x'] = p2['vel_x'] * 0.8, p1['vel_x'] * 0.8
                p1['vel_y'], p2['vel_y'] = p2['vel_y'] * 0.8, p1['vel_y'] * 0.8

                dx = p1['x'] - p2['x']
                dy = p1['y'] - p2['y']
                dist = math.hypot(dx, dy) or 1

                push = 5.0
                push_x = (dx / dist) * push
                push_y = (dy / dist) * push

                p1['x'] += push_x
                p1['y'] += push_y
                p2['x'] -= push_x
                p2['y'] -= push_y