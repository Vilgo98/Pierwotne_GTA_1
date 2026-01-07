import pygame
from typing import Dict, Any, List, Tuple, Optional
from config import GameConfig, MAP_LAYOUT
from utils import get_random_road_position


def generate_full_map_surface(map_objects: List[Dict[str, Any]], map_w: int, map_h: int) -> Tuple[pygame.Surface, float]:
    scale = 0.2
    w = int(map_w * scale)
    h = int(map_h * scale)
    surface = pygame.Surface((w, h))
    surface.fill(GameConfig.COLOR_ASPHALT)

    def draw_obj(obj: Dict[str, Any]) -> None:
        r = obj['rect']
        scaled_rect = pygame.Rect(
            int(r.x * scale), int(r.y * scale),
            max(1, int(r.w * scale)), max(1, int(r.h * scale))
        )

        col = obj['color']
        typ = obj['type']

        if typ == 'bridge': col = (100, 100, 100)
        elif typ == 'tree': col = GameConfig.COLOR_TREE
        elif typ == 'terrain': col = obj['color']
        elif typ == 'garage': col = GameConfig.COLOR_GARAGE_ZONE
        elif typ == 'road': col = (60, 60, 60)

        pygame.draw.rect(surface, col, scaled_rect)

    [draw_obj(obj) for obj in map_objects]

    return surface, scale


def init_game() -> Dict[str, Any]:
    bs = GameConfig.BLOCK_SIZE

    def parse_tile(char: str, x: int, y: int) -> Optional[Dict[str, Any]]:
        rect = pygame.Rect(x, y, bs, bs)
        tile_rect = pygame.Rect(x, y, bs, bs)

        simple_defs = {
            '*': ('road', GameConfig.COLOR_ASPHALT, 'road_h'),
            '-': ('road', GameConfig.COLOR_ASPHALT, 'road_h'),
            '|': ('road', GameConfig.COLOR_ASPHALT, 'road_v'),
            '+': ('road', GameConfig.COLOR_ASPHALT, 'road_cross'),
            'q': ('road', GameConfig.COLOR_ASPHALT, 'turn_q'),
            'w': ('road', GameConfig.COLOR_ASPHALT, 'turn_w'),
            'e': ('road', GameConfig.COLOR_ASPHALT, 'turn_e'),
            'r': ('road', GameConfig.COLOR_ASPHALT, 'turn_r'),
            'H': ('garage', GameConfig.COLOR_GARAGE_ZONE, 'building_garage'),
            'E': ('terrain', GameConfig.COLOR_GRASS_TILE, None),
            'F': ('terrain', GameConfig.COLOR_SAND_TILE, None),
            'W': ('water', GameConfig.COLOR_WATER, None),
            'T': ('tree', GameConfig.COLOR_TREE, 'tree_small'),
            'Y': ('tree', GameConfig.COLOR_TREE, 'tree_medium'),
            'U': ('tree', GameConfig.COLOR_TREE, 'tree_large'),
            'M': ('bridge', (150, 150, 150), 'building_most1'),
            'N': ('bridge', (150, 150, 150), 'building_most2'),
            'K': ('bridge', (150, 150, 150), 'building_most1_v'),
            'L': ('bridge', (150, 150, 150), 'building_most2_v'),
            'S': ('wall', (100, 200, 100), 'building_sklep'),
            'V': ('wall', (255, 100, 0), 'building_warzywa'),
            'Z': ('wall', (0, 255, 0), 'building_zielony'),
            '#': ('wall', GameConfig.COLOR_BUILDING, None),
            'P': ('road', GameConfig.COLOR_ASPHALT, 'road_cross'),
        }

        if char in simple_defs:
            t, c, tex = simple_defs[char]
            return {'type': t, 'color': c, 'texture': tex, 'rect': rect, 'tile_rect': tile_rect}

        if char in '1235':
            rect.height = bs * 2
            colors = {'1': (150, 50, 50), '2': (50, 50, 150), '3': (100, 200, 255), '5': (150, 50, 50)}
            texs = {'1': 'building_red', '2': 'building_blue', '3': 'building_glass', '5': 'building_tall'}
            return {'type': 'wall', 'color': colors[char], 'texture': texs[char], 'rect': rect, 'tile_rect': tile_rect}

        if char in 'G4':
            rect.width = bs * 2
            colors = {'G': (200, 100, 100), '4': (50, 50, 150)}
            texs = {'G': 'building_galeria', '4': 'building_wide'}
            return {'type': 'wall', 'color': colors[char], 'texture': texs[char], 'rect': rect, 'tile_rect': tile_rect}

        if char in 'D6':
            rect.width = bs * 2
            rect.height = bs * 2
            colors = {'D': (100, 100, 100), '6': (100, 200, 255)}
            texs = {'D': 'building_difrent', '6': 'building_big'}
            return {'type': 'wall', 'color': colors[char], 'texture': texs[char], 'rect': rect, 'tile_rect': tile_rect}

        if char in 'RAB':
            rect = pygame.Rect(x + 20, y + 20, bs - 40, bs - 40)
            tex = 'stone1' if char == 'A' else ('stone2' if char == 'B' else None)
            return {'type': 'wall', 'color': GameConfig.COLOR_ROCK, 'texture': tex, 'rect': rect, 'tile_rect': tile_rect}

        return None

    map_objects: List[Dict[str, Any]] = [
        obj
        for r, row in enumerate(MAP_LAYOUT)
        for c, char in enumerate(row)
        if (obj := parse_tile(char, c * bs, r * bs)) is not None
    ]

    player_start: Tuple[int, int] = next(
        (
            (c * bs + bs // 2, r * bs + bs // 2)
            for r, row in enumerate(MAP_LAYOUT)
            for c, char in enumerate(row)
            if char == 'P'
        ),
        (200, 200)
    )

    map_w = len(MAP_LAYOUT[0]) * bs
    map_h = len(MAP_LAYOUT) * bs

    minimap_surf, minimap_scale = generate_full_map_surface(map_objects, map_w, map_h)

    available_missions = [
        {'type': m_type, 'pos': get_random_road_position()}
        for m_type in ['YELLOW', 'RED', 'PURPLE']
    ]

    return {
        'current_state': "MENU",
        'player_name': "",

        'player': {
            'x': player_start[0], 'y': player_start[1],
            'angle': 0, 'vel_x': 0, 'vel_y': 0,
            'health': 100, 'alive': True,
            'max_speed': GameConfig.PLAYER_MAX_SPEED,
            'has_armor': False,
            'is_police': False,
            'tree_cooldown': 0.0
        },
        'police_cars': [],
        'map_objects': map_objects,
        'camera_x': 0, 'camera_y': 0,
        'map_width': map_w,
        'map_height': map_h,

        'money': 0,
        'game_over': False,
        'end_reason': None,
        'arrest_timer': 0.0,
        'arrest_active': False,

        'available_missions': available_missions,
        'active_mission': None,
        'missions_completed': 0,
        'mission_message': "FIND MISSION (MAP)",
        'message_timer': 0.0,

        'wanted_level': 0,
        'cooldown_timer': 0.0,
        'chase_duration': 0.0,

        'show_map': False,
        'paused': False,
        'full_map_surf': minimap_surf,
        'full_map_scale': minimap_scale
    }