import math
import pygame
from typing import Dict, Any
from config import GameConfig
from utils import get_random_road_position, get_compass_direction


def update_wanted_level(state: Dict[str, Any], dt: float) -> None:
    if state['wanted_level'] == 0:
        state['chase_duration'] = 0.0
        return

    screen_rect = pygame.Rect(state['camera_x'], state['camera_y'], GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT)
    view_rect = screen_rect.inflate(200, 200)

    police_visible = any(
        pol['alive'] and view_rect.colliderect(pygame.Rect(pol['x'] - 20, pol['y'] - 20, 40, 40))
        for pol in state['police_cars']
    )

    if police_visible:
        state['cooldown_timer'] = 0.0
        state['chase_duration'] += dt

        if state['chase_duration'] >= GameConfig.CHASE_ESCALATION_TIME and state['wanted_level'] < 6:
            state['wanted_level'] += 1
            state['mission_message'] = f"ESCALATION! {state['wanted_level']} STARS!"
            state['message_timer'] = 3.0
            state['chase_duration'] = 0.0
    else:
        state['cooldown_timer'] += dt
        state['chase_duration'] = max(0, state['chase_duration'] - dt)

        if state['cooldown_timer'] >= GameConfig.WANTED_COOLDOWN_TIME:
            is_survival = state['active_mission'] and state['active_mission']['type'] == 'RED'

            if not is_survival:
                state['wanted_level'] = 0
                state['police_cars'] = []
                state['chase_duration'] = 0.0
                state['mission_message'] = "HEAT LOST. YOU ARE SAFE."
                state['message_timer'] = 3.0
            else:
                state['cooldown_timer'] = 0.0
                state['police_cars'] = []
                state['mission_message'] = "THEY FOUND YOU! RUN!"
                state['message_timer'] = 2.0


def update_missions(state: Dict[str, Any], dt: float) -> None:
    p = state['player']

    if state['message_timer'] > 0:
        state['message_timer'] -= dt
        if state['message_timer'] <= 0 and state['active_mission'] is None:
            state['mission_message'] = "FIND MISSION (MAP)"

    if m := state['active_mission']:
        if m['type'] == 'YELLOW':
            dist = math.hypot(p['x'] - m['target'][0], p['y'] - m['target'][1])

            if state['message_timer'] <= 0:
                direction = get_compass_direction((p['x'], p['y']), m['target'])
                state['mission_message'] = f"DELIVER TO: {direction}"

            if dist < GameConfig.MISSION_TRIGGER_DIST:
                complete_mission(state, 1000, 1)

        elif m['type'] == 'RED':
            m['timer'] -= dt
            state['mission_message'] = f"SURVIVE: {int(m['timer'])}s"

            if m['timer'] <= 0:
                state['wanted_level'] = 0
                state['police_cars'] = []
                complete_mission(state, 5000, 0)
            elif state['wanted_level'] == 0:
                state['wanted_level'] = 6

        elif m['type'] == 'PURPLE':
            dist = math.hypot(p['x'] - m['target'][0], p['y'] - m['target'][1])

            if state['message_timer'] <= 0:
                state['mission_message'] = f"COLLECT PACKAGES: {m['collected']}/3"

            if dist < GameConfig.MISSION_TRIGGER_DIST:
                m['collected'] += 1
                if m['collected'] < 3:
                    state['wanted_level'] = m['collected'] * 2
                    state['cooldown_timer'] = 0.0
                    m['target'] = get_random_road_position()
                    state['mission_message'] = f"PACK {m['collected']}/3 SECURED! {state['wanted_level']} STARS!"
                    state['message_timer'] = 2.0
                else:
                    complete_mission(state, 3000, 6)
    else:
        triggered_mission = next(
            (m for m in state['available_missions']
             if math.hypot(p['x'] - m['pos'][0], p['y'] - m['pos'][1]) < GameConfig.MISSION_TRIGGER_DIST),
            None
        )

        if triggered_mission:
            state['available_missions'] = [m for m in state['available_missions'] if m != triggered_mission]
            start_mission(state, triggered_mission['type'])


def start_mission(state: Dict[str, Any], mission_type: str) -> None:
    state['active_mission'] = {'type': mission_type}

    if mission_type == 'YELLOW':
        state['active_mission']['target'] = get_random_road_position()
        state['mission_message'] = "DELIVERY JOB STARTED!"

    elif mission_type == 'RED':
        state['wanted_level'] = 6
        state['cooldown_timer'] = 0
        state['active_mission']['timer'] = GameConfig.SURVIVAL_TIME
        state['mission_message'] = "SURVIVE FOR 2 MINUTES! ARMY INBOUND!"

    elif mission_type == 'PURPLE':
        state['active_mission']['target'] = get_random_road_position()
        state['active_mission']['collected'] = 0
        state['mission_message'] = "DEALER JOB: COLLECT 3 PACKAGES"

    state['message_timer'] = 3.0


def complete_mission(state: Dict[str, Any], reward: int, min_wanted_after: int) -> None:
    state['money'] += reward
    state['active_mission'] = None
    state['missions_completed'] += 1

    base_difficulty = min(state['missions_completed'], 6)
    target_wanted = max(min_wanted_after, base_difficulty)

    if min_wanted_after == 0:
        state['wanted_level'] = 0
    elif state['wanted_level'] < target_wanted:
        state['wanted_level'] = target_wanted
        state['cooldown_timer'] = 0.0

    state['mission_message'] = f"MISSION COMPLETE! +${reward}"
    state['message_timer'] = 5.0

    state['available_missions'] = [
        {'type': m_type, 'pos': get_random_road_position()}
        for m_type in ['YELLOW', 'RED', 'PURPLE']
    ]