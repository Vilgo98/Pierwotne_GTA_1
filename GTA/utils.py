import math
import random
from typing import Tuple, Set, List
from config import GameConfig, MAP_LAYOUT


def get_random_road_position() -> Tuple[int, int]:
    valid_chars: Set[str] = {'*', '+', '-', '|', 'q', 'w', 'e', 'r', 'F', 'E'}
    valid_spots: List[Tuple[int, int]] = [
        (c * GameConfig.BLOCK_SIZE + GameConfig.BLOCK_SIZE // 2,
         r * GameConfig.BLOCK_SIZE + GameConfig.BLOCK_SIZE // 2)
        for r, row in enumerate(MAP_LAYOUT)
        for c, char in enumerate(row)
        if char in valid_chars
    ]

    return random.choice(valid_spots) if valid_spots else (1000, 1000)

def get_compass_direction(start_pos: Tuple[float, float], target_pos: Tuple[float, float]) -> str:
    dx = target_pos[0] - start_pos[0]
    dy = target_pos[1] - start_pos[1]
    angle = (math.degrees(math.atan2(-dy, dx)) + 360) % 360

    if 22.5 <= angle < 67.5: return "NORTH-EAST"
    if 67.5 <= angle < 112.5: return "NORTH"
    if 112.5 <= angle < 157.5: return "NORTH-WEST"
    if 157.5 <= angle < 202.5: return "WEST"
    if 202.5 <= angle < 247.5: return "SOUTH-WEST"
    if 247.5 <= angle < 292.5: return "SOUTH"
    if 292.5 <= angle < 337.5: return "SOUTH-EAST"
    return "EAST"