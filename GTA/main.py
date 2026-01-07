import pygame
import sys
import math

from config import GameConfig
from assets import load_assets
from game_state import init_game
from physics import update_physics_with_collisions, check_car_vs_car_collisions
from ai import spawn_police_near_player, update_police_ai, check_police_vs_police_collisions
from missions import update_wanted_level, update_missions
from ui import (
    draw_main_menu, draw_character_creation, draw_garage_menu, draw_pause_menu,
    draw_full_map_overlay, draw_round_minimap, draw_button,
    get_restart_button_rect, get_exit_button_rect, get_resume_button_rect,
    get_back_to_menu_rect, get_creation_back_rect,
    get_garage_repair_rect, get_garage_speed_rect, get_garage_armor_rect, get_garage_exit_rect
)

def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT))
    pygame.display.set_caption("GTA 1 PRIMITIVE")
    clock = pygame.time.Clock()

    assets = load_assets()
    state = init_game()
    font = pygame.font.SysFont("Arial", 24)

    def handle_menu_click(pos: tuple) -> None:
        if pygame.Rect(GameConfig.SCREEN_WIDTH // 2 - 100, 300, 200, 50).collidepoint(pos):
            state['current_state'] = "CREATION"
        elif pygame.Rect(GameConfig.SCREEN_WIDTH // 2 - 100, 400, 200, 50).collidepoint(pos):
            pygame.quit()
            sys.exit()

    def handle_garage_click(pos: tuple) -> None:
        if get_garage_repair_rect().collidepoint(pos):
            if state['money'] >= GameConfig.GARAGE_COST_REPAIR and state['player']['health'] < 100:
                state['money'] -= GameConfig.GARAGE_COST_REPAIR
                state['player']['health'] = 100
        elif get_garage_speed_rect().collidepoint(pos):
            if state['money'] >= GameConfig.GARAGE_COST_SPEED:
                state['money'] -= GameConfig.GARAGE_COST_SPEED
                state['player']['max_speed'] += 1.0
        elif get_garage_armor_rect().collidepoint(pos):
            if state['money'] >= GameConfig.GARAGE_COST_ARMOR and not state['player']['has_armor']:
                state['money'] -= GameConfig.GARAGE_COST_ARMOR
                state['player']['has_armor'] = True
        elif get_garage_exit_rect().collidepoint(pos):
            state['current_state'] = "GAME"
            state['player']['y'] += 100
            state['player']['vel_x'] = 0
            state['player']['vel_y'] = 0

    def draw_game_world() -> None:
        cam_x, cam_y = state['camera_x'], state['camera_y']
        screen.fill(GameConfig.COLOR_ASPHALT)
        screen_rect = pygame.Rect(cam_x, cam_y, GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT)
        render_rect = screen_rect.inflate(600, 600)

        visible_objects = [obj for obj in state['map_objects'] if render_rect.colliderect(obj['tile_rect'])]

        [pygame.draw.rect(
            screen,
            GameConfig.COLOR_GRASS_TILE if obj['type'] == 'tree' else (
                GameConfig.COLOR_WATER if obj['type'] == 'bridge' else (
                    GameConfig.COLOR_GARAGE_ZONE if obj['type'] == 'garage' else (
                        GameConfig.COLOR_SAND_TILE if obj.get('texture') in ['stone1', 'stone2'] or (
                                    obj['type'] == 'wall' and obj['color'] == GameConfig.COLOR_ROCK) else
                        (60, 60, 60)
                    )
                )
            ),
            (obj['tile_rect'].x - cam_x, obj['tile_rect'].y - cam_y, obj['tile_rect'].w, obj['tile_rect'].h)
        ) for obj in visible_objects if
            obj['type'] in ['tree', 'bridge', 'garage', 'road'] or obj.get('texture') in ['stone1', 'stone2'] or (
                        obj['type'] == 'wall' and obj['color'] == GameConfig.COLOR_ROCK)]

        def draw_single_obj(obj):
            if obj.get('texture') and assets.get(obj['texture']):
                screen.blit(assets[obj['texture']], (obj['tile_rect'].x - cam_x, obj['tile_rect'].y - cam_y))
            else:
                if not (obj['type'] in ['tree', 'garage', 'road'] or (
                        obj['type'] == 'wall' and obj['color'] == GameConfig.COLOR_ROCK)):
                    pygame.draw.rect(screen, obj['color'],
                                     (obj['rect'].x - cam_x, obj['rect'].y - cam_y, obj['rect'].w, obj['rect'].h))

        [draw_single_obj(obj) for obj in visible_objects]

        def draw_mission_point(pos, col):
            pygame.draw.circle(screen, col, (int(pos[0] - cam_x), int(pos[1] - cam_y)), 15)

        if state['active_mission'] and 'target' in state['active_mission']:
            col = GameConfig.COLOR_MISSION_PURPLE if state['active_mission'][
                                                         'type'] == 'PURPLE' else GameConfig.COLOR_MISSION_YELLOW
            draw_mission_point(state['active_mission']['target'], col)
        else:
            [draw_mission_point(m['pos'], GameConfig.COLOR_MISSION_RED if m['type'] == 'RED' else (
                GameConfig.COLOR_MISSION_PURPLE if m['type'] == 'PURPLE' else GameConfig.COLOR_MISSION_YELLOW)) for m in
             state['available_missions']]

        def draw_car(car):
            if car['alive'] or car['health'] > 0:
                img = assets['player'] if not car.get('is_police') else assets['police']
                if img:
                    rotated = pygame.transform.rotate(img, car['angle'])
                    new_rect = rotated.get_rect(center=(car['x'] - cam_x, car['y'] - cam_y))
                    screen.blit(rotated, new_rect.topleft)
                else:
                    c = (0, 0, 255) if car.get('is_police') else (255, 0, 0)
                    pygame.draw.rect(screen, c, (car['x'] - cam_x - 15, car['y'] - cam_y - 10, 30, 20))

        all_cars = [state['player']] + state['police_cars']
        [draw_car(c) for c in all_cars]

    while True:
        dt = clock.tick(GameConfig.FPS) / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if state['current_state'] == "MENU":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    handle_menu_click(mouse_pos)

            elif state['current_state'] == "CREATION":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if get_creation_back_rect().collidepoint(mouse_pos):
                        state['current_state'] = "MENU"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and len(state['player_name']) > 0:
                        state['current_state'] = "GAME"
                    elif event.key == pygame.K_BACKSPACE:
                        state['player_name'] = state['player_name'][:-1]
                    elif len(state['player_name']) < 20 and (event.unicode.isalpha() or event.key == pygame.K_SPACE):
                        state['player_name'] += event.unicode

            elif state['current_state'] == "GARAGE":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    handle_garage_click(mouse_pos)

            elif state['current_state'] == "GAME":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m and not state['game_over'] and not state['paused']:
                        state['show_map'] = not state['show_map']
                    if event.key == pygame.K_ESCAPE and not state['game_over'] and not state['show_map']:
                        state['paused'] = not state['paused']

                if state['paused'] and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if get_resume_button_rect().collidepoint(mouse_pos):
                        state['paused'] = False
                    elif get_back_to_menu_rect().collidepoint(mouse_pos):
                        state = init_game()
                        state['current_state'] = "MENU"
                    elif get_exit_button_rect(40).collidepoint(mouse_pos):
                        pygame.quit()
                        sys.exit()

                if state['game_over'] and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if get_restart_button_rect(30).collidepoint(mouse_pos):
                        temp_name = state['player_name']
                        state = init_game()
                        state['player_name'] = temp_name
                        state['current_state'] = "GAME"
                    elif get_exit_button_rect(100).collidepoint(mouse_pos):
                        state = init_game()
                        state['current_state'] = "MENU"

        if state['current_state'] == "MENU":
            draw_main_menu(screen, assets, font, mouse_pos)
        elif state['current_state'] == "CREATION":
            draw_character_creation(screen, assets, font, state, mouse_pos)
        elif state['current_state'] == "GARAGE":
            draw_garage_menu(screen, assets, font, state, mouse_pos)
        elif state['current_state'] == "GAME":
            if not state['paused'] and not state['game_over'] and not state['show_map']:
                keys = pygame.key.get_pressed()

                status = update_physics_with_collisions(state['player'], keys, state['map_objects'], dt)
                if status == "ENTER_GARAGE":
                    state['current_state'] = "GARAGE"
                elif status in ["DROWNED", "WASTED"]:
                    state['game_over'] = True
                    state['end_reason'] = status

                if len(state['police_cars']) < state['wanted_level']:
                    state['police_cars'].append(
                        spawn_police_near_player(state['player'], state['map_objects']))
                if len(state['police_cars']) > state['wanted_level']:
                    state['police_cars'].pop()

                check_police_vs_police_collisions(state['police_cars'])

                [update_police_ai(pol, state['player'], state['map_objects'], dt) for pol in state['police_cars']]
                [check_car_vs_car_collisions(state['player'], pol) for pol in state['police_cars']]

                update_wanted_level(state, dt)
                update_missions(state, dt)

                closest_cop_dist = min(
                    [math.hypot(p['x'] - state['player']['x'], p['y'] - state['player']['y']) for p in
                     state['police_cars']], default=float('inf'))
                player_speed = math.hypot(state['player']['vel_x'], state['player']['vel_y'])

                if state['wanted_level'] > 0:
                    if state['arrest_active']:
                        if closest_cop_dist > GameConfig.ARREST_ESCAPE_DIST:
                            state['arrest_active'] = False
                            state['arrest_timer'] = max(0.0, state['arrest_timer'] - dt * 2.0)
                        else:
                            state['arrest_timer'] += dt
                    elif closest_cop_dist < GameConfig.ARREST_START_DIST and player_speed < 0.5:
                        state['arrest_active'] = True
                        state['arrest_timer'] += dt
                    else:
                        state['arrest_timer'] = max(0.0, state['arrest_timer'] - dt * 2.0)
                else:
                    state['arrest_active'] = False
                    state['arrest_timer'] = 0.0

                if state['arrest_timer'] >= GameConfig.ARREST_TIME:
                    state['game_over'] = True
                    state['end_reason'] = "BUSTED"
                if state['player']['health'] <= 0:
                    state['game_over'] = True
                    state['end_reason'] = "WASTED"

                state['camera_x'] += (state['player']['x'] - GameConfig.SCREEN_WIDTH / 2 - state['camera_x']) * 0.1
                state['camera_y'] += (state['player']['y'] - GameConfig.SCREEN_HEIGHT / 2 - state['camera_y']) * 0.1
                state['camera_x'] = max(0, min(state['camera_x'], state['map_width'] - GameConfig.SCREEN_WIDTH))
                state['camera_y'] = max(0, min(state['camera_y'], state['map_height'] - GameConfig.SCREEN_HEIGHT))

            if state['show_map']:
                draw_full_map_overlay(screen, state)
            elif state['paused']:
                draw_pause_menu(screen, assets, font, mouse_pos)
            else:
                draw_game_world()
                draw_round_minimap(screen, state)

                if state['player']['alive']:
                    hud_img = assets.get('character_hud')
                    hp_text = font.render(f"HP: {int(state['player']['health'])}", True, GameConfig.COLOR_TEXT_WHITE)
                    money_text = font.render(f"$ {state['money']}", True, (50, 200, 50))
                    name_text = font.render(state['player_name'], True, (200, 200, 200))

                    total_w = max(name_text.get_width(), hp_text.get_width(), money_text.get_width()) + 130
                    pygame.draw.rect(screen, (30, 30, 30), (GameConfig.SCREEN_WIDTH - total_w, 0, total_w, 120))
                    pygame.draw.rect(screen, (255, 255, 255), (GameConfig.SCREEN_WIDTH - total_w, 0, total_w, 120), 2)

                    screen.blit(name_text, (GameConfig.SCREEN_WIDTH - total_w + 10, 10))
                    screen.blit(hp_text, (GameConfig.SCREEN_WIDTH - total_w + 10, 40))
                    screen.blit(money_text, (GameConfig.SCREEN_WIDTH - total_w + 10, 70))
                    if hud_img:
                        screen.blit(hud_img, (GameConfig.SCREEN_WIDTH - 110, 10))

                    if state['wanted_level'] > 0:
                        star_text = font.render(f"WANTED LEVEL: {state['wanted_level']}", True,
                                                GameConfig.COLOR_WANTED_STAR)
                        screen.blit(star_text, (GameConfig.SCREEN_WIDTH - 250, 140))

                        is_survival = state['active_mission'] and state['active_mission']['type'] == 'SURVIVAL'
                        if state['cooldown_timer'] > 0 and not is_survival:
                            percent_safe = min(100,
                                               int((state['cooldown_timer'] / GameConfig.WANTED_COOLDOWN_TIME) * 100))
                            cool_text = font.render(f"LOSING HEAT... {percent_safe}%", True, (100, 100, 255))
                            screen.blit(cool_text, (GameConfig.SCREEN_WIDTH - 280, 170))

                    msg_text = pygame.font.SysFont("Arial", 28, bold=True).render(state['mission_message'], True,
                                                                                  (255, 255, 0))
                    screen.blit(msg_text, (GameConfig.SCREEN_WIDTH // 2 - msg_text.get_width() // 2, 20))

                    if state['arrest_timer'] > 0:
                        percent = int((state['arrest_timer'] / GameConfig.ARREST_TIME) * 100)
                        bust_text = font.render(f"BUSTED: {percent}%", True, (0, 0, 255))
                        screen.blit(bust_text, (GameConfig.SCREEN_WIDTH // 2 - 50, 80))

                if state['game_over']:
                    overlay = pygame.Surface((GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT))
                    overlay.set_alpha(150)
                    overlay.fill((0, 0, 0))
                    screen.blit(overlay, (0, 0))

                    col = (200, 0, 0) if state['end_reason'] == "WASTED" else (0, 100, 255)
                    reason_text = pygame.font.SysFont("Arial", 80, bold=True).render(state['end_reason'], True, col)
                    screen.blit(reason_text, (GameConfig.SCREEN_WIDTH // 2 - reason_text.get_width() // 2,
                                              GameConfig.SCREEN_HEIGHT // 2 - 100))

                    draw_button(screen, get_restart_button_rect(), "RESTART", font, mouse_pos)
                    draw_button(screen, get_exit_button_rect(), "EXIT TO MENU", font, mouse_pos)

        pygame.display.flip()


if __name__ == "__main__":
    main()