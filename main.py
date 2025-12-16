#test github
import pygame
import sys
import math
import random
from typing import TypedDict, List, Tuple, Optional, Any


# --- KLASA KONFIGURACYJNA ---
class GameConfig:
    # Ustawienia Ekranu i Mapy
    SCREEN_WIDTH = 1000
    SCREEN_HEIGHT = 700
    MAP_WIDTH = 4000
    MAP_HEIGHT = 4000
    FPS = 60

    # Fizyka
    ACCELERATION = 0.15
    FRICTION = 0.05
    TURN_SPEED = 3.0

    # Prędkości
    PLAYER_MAX_SPEED = 6.0
    POLICE_MAX_SPEED = 6.3
    POLICE_REVERSE_SPEED = -2.0

    # AI i Mechaniki Gry
    ARREST_DISTANCE = 150.0
    MIN_DIST_TO_PLAYER = 60.0
    ARREST_TIME_LIMIT = 5.0

    # Balans Obrażeń
    DAMAGE_ON_WALL = 5.0
    DAMAGE_ON_CAR = 15.0
    COLLISION_COOLDOWN_TIME = 1.0

    # Kolory
    COLOR_BTN_NORMAL = (70, 70, 70)
    COLOR_BTN_HOVER = (100, 100, 100)
    COLOR_TEXT = (255, 255, 255)
    COLOR_GRASS = (34, 139, 34)
    COLOR_DESERT = (210, 180, 140)
    COLOR_ASPHALT = (50, 50, 50)
    COLOR_BLACK = (0, 0, 0)
    COLOR_PLAYER = (255, 0, 0)
    COLOR_POLICE_NORMAL = (0, 0, 255)
    COLOR_POLICE_STUCK = (255, 255, 0)
    COLOR_POLICE_STOP = (255, 100, 100)
    COLOR_DEBUG_LINE = (255, 0, 0)


# --- STRUKTURY DANYCH ---

class Car(TypedDict):
    x: float
    y: float
    angle: float
    speed: float
    max_speed: float
    health: float
    max_health: float
    color: Tuple[int, int, int]
    is_police: bool

    collided: bool
    last_collision: Optional[str]
    damage_cooldown: float

    stuck_timer: float
    turn_direction: int


class StaticObject(TypedDict):
    rect: pygame.Rect
    color: Tuple[int, int, int]


class TerrainZone(TypedDict):
    rect: pygame.Rect
    color: Tuple[int, int, int]


class GameState(TypedDict):
    player: Car
    police_cars: List[Car]
    map_objects: List[StaticObject]
    terrain_zones: List[TerrainZone]

    camera_x: float
    camera_y: float

    wanted_level: int
    arrest_timer: float
    is_busted: bool
    game_over: bool

    current_mission: Optional[str]
    money: int


# --- INICJALIZACJA I GENEROWANIE ---

def generate_random_buildings(count: int, forbidden_rects: List[pygame.Rect]) -> List[StaticObject]:
    buildings = []
    attempts = 0
    max_attempts = count * 50

    while len(buildings) < count and attempts < max_attempts:
        attempts += 1
        w = random.randint(50, 200)
        h = random.randint(50, 200)
        x = random.randint(0, GameConfig.MAP_WIDTH - w)
        y = random.randint(0, GameConfig.MAP_HEIGHT - h)

        new_rect = pygame.Rect(x, y, w, h)

        collision = False
        for forbidden in forbidden_rects:
            if new_rect.colliderect(forbidden):
                collision = True
                break

        if not collision:
            for b in buildings:
                if new_rect.colliderect(b['rect']):
                    collision = True
                    break

        if not collision:
            color = (random.randint(80, 120), random.randint(80, 120), random.randint(80, 120))
            buildings.append({'rect': new_rect, 'color': color})

    return buildings


def get_safe_spawn_position(map_objects: List[StaticObject]) -> Tuple[float, float]:
    car_w, car_h = 40, 40
    while True:
        x = random.randint(100, GameConfig.MAP_WIDTH - 100)
        y = random.randint(100, GameConfig.MAP_HEIGHT - 100)
        test_rect = pygame.Rect(x - car_w // 2, y - car_h // 2, car_w, car_h)
        collision = any(test_rect.colliderect(obj['rect']) for obj in map_objects)
        if not collision:
            return float(x), float(y)


def create_police_car(map_objects: List[StaticObject]) -> Car:
    x, y = get_safe_spawn_position(map_objects)
    return {
        'x': x, 'y': y,
        'angle': 0, 'speed': 0, 'max_speed': GameConfig.POLICE_MAX_SPEED,
        'health': 100, 'max_health': 100, 'color': GameConfig.COLOR_POLICE_NORMAL, 'is_police': True,
        'collided': False, 'last_collision': None, 'damage_cooldown': 0.0,
        'stuck_timer': 0.0, 'turn_direction': 1
    }


def init_game_state() -> GameState:
    mw = GameConfig.MAP_WIDTH
    mh = GameConfig.MAP_HEIGHT

    zones: List[TerrainZone] = [
        {'rect': pygame.Rect(0, 0, mw, mh), 'color': GameConfig.COLOR_GRASS},
        {'rect': pygame.Rect(mw // 2, 0, mw // 2, mh), 'color': GameConfig.COLOR_DESERT},
        {'rect': pygame.Rect(0, mh // 2 - 100, mw, 200), 'color': GameConfig.COLOR_ASPHALT},
        {'rect': pygame.Rect(mw // 4 - 100, 0, 200, mh), 'color': GameConfig.COLOR_ASPHALT}
    ]

    player_start_x = 500.0
    player_start_y = mh // 2
    safe_zone_rect = pygame.Rect(int(player_start_x) - 150, int(player_start_y) - 150, 300, 300)

    walls = generate_random_buildings(40, forbidden_rects=[safe_zone_rect])

    walls.append({'rect': pygame.Rect(-50, 0, 50, mh), 'color': GameConfig.COLOR_BLACK})
    walls.append({'rect': pygame.Rect(mw, 0, 50, mh), 'color': GameConfig.COLOR_BLACK})
    walls.append({'rect': pygame.Rect(0, -50, mw, 50), 'color': GameConfig.COLOR_BLACK})
    walls.append({'rect': pygame.Rect(0, mh, mw, 50), 'color': GameConfig.COLOR_BLACK})

    return {
        'player': {
            'x': player_start_x, 'y': player_start_y,
            'angle': 0.0, 'speed': 0.0,
            'max_speed': GameConfig.PLAYER_MAX_SPEED,
            'health': 100.0, 'max_health': 100.0,
            'color': GameConfig.COLOR_PLAYER, 'is_police': False,
            'collided': False, 'last_collision': None, 'damage_cooldown': 0.0,
            'stuck_timer': 0.0, 'turn_direction': 1
        },
        'police_cars': [],
        'map_objects': walls,
        'terrain_zones': zones,

        'camera_x': 0.0,
        'camera_y': 0.0,

        'wanted_level': 0, 'arrest_timer': 0.0,
        'is_busted': False, 'game_over': False,
        'current_mission': None, 'money': 0
    }


# --- FUNKCJE POMOCNICZE ---

def get_ui_rects() -> Tuple[pygame.Rect, pygame.Rect]:
    btn_w, btn_h = 200, 50
    center_x = GameConfig.SCREEN_WIDTH // 2
    center_y = GameConfig.SCREEN_HEIGHT // 2
    restart_rect = pygame.Rect(center_x - btn_w // 2, center_y + 50, btn_w, btn_h)
    exit_rect = pygame.Rect(center_x - btn_w // 2, center_y + 120, btn_w, btn_h)
    return restart_rect, exit_rect


def get_car_rect(car: Car) -> pygame.Rect:
    return pygame.Rect(car['x'] - 15, car['y'] - 10, 30, 20)


def has_line_of_sight(p1_pos: Tuple[float, float], p2_pos: Tuple[float, float], walls: List[StaticObject]) -> bool:
    for wall in walls:
        if wall['rect'].clipline(p1_pos, p2_pos):
            return False
    return True


def approach_speed(current: float, target: float, step: float) -> float:
    if current < target:
        return min(current + step, target)
    elif current > target:
        return max(current - step, target)
    return current


# --- KAMERA ---

def update_camera(state: GameState) -> GameState:
    new_state = state.copy()
    p = state['player']

    target_x = p['x'] - GameConfig.SCREEN_WIDTH / 2
    target_y = p['y'] - GameConfig.SCREEN_HEIGHT / 2

    cam_x = max(0, min(target_x, GameConfig.MAP_WIDTH - GameConfig.SCREEN_WIDTH))
    cam_y = max(0, min(target_y, GameConfig.MAP_HEIGHT - GameConfig.SCREEN_HEIGHT))

    new_state['camera_x'] = cam_x
    new_state['camera_y'] = cam_y
    return new_state


# --- LOGIKA FIZYKI I AI ---

def calculate_physics(car: Car, keys: Any, police_cars: List[Car], dt: float) -> Car:
    if car['is_police']: return car
    new_car = car.copy()

    if new_car['damage_cooldown'] > 0:
        new_car['damage_cooldown'] -= dt

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        new_car['angle'] += GameConfig.TURN_SPEED
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        new_car['angle'] -= GameConfig.TURN_SPEED

    target_speed = 0.0
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        target_speed = new_car['max_speed']
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        target_speed = -new_car['max_speed'] / 2

    if target_speed != 0:
        new_car['speed'] = approach_speed(new_car['speed'], target_speed, GameConfig.ACCELERATION)
    else:
        if new_car['speed'] > 0:
            new_car['speed'] = max(0.0, new_car['speed'] - GameConfig.FRICTION)
        elif new_car['speed'] < 0:
            new_car['speed'] = min(0.0, new_car['speed'] + GameConfig.FRICTION)

    player_rect = get_car_rect(new_car)
    collided_car = None

    for p in police_cars:
        if player_rect.colliderect(get_car_rect(p)):
            collided_car = p
            break

    if collided_car:
        new_car['speed'] *= -0.5
        new_car['collided'] = True
        new_car['last_collision'] = 'police'

        dx = new_car['x'] - collided_car['x']
        dy = new_car['y'] - collided_car['y']
        angle = math.atan2(dy, dx)
        push_dist = 10.0
        new_car['x'] += math.cos(angle) * push_dist
        new_car['y'] += math.sin(angle) * push_dist

        if new_car['damage_cooldown'] <= 0:
            new_car['health'] -= GameConfig.DAMAGE_ON_CAR
            new_car['damage_cooldown'] = GameConfig.COLLISION_COOLDOWN_TIME
    else:
        new_car['collided'] = False
        new_car['last_collision'] = None

    return new_car


def handle_wall_collisions(car: Car, map_objects: List[StaticObject]) -> Car:
    new_car = car.copy()
    rad = math.radians(new_car['angle'])
    dx = math.cos(rad) * new_car['speed']
    dy = -math.sin(rad) * new_car['speed']

    next_x = new_car['x'] + dx
    next_y = new_car['y'] + dy

    test_rect = get_car_rect({'x': next_x, 'y': next_y})  # type: ignore
    collision = any(test_rect.colliderect(obj['rect']) for obj in map_objects)

    if collision:
        new_car['collided'] = True
        new_car['last_collision'] = 'wall'
        if new_car['is_police']:
            if new_car['speed'] > 0: new_car['speed'] = 0
        else:
            new_car['speed'] *= -0.5
            new_car['health'] -= GameConfig.DAMAGE_ON_WALL
    else:
        if not new_car.get('collided', False):
            new_car['collided'] = False
        new_car['x'] = next_x
        new_car['y'] = next_y

    if new_car['health'] <= 0: new_car['health'] = 0
    return new_car


def update_police_ai(police: Car, player: Car, map_objects: List[StaticObject], dt: float) -> Car:
    new_police = police.copy()
    police_rect = get_car_rect(police)
    player_rect = get_car_rect(player)

    hit_player = police_rect.colliderect(player_rect)

    if hit_player:
        new_police['speed'] *= -0.5
        new_police['collided'] = True
        new_police['last_collision'] = 'player'

        dx = new_police['x'] - player['x']
        dy = new_police['y'] - player['y']
        angle = math.atan2(dy, dx)
        push_dist = 10.0
        new_police['x'] += math.cos(angle) * push_dist
        new_police['y'] += math.sin(angle) * push_dist

        return handle_wall_collisions(new_police, map_objects)

    if new_police['stuck_timer'] > 0:
        new_police['stuck_timer'] -= dt
        new_police['collided'] = False
        new_police['last_collision'] = None
        if new_police['stuck_timer'] > 0.5:
            target_speed = 0.0
        else:
            target_speed = GameConfig.POLICE_REVERSE_SPEED
            new_police['angle'] += GameConfig.TURN_SPEED * new_police['turn_direction']
        new_police['speed'] = approach_speed(new_police['speed'], target_speed, GameConfig.ACCELERATION)
    else:
        dx = player['x'] - police['x']
        dy = player['y'] - police['y']
        dist_to_player = math.hypot(dx, dy)
        target_angle = math.degrees(math.atan2(-dy, dx))
        target_speed = GameConfig.POLICE_MAX_SPEED

        if dist_to_player < GameConfig.MIN_DIST_TO_PLAYER:
            target_speed = 0.0
            diff = (target_angle - new_police['angle'] + 180) % 360 - 180
            if abs(diff) > GameConfig.TURN_SPEED:
                new_police['angle'] += GameConfig.TURN_SPEED if diff > 0 else -GameConfig.TURN_SPEED
        else:
            if police['collided'] and police['last_collision'] == 'wall':
                new_police['stuck_timer'] = 1.0
                new_police['turn_direction'] = random.choice([-1, 1])
                target_speed = 0.0
            elif police['collided'] and police['last_collision'] == 'player':
                target_speed = GameConfig.POLICE_MAX_SPEED

            diff = (target_angle - new_police['angle'] + 180) % 360 - 180
            if abs(diff) > GameConfig.TURN_SPEED:
                new_police['angle'] += GameConfig.TURN_SPEED if diff > 0 else -GameConfig.TURN_SPEED
            else:
                new_police['angle'] = target_angle
        new_police['speed'] = approach_speed(new_police['speed'], target_speed, GameConfig.ACCELERATION)

    return handle_wall_collisions(new_police, map_objects)


def check_arrest_status(state: GameState, dt: float) -> GameState:
    new_state = state.copy()
    player = state['player']
    active_police = []
    for p in state['police_cars']:
        dist = math.hypot(p['x'] - player['x'], p['y'] - player['y'])
        if dist < GameConfig.ARREST_DISTANCE:
            if has_line_of_sight((player['x'], player['y']), (p['x'], p['y']), state['map_objects']):
                active_police.append(p)

    is_under_arrest_conditions = len(active_police) > 0
    is_stopped = abs(player['speed']) < 0.5

    if new_state['arrest_timer'] == 0.0:
        if is_stopped and is_under_arrest_conditions: new_state['arrest_timer'] += dt
    else:
        if is_under_arrest_conditions:
            new_state['arrest_timer'] += dt
        else:
            new_state['arrest_timer'] = 0.0

    if new_state['arrest_timer'] >= GameConfig.ARREST_TIME_LIMIT:
        new_state['is_busted'] = True
        new_state['game_over'] = True
    if player['health'] <= 0:
        new_state['game_over'] = True
    return new_state


# --- RENDEROWANIE ---

def draw_button(screen: pygame.Surface, rect: pygame.Rect, text: str, mouse_pos: Tuple[int, int]):
    is_hovered = rect.collidepoint(mouse_pos)
    color = GameConfig.COLOR_BTN_HOVER if is_hovered else GameConfig.COLOR_BTN_NORMAL
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, (200, 200, 200), rect, 2)
    font = pygame.font.SysFont("Arial", 30)
    text_surf = font.render(text, True, GameConfig.COLOR_TEXT)
    screen.blit(text_surf, (rect.x + (rect.width - text_surf.get_width()) // 2,
                            rect.y + (rect.height - text_surf.get_height()) // 2))


def draw_game(screen: pygame.Surface, state: GameState):
    screen.fill(GameConfig.COLOR_BLACK)
    cam_x = state['camera_x']
    cam_y = state['camera_y']
    sw = GameConfig.SCREEN_WIDTH
    sh = GameConfig.SCREEN_HEIGHT

    for zone in state['terrain_zones']:
        draw_rect = pygame.Rect(zone['rect'].x - cam_x, zone['rect'].y - cam_y, zone['rect'].width, zone['rect'].height)
        if draw_rect.colliderect(0, 0, sw, sh):
            pygame.draw.rect(screen, zone['color'], draw_rect)

    for obj in state['map_objects']:
        draw_rect = pygame.Rect(obj['rect'].x - cam_x, obj['rect'].y - cam_y, obj['rect'].width, obj['rect'].height)
        if draw_rect.colliderect(0, 0, sw, sh):
            pygame.draw.rect(screen, obj['color'], draw_rect)

    p = state['player']
    player_color = (255, 100, 100) if p['damage_cooldown'] > 0 else p['color']
    player_surf = pygame.Surface((40, 20), pygame.SRCALPHA)
    player_surf.fill(player_color)
    pygame.draw.rect(player_surf, (255, 255, 255), (30, 0, 10, 20))
    rotated_player = pygame.transform.rotate(player_surf, p['angle'])
    screen_x = p['x'] - cam_x
    screen_y = p['y'] - cam_y
    screen.blit(rotated_player,
                (screen_x - rotated_player.get_width() // 2, screen_y - rotated_player.get_height() // 2))

    for pol in state['police_cars']:
        screen_x = pol['x'] - cam_x
        screen_y = pol['y'] - cam_y
        if not (0 <= screen_x <= sw and 0 <= screen_y <= sh): continue

        if pol['stuck_timer'] > 0.5:
            police_color = GameConfig.COLOR_POLICE_STOP
        elif pol['stuck_timer'] > 0:
            police_color = GameConfig.COLOR_POLICE_STUCK
        else:
            police_color = GameConfig.COLOR_POLICE_NORMAL

        pygame.draw.circle(screen, police_color, (int(screen_x), int(screen_y)), 15)
        rad = math.radians(pol['angle'])
        front_x = screen_x + math.cos(rad) * 15
        front_y = screen_y - math.sin(rad) * 15
        pygame.draw.circle(screen, (255, 255, 255), (int(front_x), int(front_y)), 5)

        if state['arrest_timer'] > 0:
            dist = math.hypot(pol['x'] - p['x'], pol['y'] - p['y'])
            if dist < GameConfig.ARREST_DISTANCE and has_line_of_sight((p['x'], p['y']), (pol['x'], pol['y']),
                                                                       state['map_objects']):
                start_pos = (p['x'] - cam_x, p['y'] - cam_y)
                end_pos = (pol['x'] - cam_x, pol['y'] - cam_y)
                pygame.draw.line(screen, GameConfig.COLOR_DEBUG_LINE, start_pos, end_pos, 2)

    font = pygame.font.SysFont("Arial", 20)
    ui_text = f"HP: {int(p['health'])}% | Busted: {int(state['arrest_timer'] / GameConfig.ARREST_TIME_LIMIT * 100)}%"
    screen.blit(font.render(ui_text, True, GameConfig.COLOR_TEXT), (10, 10))
    coord_text = f"Pos: {int(p['x'])}, {int(p['y'])}"
    screen.blit(font.render(coord_text, True, (200, 200, 200)), (10, 35))

    if state['game_over']:
        overlay = pygame.Surface((sw, sh))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        big_font = pygame.font.SysFont("Arial", 80, bold=True)
        if state['is_busted']:
            text = big_font.render("BUSTED!", True, (50, 100, 255))
        else:
            text = big_font.render("WASTED", True, (200, 0, 0))
        text_rect = text.get_rect(center=(sw // 2, sh // 2 - 50))
        screen.blit(text, text_rect)

        restart_rect, exit_rect = get_ui_rects()
        mouse_pos = pygame.mouse.get_pos()
        draw_button(screen, restart_rect, "RESTART", mouse_pos)
        draw_button(screen, exit_rect, "EXIT", mouse_pos)

    pygame.display.flip()


# --- MAIN ---

def main():
    pygame.init()
    screen = pygame.display.set_mode((GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT))
    pygame.display.set_caption("GTA Functional Style - WASD Controls")
    clock = pygame.time.Clock()

    state = init_game_state()

    # Tworzymy radiowóz w bezpiecznym miejscu
    state['police_cars'].append(create_police_car(state['map_objects']))

    running = True
    while running:
        dt = clock.tick(GameConfig.FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if state['game_over'] and event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    restart_rect, exit_rect = get_ui_rects()
                    if restart_rect.collidepoint(mouse_pos):
                        # RESTART GRY
                        state = init_game_state()
                        state['police_cars'].append(create_police_car(state['map_objects']))

                    elif exit_rect.collidepoint(mouse_pos):
                        running = False

        keys = pygame.key.get_pressed()

        if not state['game_over']:
            player_phys = calculate_physics(state['player'], keys, state['police_cars'], dt)
            player_collided = handle_wall_collisions(player_phys, state['map_objects'])

            new_police = [
                update_police_ai(p, player_collided, state['map_objects'], dt)
                for p in state['police_cars']
            ]

            state['player'] = player_collided
            state['police_cars'] = new_police
            state = check_arrest_status(state, dt)
            state = update_camera(state)

        draw_game(screen, state)

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()