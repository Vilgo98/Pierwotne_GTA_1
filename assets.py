import pygame
import os
from typing import Dict, Any, Tuple
from config import GameConfig


def load_assets() -> Dict[str, Any]:
    assets: Dict[str, Any] = {}
    base_path = os.path.dirname(os.path.abspath(__file__))
    images_dir = "photos"

    def get_path(filename: str) -> str:
        return os.path.join(base_path, images_dir, filename)

    try:
        bs = GameConfig.BLOCK_SIZE

        def load_scale_rot(filename: str, size: Tuple[int, int], rotation: int = 0) -> pygame.Surface:
            img = pygame.image.load(get_path(filename)).convert_alpha()
            scaled = pygame.transform.scale(img, size)
            if rotation != 0:
                return pygame.transform.rotate(scaled, rotation)
            return scaled

        resources = {
            # Auta
            'player': ('car.png', (25, 50), -90),
            'police': ('police.png', (25, 50), -90),

            # Drogi
            'road_h': ('road1.png', (bs, bs), 0),
            'road_v': ('road1.png', (bs, bs), 90),
            'turn_q': ('road2.png', (bs, bs), 0),
            'turn_w': ('road2.png', (bs, bs), -90),
            'turn_e': ('road2.png', (bs, bs), 180),
            'turn_r': ('road2.png', (bs, bs), 90),
            'road_cross': ('cross.png', (bs, bs), 0),

            # Kamienie
            'stone1': ('stone1.png', (bs, bs), 0),
            'stone2': ('stone2.png', (bs, bs), 0),

            # Budynki
            'building_red': ('building_red.png', (bs, bs * 2), 0),
            'building_blue': ('building_blue.png', (bs, bs * 2), 0),
            'building_glass': ('building_glass.png', (bs, bs * 2), 0),
            'building_sklep': ('building_sklep.png', (bs, bs), 0),
            'building_warzywa': ('building_warzywa.png', (bs, bs), 0),
            'building_zielony': ('building_zielony.png', (bs, bs), 0),
            'building_garage': ('building_garage.png', (bs, bs), 0),
            'building_galeria': ('building_galeria.png', (bs * 2, bs), 0),
            'building_difrent': ('building_difrent.png', (bs * 2, bs * 2), 0),

            # Mosty
            'building_most1': ('building_most1.png', (bs, bs), 0),
            'building_most1_v': ('building_most1.png', (bs, bs), 90),
            'building_most2': ('building_most2.png', (bs, bs), 0),
            'building_most2_v': ('building_most2.png', (bs, bs), 90),

            # Drzewa
            'tree_small': ('Tree3.png', (bs, bs), 0),
            'tree_medium': ('tree2.png', (bs, bs), 0),
            'tree_large': ('Tree1.png', (bs, bs), 0),
        }

        assets.update({name: load_scale_rot(*args) for name, args in resources.items()})

        assets['building_wide'] = assets['building_galeria']
        assets['building_tall'] = assets['building_red']
        assets['building_big'] = assets['building_difrent']

        bg_raw = pygame.image.load(get_path('tlo.png')).convert()
        assets['background'] = pygame.transform.scale(bg_raw, (GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT))
        assets['garage_bg'] = assets['background']

        char_raw = pygame.image.load(get_path('postac.png')).convert_alpha()

        ratio = (GameConfig.SCREEN_HEIGHT // 2 + 100) / char_raw.get_height()
        target_w = int(char_raw.get_width() * ratio)
        target_h = int(GameConfig.SCREEN_HEIGHT // 2 + 100)

        assets['character_creation'] = pygame.transform.scale(char_raw, (target_w, target_h))
        assets['character_hud'] = pygame.transform.scale(char_raw, (100, 100))

        print("Zasoby załadowane pomyślnie z folderu photos.")

    except Exception as e:
        print(f"!!! BŁĄD ŁADOWANIA GRAFIK !!!: {e}")
        print(f"Upewnij się, że folder 'photos' istnieje i zawiera pliki .png")
        assets['background'] = None

    return assets