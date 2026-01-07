from typing import Tuple, List

class GameConfig:
    SCREEN_WIDTH: int = 1000
    SCREEN_HEIGHT: int = 700
    FPS: int = 60
    BLOCK_SIZE: int = 200

    # Fizyka
    ACCELERATION: float = 0.15
    REVERSE_ACCELERATION: float = 0.05
    BRAKE_FORCE: float = 0.4
    FRICTION: float = 0.96
    TURN_SPEED: float = 3.5

    # Drift
    DRIFT_FRICTION: float = 0.985
    DRIFT_TURN_SPEED: float = 5.5

    # Prędkości
    PLAYER_MAX_SPEED: float = 10.0
    PLAYER_REVERSE_SPEED: float = 3.0
    POLICE_MAX_SPEED: float = 11.5

    # Garaż
    GARAGE_COST_REPAIR: int = 500
    GARAGE_COST_SPEED: int = 2500
    GARAGE_COST_ARMOR: int = 3000
    PLAYER_ARMOR_FACTOR: float = 0.5

    # Misje
    MISSION_REWARD: int = 1000
    MISSION_TRIGGER_DIST: float = 100.0
    WANTED_COOLDOWN_TIME: float = 30.0

    # Parametry misji
    SURVIVAL_TIME: float = 120.0
    CHASE_ESCALATION_TIME: float = 60.0

    # Mechanika Aresztowania
    ARREST_TIME: float = 3.0
    ARREST_START_DIST: float = 120.0
    ARREST_ESCAPE_DIST: float = 250.0

    # Minimapa
    MINIMAP_RADIUS: int = 80
    MINIMAP_MARGIN: int = 20
    MINIMAP_ZOOM: float = 0.15

    # Kolory
    COLOR_WATER: Tuple[int, int, int] = (0, 100, 255)
    COLOR_ASPHALT: Tuple[int, int, int] = (40, 40, 40)
    COLOR_BUILDING: Tuple[int, int, int] = (100, 100, 100)
    COLOR_TREE: Tuple[int, int, int] = (0, 60, 0)
    COLOR_ROCK: Tuple[int, int, int] = (100, 50, 0)
    COLOR_GRASS_TILE: Tuple[int, int, int] = (34, 139, 34)
    COLOR_SAND_TILE: Tuple[int, int, int] = (238, 214, 175)
    COLOR_GARAGE_ZONE: Tuple[int, int, int] = (255, 140, 0)

    # Kolory UI
    COLOR_BTN_NORMAL: Tuple[int, int, int] = (50, 50, 50)
    COLOR_BTN_HOVER: Tuple[int, int, int] = (100, 100, 100)
    COLOR_TEXT_WHITE: Tuple[int, int, int] = (255, 255, 255)
    COLOR_MINIMAP_BG: Tuple[int, int, int] = (30, 30, 30)
    COLOR_MINIMAP_BORDER: Tuple[int, int, int] = (0, 0, 0)

    # Kolory Misji
    COLOR_MISSION_YELLOW: Tuple[int, int, int] = (255, 215, 0)
    COLOR_MISSION_RED: Tuple[int, int, int] = (255, 0, 0)
    COLOR_MISSION_PURPLE: Tuple[int, int, int] = (180, 0, 255)
    COLOR_WANTED_STAR: Tuple[int, int, int] = (255, 0, 0)

# MAPA
MAP_LAYOUT: List[str] = [
    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
    "Ww-+-------------------------eWWw--+--eW",
    "W|S|G.SG.|Z|Z|V|S|G.|VSH|SZG.|WW|WW|WW|W",
    "W+-+-----+-+-+-+-+--+---+----+--+--+--+W",
    "W|1|G.321|S|1|2|3|D.|123|G.G.|WW|WW|WW|W",
    "W|.q-e...q-+.|.|.|..|...+----+WWq--+--rW",
    "W|G.S|G.SG.|V|S|Z|G.|SVZ|G.G.|WWKWWKWWKW",
    "W+---+-----+-+--+---+--------+-----+--+W",
    "W|G.SVZZZ123|VG.|2D.132|G.SG.|ZSSV2|ZS|W",
    "W|-eG.G.G...q---+......+-----+-eG..|G.|W",
    "W|1+------+12D.3|2w----rS1231G.|G.S|HV|W",
    "W|.|G.G.G.|.....|.|G.G.G.....Vw+---+--rW",
    "Wq-+------+---+-+--+----+--+-+rWWWWLWWWW",
    "WWWWWWWWWW|SZ3|Z|V3|V32S|S1|S|WWFFBFFFFW",
    "Ww---+--eW|VS.q-+S.q+..wrV.q-|NFFFFFFFFW",
    "W|SVZ|VS|W|21D.2|D.32D.|2D.23|WFFFFFAFFW",
    "W|ZSH|SV+M+.....|......|.....|NFFFFFFFFW",
    "Wq---+--rWq-----P------------rWFFFBFFFFW",
    "WWWWWKWWWWWWWWWWKWWWWWWWWWWWWWWFFFFFFFFW",
    "WTEYEEEYEUETEUETETWFFFFFFFFFFFFFFFFBFFFW",
    "WTYEUETEUTYYTYUTETWFFBFFFFFFBFFFFFFFFFFW",
    "WTEYEEEEEEEEEEEEEENFFFFAFFFFFFAFFFFFBFFW",
    "WTUUTYYTYTYTUTUTETWFFFFFFFFFFFFFFFFFFFFW",
    "WTEYEUETEYEUEUETETWFFFFBFFFFFFAFFFFFFFFW",
    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
]