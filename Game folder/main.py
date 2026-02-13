import pygame
import sys
from settings import *
from level import Level
from start_menu import StartMenu

class CustomCursor(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            # Загружаем изображение
            original_image = pygame.image.load('sproutland-main/pointer.png').convert_alpha()
            # Увеличиваем курсор (например, в 2.5 раза для заметности)
            scale_factor = 2.5
            new_size = (int(original_image.get_width() * scale_factor), 
                        int(original_image.get_height() * scale_factor))
            self.image = pygame.transform.scale(original_image, new_size)
        except:
            # Если файл не найден, создаем увеличенный белый квадрат
            self.image = pygame.Surface((40, 40))
            self.image.fill('white')
            
        self.rect = self.image.get_rect()
        pygame.mouse.set_visible(False)

    def update(self):
        self.rect.center = pygame.mouse.get_pos()

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Sproutland')
        self.clock = pygame.time.Clock()
        
        self.cursor = CustomCursor()
        self.start_menu = StartMenu(self.switch_to_game)
        self.level = None
        self.is_playing = False

    def switch_to_game(self):
        self.level = Level() 
        self.is_playing = True

    def run(self):
        while True:
            dt = self.clock.tick() / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill('#fbf2da') 

            if self.is_playing:
                self.level.run(dt)
            else:
                self.start_menu.update(dt)
                self.start_menu.draw()

            # Курсор рисуется поверх всего
            self.cursor.update()
            self.cursor.draw(self.screen)

            pygame.display.update()

if __name__ == '__main__':
    game = Game()
    game.run()
