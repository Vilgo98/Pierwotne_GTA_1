import pygame
from typing import Dict, Any, Tuple, List
from config import GameConfig


def get_restart_button_rect(offset_y: int = 30) -> pygame.Rect:
    return pygame.Rect(GameConfig.SCREEN_WIDTH // 2 - 100, GameConfig.SCREEN_HEIGHT // 2 + offset_y, 200, 50)
def get_exit_button_rect(offset_y: int = 100) -> pygame.Rect:
    return pygame.Rect(GameConfig.SCREEN_WIDTH // 2 - 100, GameConfig.SCREEN_HEIGHT // 2 + offset_y, 200, 50)
def get_resume_button_rect() -> pygame.Rect:
    return pygame.Rect(GameConfig.SCREEN_WIDTH // 2 - 100, GameConfig.SCREEN_HEIGHT // 2 - 100, 200, 50)
def get_back_to_menu_rect() -> pygame.Rect:
    return pygame.Rect(GameConfig.SCREEN_WIDTH // 2 - 100, GameConfig.SCREEN_HEIGHT // 2 - 30, 200, 50)
def get_creation_back_rect() -> pygame.Rect:
    return pygame.Rect(20, GameConfig.SCREEN_HEIGHT - 70, 150, 50)
def get_garage_repair_rect() -> pygame.Rect:
    return pygame.Rect(GameConfig.SCREEN_WIDTH // 2 - 200, 200, 400, 50)
def get_garage_speed_rect() -> pygame.Rect:
    return pygame.Rect(GameConfig.SCREEN_WIDTH // 2 - 200, 300, 400, 50)
def get_garage_armor_rect() -> pygame.Rect:
    return pygame.Rect(GameConfig.SCREEN_WIDTH // 2 - 200, 400, 400, 50)
def get_garage_exit_rect() -> pygame.Rect:
    return pygame.Rect(GameConfig.SCREEN_WIDTH // 2 - 100, 550, 200, 50)

def draw_button(screen: pygame.Surface, rect: pygame.Rect, text: str, font: pygame.font.Font,
                mouse_pos: Tuple[int, int]) -> None:
    color = GameConfig.COLOR_BTN_HOVER if rect.collidepoint(mouse_pos) else GameConfig.COLOR_BTN_NORMAL
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, (255, 255, 255), rect, 2)

    text_surf = font.render(text, True, GameConfig.COLOR_TEXT_WHITE)
    text_x = rect.x + (rect.width - text_surf.get_width()) // 2
    text_y = rect.y + (rect.height - text_surf.get_height()) // 2
    screen.blit(text_surf, (text_x, text_y))

def draw_round_minimap(screen: pygame.Surface, state: Dict[str, Any]) -> None:
    p = state['player']
    diameter = GameConfig.MINIMAP_RADIUS * 2

    minimap_surf = pygame.Surface((diameter, diameter))
    minimap_surf.fill(GameConfig.COLOR_MINIMAP_BG)

    cx, cy = GameConfig.MINIMAP_RADIUS, GameConfig.MINIMAP_RADIUS
    zoom = GameConfig.MINIMAP_ZOOM
    current_time = pygame.time.get_ticks()

    def draw_minimap_obj(obj: Dict[str, Any]) -> None:
        dx = obj['rect'].x - p['x']
        dy = obj['rect'].y - p['y']

        if dx * dx + dy * dy < 16000000:
            mx = cx + dx * zoom
            my = cy + dy * zoom
            mw = obj['rect'].w * zoom
            mh = obj['rect'].h * zoom

            should_draw = True
            if obj['type'] == 'garage':
                if (current_time // 500) % 2 != 0:
                    should_draw = False

            if should_draw:
                if -mw < mx < diameter and -mh < my < diameter:
                    pygame.draw.rect(minimap_surf, obj['color'], (mx, my, mw + 1, mh + 1))

    [draw_minimap_obj(obj) for obj in state['map_objects']]

    mission_points: List[Tuple[Tuple[int, int], Tuple[int, int, int]]] = []
    if state['active_mission'] and 'target' in state['active_mission']:
        col = GameConfig.COLOR_MISSION_PURPLE if state['active_mission'][
                                                     'type'] == 'PURPLE' else GameConfig.COLOR_MISSION_YELLOW
        mission_points.append((state['active_mission']['target'], col))
    else:
        for m in state['available_missions']:
            col = GameConfig.COLOR_MISSION_RED if m['type'] == 'RED' else (
                GameConfig.COLOR_MISSION_PURPLE if m['type'] == 'PURPLE' else GameConfig.COLOR_MISSION_YELLOW
            )
            mission_points.append((m['pos'], col))

    [pygame.draw.circle(
        minimap_surf,
        col,
        (int(cx + (pos[0] - p['x']) * zoom), int(cy + (pos[1] - p['y']) * zoom)),
        5
    ) for pos, col in mission_points]

    pygame.draw.circle(minimap_surf, (255, 255, 255), (cx, cy), 4)

    [pygame.draw.circle(
        minimap_surf,
        (0, 0, 255),
        (int(cx + (pol['x'] - p['x']) * zoom), int(cy + (pol['y'] - p['y']) * zoom)),
        4
    ) for pol in state['police_cars'] if pol['alive']]

    mask = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (cx, cy), GameConfig.MINIMAP_RADIUS)

    final_minimap = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
    final_minimap.blit(minimap_surf, (0, 0))
    final_minimap.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    screen_x = GameConfig.MINIMAP_MARGIN
    screen_y = GameConfig.MINIMAP_MARGIN
    screen.blit(final_minimap, (screen_x, screen_y))
    pygame.draw.circle(screen, (255, 255, 255), (screen_x + cx, screen_y + cy), GameConfig.MINIMAP_RADIUS, 2)


def draw_full_map_overlay(screen: pygame.Surface, state: Dict[str, Any]) -> None:
    overlay = pygame.Surface((GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    margin = 50
    available_h = GameConfig.SCREEN_HEIGHT - 2 * margin
    raw_map = state['full_map_surf']

    aspect_ratio = raw_map.get_width() / raw_map.get_height()
    new_h = available_h
    new_w = int(new_h * aspect_ratio)

    scaled_map = pygame.transform.scale(raw_map, (new_w, new_h))
    map_x = (GameConfig.SCREEN_WIDTH - new_w) // 2
    map_y = (GameConfig.SCREEN_HEIGHT - new_h) // 2

    screen.blit(scaled_map, (map_x, map_y))
    pygame.draw.rect(screen, (255, 255, 255), (map_x, map_y, new_w, new_h), 2)

    ratio_x = new_w / state['map_width']
    ratio_y = new_h / state['map_height']

    px = int(map_x + state['player']['x'] * ratio_x)
    py = int(map_y + state['player']['y'] * ratio_y)
    pygame.draw.circle(screen, (255, 255, 255), (px, py), 6)

    [pygame.draw.circle(
        screen,
        (0, 0, 255),
        (int(map_x + pol['x'] * ratio_x), int(map_y + pol['y'] * ratio_y)),
        5
    ) for pol in state['police_cars'] if pol['alive']]

    mission_points: List[Tuple[Tuple[int, int], Tuple[int, int, int]]] = []
    if state['active_mission'] and 'target' in state['active_mission']:
        col = GameConfig.COLOR_MISSION_PURPLE if state['active_mission'][
                                                     'type'] == 'PURPLE' else GameConfig.COLOR_MISSION_YELLOW
        mission_points.append((state['active_mission']['target'], col))
    else:
        for m in state['available_missions']:
            col = GameConfig.COLOR_MISSION_RED if m['type'] == 'RED' else (
                GameConfig.COLOR_MISSION_PURPLE if m['type'] == 'PURPLE' else GameConfig.COLOR_MISSION_YELLOW
            )
            mission_points.append((m['pos'], col))

    current_ticks = pygame.time.get_ticks()
    [pygame.draw.circle(
        screen,
        col,
        (int(map_x + pos[0] * ratio_x), int(map_y + pos[1] * ratio_y)),
        8
    ) for pos, col in mission_points if (current_ticks // 500) % 2 == 0]

    font = pygame.font.SysFont("Arial", 40, bold=True)
    title = font.render("MAP", True, (255, 255, 255))
    screen.blit(title, (GameConfig.SCREEN_WIDTH // 2 - title.get_width() // 2, 10))


def draw_pause_menu(screen: pygame.Surface, assets: Dict[str, Any], font: pygame.font.Font,
                    mouse_pos: Tuple[int, int]) -> None:
    if assets['background']:
        screen.blit(assets['background'], (0, 0))
    else:
        screen.fill((20, 20, 20))

    overlay = pygame.Surface((GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT))
    overlay.set_alpha(220)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    title_font = pygame.font.SysFont("Arial", 60, bold=True)
    title = title_font.render("PAUSE", True, (255, 255, 255))
    screen.blit(title, (GameConfig.SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

    draw_button(screen, get_resume_button_rect(), "RESUME", font, mouse_pos)
    draw_button(screen, get_back_to_menu_rect(), "BACK TO MENU", font, mouse_pos)
    draw_button(screen, get_exit_button_rect(40), "EXIT GAME", font, mouse_pos)


def draw_main_menu(screen: pygame.Surface, assets: Dict[str, Any], font: pygame.font.Font,
                   mouse_pos: Tuple[int, int]) -> None:
    if assets['background']:
        screen.blit(assets['background'], (0, 0))
    else:
        screen.fill((20, 20, 20))

    title_font = pygame.font.SysFont("Arial", 80, bold=True)
    title = title_font.render("GTA 1 PRIMITIVE", True, GameConfig.COLOR_TEXT_WHITE)
    screen.blit(title, (GameConfig.SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

    draw_button(screen, pygame.Rect(GameConfig.SCREEN_WIDTH // 2 - 100, 300, 200, 50), "START", font, mouse_pos)
    draw_button(screen, pygame.Rect(GameConfig.SCREEN_WIDTH // 2 - 100, 400, 200, 50), "EXIT", font, mouse_pos)


def draw_character_creation(screen: pygame.Surface, assets: Dict[str, Any], font: pygame.font.Font,
                            state: Dict[str, Any], mouse_pos: Tuple[int, int]) -> None:
    if assets['background']:
        screen.blit(assets['background'], (0, 0))
    else:
        screen.fill((20, 20, 20))

    inst_font = pygame.font.SysFont("Arial", 40, bold=True)
    inst = inst_font.render("ENTER NAME & SURNAME:", True, GameConfig.COLOR_TEXT_WHITE)
    screen.blit(inst, (GameConfig.SCREEN_WIDTH // 2 - inst.get_width() // 2, 50))

    input_rect = pygame.Rect(GameConfig.SCREEN_WIDTH // 2 - 200, 120, 400, 50)
    pygame.draw.rect(screen, (50, 50, 50), input_rect)
    pygame.draw.rect(screen, (255, 255, 255), input_rect, 2)

    name_surf = font.render(state['player_name'], True, (255, 255, 0))
    screen.blit(name_surf, (input_rect.x + 10, input_rect.y + 10))

    hint_font = pygame.font.SysFont("Arial", 20)
    hint = hint_font.render("(Press ENTER to confirm)", True, (150, 150, 150))
    screen.blit(hint, (GameConfig.SCREEN_WIDTH // 2 - hint.get_width() // 2, 180))

    if assets.get('character_creation'):
        img = assets['character_creation']
        screen.blit(img, (GameConfig.SCREEN_WIDTH // 2 - img.get_width() // 2, 220))

    draw_button(screen, get_creation_back_rect(), "BACK", font, mouse_pos)


def draw_garage_menu(screen: pygame.Surface, assets: Dict[str, Any], font: pygame.font.Font, state: Dict[str, Any],
                     mouse_pos: Tuple[int, int]) -> None:
    if assets.get('garage_bg'):
        screen.blit(assets['garage_bg'], (0, 0))
        overlay = pygame.Surface((GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
    else:
        overlay = pygame.Surface((GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT))
        overlay.set_alpha(220)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

    title_font = pygame.font.SysFont("Arial", 60, bold=True)
    title = title_font.render("GARAGE", True, (255, 165, 0))
    screen.blit(title, (GameConfig.SCREEN_WIDTH // 2 - title.get_width() // 2, 80))

    draw_button(screen, get_garage_repair_rect(), f"REPAIR (${GameConfig.GARAGE_COST_REPAIR})", font, mouse_pos)
    draw_button(screen, get_garage_speed_rect(), f"SPEED UPGRADE (${GameConfig.GARAGE_COST_SPEED})", font, mouse_pos)

    armor_text = f"ARMOR UPGRADE (${GameConfig.GARAGE_COST_ARMOR})"
    if state['player']['has_armor']:
        armor_text = "ARMOR EQUIPPED"
    draw_button(screen, get_garage_armor_rect(), armor_text, font, mouse_pos)

    draw_button(screen, get_garage_exit_rect(), "EXIT GARAGE", font, mouse_pos)

    money_text = font.render(f"YOUR CASH: ${state['money']}", True, (50, 255, 50))
    screen.blit(money_text, (GameConfig.SCREEN_WIDTH // 2 - money_text.get_width() // 2, 150))

    armor_status = "YES" if state['player']['has_armor'] else "NO"
    status_text = font.render(
        f"HP: {int(state['player']['health'])} | SPEED: {state['player']['max_speed']:.1f} | ARMOR: {armor_status}",
        True, (200, 200, 200))
    screen.blit(status_text, (GameConfig.SCREEN_WIDTH // 2 - status_text.get_width() // 2, 470))