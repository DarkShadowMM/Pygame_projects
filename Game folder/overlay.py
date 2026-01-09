import pygame
from settings import *

class Overlay:
    def __init__(self, player):
        self.display_surface = pygame.display.get_surface()
        self.player = player

        # Загрузка графики
        overlay_path = 'sproutland-main/graphics/overlay/'
        self.tools_surf = {
            'hoe': pygame.image.load(f'{overlay_path}hoe.png').convert_alpha(),
            'axe': pygame.image.load(f'{overlay_path}axe.png').convert_alpha(),
            'water': pygame.image.load(f'{overlay_path}water.png').convert_alpha(),
        }
        self.seeds_surf = {
            'corn': pygame.image.load(f'{overlay_path}corn.png').convert_alpha(),
            'tomato': pygame.image.load(f'{overlay_path}tomato.png').convert_alpha()
        }

        # Настройки стиля
        self.box_size = 60
        self.padding = 10
        self.border_radius = 10
        self.bg_color = (0, 0, 0, 120)  # Полупрозрачный черный
        self.border_color = (255, 255, 255) # Белая рамка для активного слота

    def draw_slot(self, pos, icon_surf, is_active):
        """Рисует один слот интерфейса с иконкой"""
        # 1. Создаем поверхность для фона слота (с поддержкой прозрачности)
        slot_rect = pygame.Rect(pos[0], pos[1], self.box_size, self.box_size)
        slot_surf = pygame.Surface((self.box_size, self.box_size), pygame.SRCALPHA)
        
        # Рисуем скругленный фон
        pygame.draw.rect(slot_surf, self.bg_color, (0, 0, self.box_size, self.box_size), border_radius=self.border_radius)
        
        # 2. Если слот активен, рисуем яркую рамку
        if is_active:
            pygame.draw.rect(slot_surf, self.border_color, (0, 0, self.box_size, self.box_size), 3, border_radius=self.border_radius)
        
        # Выводим фон на экран
        self.display_surface.blit(slot_surf, slot_rect)

        # 3. Рисуем иконку предмета по центру слота
        icon_rect = icon_surf.get_rect(center=slot_rect.center)
        self.display_surface.blit(icon_surf, icon_rect)

    def display(self):
        # Позиция для всей панели (в левом нижнем углу)
        start_x = 20
        start_y = SCREEN_HEIGHT - self.box_size - 20

        # Рисуем слот для ИНСТРУМЕНТА
        tool_surf = self.tools_surf[self.player.selected_tool]
        self.draw_slot((start_x, start_y), tool_surf, True)

        # Рисуем слот для СЕМЯН (чуть правее)
        seed_surf = self.seeds_surf[self.player.selected_seed]
        seed_x = start_x + self.box_size + self.padding
        self.draw_slot((seed_x, start_y), seed_surf, True)

        # (Опционально) Можно добавить текст-подсказку сверху
        # font = pygame.font.Font(None, 20)
        # text_surf = font.render(f"{self.player.selected_tool.capitalize()}", True, 'white')
        # self.display_surface.blit(text_surf, (start_x, start_y - 20))
