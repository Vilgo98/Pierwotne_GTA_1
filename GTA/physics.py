import pygame
import math
from typing import Dict, Any, List, Optional
from config import GameConfig


def update_physics_with_collisions(car: Dict[str, Any], keys: Any, map_objects: List[Dict[str, Any]], dt: float) -> \
Optional[str]:
    if not car['alive']: return None

    car['tree_cooldown'] = max(0.0, car['tree_cooldown'] - dt)

    rad = math.radians(car['angle'])
    dir_vec = (math.cos(rad), -math.sin(rad))

    forward_velocity = car['vel_x'] * dir_vec[0] + car['vel_y'] * dir_vec[1]

    force = 0.0
    turn_input = 0
    is_drifting = False

    current_friction = GameConfig.FRICTION
    current_turn_speed = GameConfig.TURN_SPEED

    if not car['is_police']:
        if keys:
            if keys[pygame.K_SPACE]:
                is_drifting = True
                current_friction = GameConfig.DRIFT_FRICTION
                current_turn_speed = GameConfig.DRIFT_TURN_SPEED

            if keys[pygame.K_UP] or keys[pygame.K_w]:
                force = GameConfig.ACCELERATION * (0.1 if is_drifting else 1.0)
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                force = -GameConfig.BRAKE_FORCE if forward_velocity > 0.5 else -GameConfig.REVERSE_ACCELERATION

            if keys[pygame.K_LEFT] or keys[pygame.K_a]: turn_input = 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: turn_input = -1
    else:
        force = car.get('ai_throttle', 0)
        turn_input = car.get('ai_turn', 0)

    if abs(forward_velocity) > 0.5:
        turn = current_turn_speed * turn_input
        if forward_velocity < -0.1 and not is_drifting: turn = -turn
        car['angle'] += turn

    car['vel_x'] += dir_vec[0] * force
    car['vel_y'] += dir_vec[1] * force

    speed = math.hypot(car['vel_x'], car['vel_y'])
    max_s = GameConfig.PLAYER_REVERSE_SPEED if forward_velocity < 0 else car['max_speed']

    if speed > max_s:
        scale = max_s / speed
        car['vel_x'] *= scale
        car['vel_y'] *= scale

    car['vel_x'] *= current_friction
    car['vel_y'] *= current_friction

    hitbox_size = 36
    offset = hitbox_size // 2
    bounce_factor = 0.3 if not car['is_police'] else 0.8
    stop_factor = 0.2 if not car['is_police'] else 0.1

    def resolve_axis_collision(axis: str) -> Optional[str]:
        if axis == 'x':
            car['x'] += car['vel_x']
        else:
            car['y'] += car['vel_y']

        hitbox = pygame.Rect(car['x'] - offset, car['y'] - offset, hitbox_size, hitbox_size)

        hit_obj = next((obj for obj in map_objects
                        if hitbox.colliderect(obj['rect'])
                        and obj['type'] not in ['road', 'terrain', 'bridge']), None)

        if not hit_obj:
            return None

        obj_type = hit_obj['type']

        if obj_type == 'garage':
            if not car['is_police']: return "ENTER_GARAGE"
            return None

        if obj_type == 'tree':
            if not car['is_police'] and car['tree_cooldown'] <= 0:
                car['health'] -= 1
                car['tree_cooldown'] = 2.0
            return None

        if obj_type == 'water':
            on_bridge = any(o['type'] == 'bridge' and hitbox.colliderect(o['rect']) for o in map_objects)

            if not on_bridge:
                if car['is_police']:
                    if axis == 'x':
                        car['x'] -= car['vel_x']; car['vel_x'] = 0
                    else:
                        car['y'] -= car['vel_y']; car['vel_y'] = 0
                    return "wall"
                else:
                    car['alive'] = False
                    return "DROWNED"
            return None

        if obj_type == 'wall':
            if axis == 'x':
                car['x'] -= car['vel_x']
                if car['is_police']: car['x'] -= car['vel_x'] * 2
                car['vel_x'] = -car['vel_x'] * bounce_factor
                car['vel_y'] *= stop_factor
            else:
                car['y'] -= car['vel_y']
                if car['is_police']: car['y'] -= car['vel_y'] * 2
                car['vel_y'] = -car['vel_y'] * bounce_factor
                car['vel_x'] *= stop_factor

            if not car['is_police'] and speed > 3.0:
                dmg = 5 * (GameConfig.PLAYER_ARMOR_FACTOR if car.get('has_armor') else 1)
                car['health'] -= dmg

            return "wall"

        return None

    status_x = resolve_axis_collision('x')
    if status_x in ["DROWNED", "ENTER_GARAGE"]: return status_x

    if abs(car['vel_y']) > 0.01:
        status_y = resolve_axis_collision('y')
        if status_y in ["DROWNED", "ENTER_GARAGE"]: return status_y
        if status_y == "wall" or status_x == "wall": return "wall"
    elif status_x == "wall":
        return "wall"

    if car['health'] <= 0:
        car['health'] = 0
        car['alive'] = False
        return "WASTED"

    return None


def check_car_vs_car_collisions(car1: Dict[str, Any], car2: Dict[str, Any]) -> None:
    if not car1['alive'] or not car2['alive']: return

    rect1 = pygame.Rect(car1['x'] - 15, car1['y'] - 10, 30, 20)
    rect2 = pygame.Rect(car2['x'] - 15, car2['y'] - 10, 30, 20)

    if rect1.colliderect(rect2):
        car1['vel_x'], car2['vel_x'] = car2['vel_x'] * 0.6, car1['vel_x'] * 0.6
        car1['vel_y'], car2['vel_y'] = car2['vel_y'] * 0.6, car1['vel_y'] * 0.6

        dx = car1['x'] - car2['x']
        dy = car1['y'] - car2['y']
        dist = math.hypot(dx, dy)
        if dist == 0: dist = 1

        push_force = 8.0
        car1['x'] += (dx / dist) * push_force
        car1['y'] += (dy / dist) * push_force

        if not car1['is_police']:
            dmg = 5 * (GameConfig.PLAYER_ARMOR_FACTOR if car1.get('has_armor') else 1)
            car1['health'] -= dmg

        if not car2['is_police']:
            dmg = 5 * (GameConfig.PLAYER_ARMOR_FACTOR if car2.get('has_armor') else 1)
            car2['health'] -= dmg