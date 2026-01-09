import pygame
from settings import *
from support import import_folder
from sprites import Generic
from random import randint,choice



class Sky:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.full_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.start_color = [255, 255, 255] # Начинаем с полного дня
        
        # Этапы изменения цвета: [R, G, B]
        self.stages = [
            [255, 170, 120], # 0: Закат (оранжевый)
            [38, 101, 189],  # 1: Ночь (темно-синий)
            [255, 230, 180], # 2: Рассвет (нежно-желтый/розовый)
            [255, 255, 255]  # 3: День (белый свет)
        ]
        self.current_stage = 0
        self.transition_speed = 3 # Скорость изменения (можно подстроить под себя)

    def display(self, dt):
        target_color = self.stages[self.current_stage]
        
        # Проверяем, достигли ли мы текущего целевого цвета
        at_target = True
        for index, value in enumerate(target_color):
            if abs(self.start_color[index] - value) > 1:
                at_target = False
                # Плавное движение к целевому значению
                if self.start_color[index] > value:
                    self.start_color[index] -= self.transition_speed * dt
                else:
                    self.start_color[index] += self.transition_speed * dt
        
        # Если текущий этап завершен, переходим к следующему
        # Цикл будет идти бесконечно: Закат -> Ночь -> Рассвет -> День -> Закат...
        if at_target:
            self.current_stage = (self.current_stage + 1) % len(self.stages)

        self.full_surf.fill(self.start_color)
        self.display_surface.blit(self.full_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
# Keep your Drop and Rain classes below as they were...
class Drop(Generic):
    def __init__(self, surf, pos, moving, groups, z):

        # general setup
        super().__init__(pos, surf, groups, z)
        self.lifetime = randint(400, 500)
        self.start_time = pygame.time.get_ticks()


        self.moving = moving
        if self.moving:
            self.pos = pygame.math.Vector2(self.rect.topleft)
            self.direction = pygame.math.Vector2(-2, 4)
            self.speed = randint(200, 250)
            
    # Метод update вынесен из __init__ для корректного вызова в игровом цикле
    def update(self, dt):
        # movement
        if self.moving:
            self.pos += self.direction * self.speed * dt
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))
    
        # timer
        # Этот код теперь будет выполняться, удаляя капли по истечении времени жизни
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()


class Rain:
    def __init__(self,all_sprites):
        self.all_sprites=all_sprites
        self.rain_drops=import_folder("sproutland-main/graphics/rain/drops/")
        self.rain_floor=import_folder("sproutland-main/graphics/rain/floor/")
        self.floor_w, self.floor_h = pygame.image.load('sproutland-main/graphics/world/ground.png').get_size()


    def create_floor(self):
        # Капли на полу (неподвижные)
        Drop(
            surf=choice(self.rain_floor),
            pos=(randint(0, self.floor_w), randint(0, self.floor_h)),
            moving=False,
            groups=self.all_sprites,
            z=LAYERS['rain floor'])
            
    def create_drops(self):
        # Движущиеся капли. Установлен Z-уровень 'rain' (более высокий) для отображения над объектами.
        Drop(
            surf=choice(self.rain_drops),
            pos=(randint(0, self.floor_w), randint(0, self.floor_h)),
            moving=True,
            groups=self.all_sprites,
            z=LAYERS['rain floor']) # <--- ИСПРАВЛЕНИЕ Z-УРОВНЯ


    def update(self):
        self.create_floor()
        self.create_drops()
