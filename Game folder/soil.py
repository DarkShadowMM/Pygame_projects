import pygame
from settings import *
from pytmx import load_pygame
from support import *
from random import choice


class SoilTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = LAYERS['soil']


class WaterTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = LAYERS['soil water']


class Plant(pygame.sprite.Sprite):
    def __init__(self, plant_type, groups, soil, check_watered):
        super().__init__(groups)
        self.plant_type = plant_type
        # Предполагается, что import_folder возвращает список поверхностей
        self.frames = import_folder(f'sproutland-main/graphics/fruit/{plant_type}')
        
        # Состояние роста
        self.age = 0
        self.max_age = len(self.frames) - 1
        self.grow_speed = GROW_SPEED[plant_type]
        self.harvestable=False
        self.soil = soil
        self.check_watered = check_watered # Это метод SoilLayer.check_watered
        
        # Визуальное представление
        self.image = self.frames[self.age]
        # Сдвиг для центрирования растения над плиткой почвы
        self.y_offset = -16 if plant_type == 'corn' else -8
        self.rect = self.image.get_rect(midbottom=soil.rect.midbottom + pygame.math.Vector2(0, self.y_offset))
        self.z = LAYERS['ground plant']
        
    def grow(self): # ИСПРАВЛЕНИЕ: добавлен self
        # Проверяем, полита ли почва, используя колбэк
        if self.check_watered(self.rect.center):
            self.age += self.grow_speed
            
            new_age = int(self.age)
            
            if int(self.age)>0:
                self.z=LAYERS['main']
                self.hitbox=self.rect.copy().inflate(-26, -self.rect.height*0.4)
            
            # Если растение еще может расти (не достигло максимального возраста)
            if new_age <= self.max_age:
                self.image = self.frames[new_age]
                # Пересчитываем rect, чтобы сохранить центрирование, так как размер изображения мог измениться
                self.rect = self.image.get_rect(midbottom=self.soil.rect.midbottom + pygame.math.Vector2(0, self.y_offset))
            
            # TODO: Здесь можно добавить логику сбора урожая, если self.age > self.max_age
            if self.age>=self.max_age:
                self.age=self.max_age
                self.harvestable=True
        
class SoilLayer():
    def __init__(self, all_sprites,collision_sprites, raining=False): # Добавлен raining для get_hit/water_all
        
        self.all_sprites = all_sprites
        self.collision_sprites=collision_sprites
        self.soil_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()
        self.plant_sprites = pygame.sprite.Group()
        self.raining = raining # Флаг дождя
        
        
        self.soil_surf = pygame.image.load("sproutland-main/graphics/soil/o.png")
        self.soil_surfs = import_folder_dict("sproutland-main/graphics/soil/")
        self.water_surfs = import_folder("sproutland-main/graphics/soil_water")
        
        
        
        self.create_soil_grid()
        self.create_hit_rects()
        
    def create_soil_grid(self):
        # Предполагается, что TILE_SIZE и LAYERS определены в settings.py
        # Загрузка карты TMX
        try:
            tmx_data = load_pygame('sproutland-main/data/new_map.tmx')
        except FileNotFoundError:
            # Обработка, если файл TMX не найден
            print("Ошибка: Файл карты TMX не найден.")
            return

        ground = pygame.image.load("sproutland-main/graphics/world/ground.png")
        h_tiles, v_tiles = ground.get_width() // TILE_SIZE, ground.get_height() // TILE_SIZE
        
        # Сетка для хранения состояния почвы: [] (пусто), ['F'] (доступно), ['F', 'X'] (вскопано), ['F', 'X', 'W'] (полито), ['F', 'X', 'P'] (посажено)
        self.grid = [[[] for col in range(h_tiles)] for row in range(v_tiles)]
        
        for x, y, _ in tmx_data.get_layer_by_name('Farmable').tiles():
            self.grid[y][x].append('F')
            
    def create_hit_rects(self):
        self.hit_rects = []
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'F' in cell:
                    x = index_col * TILE_SIZE
                    y = index_row * TILE_SIZE
                    rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                    self.hit_rects.append(rect)
    
    def check_watered(self, pos):
        # Получаем координаты сетки из позиции в пикселях
        x = pos[0] // TILE_SIZE
        y = pos[1] // TILE_SIZE
        
        # Проверка границ
        if 0 <= y < len(self.grid) and 0 <= x < len(self.grid[0]):
            cell = self.grid[y][x]
            is_watered = 'W' in cell
            return is_watered
        return False
        
    def get_hit(self, point):
        # Метод для вскапывания почвы
        for rect in self.hit_rects:
            if rect.collidepoint(point):
                x = rect.x // TILE_SIZE
                y = rect.y // TILE_SIZE
                # Убедиться, что это доступная и еще не вскопанная ячейка
                if 'F' in self.grid[y][x] and 'X' not in self.grid[y][x]:
                    self.grid[y][x].append('X')
                    self.create_soil_tiles()
                    if self.raining:
                        self.water_all()
                    return True # Успешное вскапывание
        return False # Не попали в зону для вскапывания

    def update_plants(self):
        for plant in self.plant_sprites.sprites():
            plant.grow()

    def create_soil_tiles(self):
        # Очищаем текущие спрайты почвы
        self.soil_sprites.empty()
        
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'X' in cell:
                    # Логика определения типа плитки (тайла) на основе соседних вскопанных клеток ('X')
                    
                    # Проверки границ, чтобы избежать ошибок IndexError
                    t = 'X' in self.grid[index_row - 1][index_col] if index_row > 0 else False
                    b = 'X' in self.grid[index_row + 1][index_col] if index_row < len(self.grid) - 1 else False
                    r = 'X' in row[index_col + 1] if index_col < len(row) - 1 else False
                    l = 'X' in row[index_col - 1] if index_col > 0 else False
                    
                    # Определяем tile_type
                    tile_type = 'o' # по умолчанию
                    
                    # Полностью окруженный
                    if all((t, r, b, l)):
                        tile_type = 'x'

                    # Горизонтальные
                    elif l and not any((t, r, b)): tile_type = 'r'
                    elif r and not any((t, l, b)): tile_type = 'l'
                    elif r and l and not any((t, b)): tile_type = 'lr'
                    
                    # Вертикальные
                    elif t and not any((r, l, b)): tile_type = 'b'
                    elif b and not any((r, l, t)): tile_type = 't'
                    elif b and t and not any((r, l)): tile_type = 'tb'

                    # Углы
                    elif l and b and not any((t, r)): tile_type = 'tr'
                    elif r and b and not any((t, l)): tile_type = 'tl'
                    elif l and t and not any((b, r)): tile_type = 'br'
                    elif r and t and not any((b, l)): tile_type = 'bl'

                    # T-формы
                    elif all((t, b, r)) and not l: tile_type = 'tbr'
                    elif all((t, b, l)) and not r: tile_type = 'tbl'
                    elif all((l, r, t)) and not b: tile_type = 'lrb'
                    elif all((l, r, b)) and not t: tile_type = 'lrt'

                    # Создание спрайта почвы
                    SoilTile(pos=(index_col * TILE_SIZE, index_row * TILE_SIZE),
                             surf=self.soil_surfs[tile_type],
                             groups=[self.all_sprites, self.soil_sprites])
                             
                    # Если почва полита, создаем также спрайт воды
                    if 'W' in cell:
                        pos = (index_col * TILE_SIZE, index_row * TILE_SIZE)
                        surf = choice(self.water_surfs)
                        WaterTile(pos, surf, [self.all_sprites, self.water_sprites])


    def water(self, target_pos):
        # Метод для ручного полива
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target_pos):
                x = soil_sprite.rect.x // TILE_SIZE
                y = soil_sprite.rect.y // TILE_SIZE
                
                # Проверяем, что почва вскопана ('X') и еще не полита ('W')
                if 'X' in self.grid[y][x] and 'W' not in self.grid[y][x]:
                    self.grid[y][x].append('W') 
                    
                    pos = soil_sprite.rect.topleft
                    surf = choice(self.water_surfs) 
                    WaterTile(pos, surf, [self.all_sprites, self.water_sprites])
                    return True # Успешный полив
        return False


    def water_all(self):
        # Метод для полива всех вскопанных клеток (например, при дожде)
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'X' in cell and 'W' not in cell:
                    cell.append('W')
                    x = index_col * TILE_SIZE
                    y = index_row * TILE_SIZE
                    
                    WaterTile((x, y), choice(self.water_surfs), [self.all_sprites, self.water_sprites])
    
    def plant_seed(self, target_pos, seed):
        # Метод для посадки семян
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target_pos):
                x = soil_sprite.rect.x // TILE_SIZE
                y = soil_sprite.rect.y // TILE_SIZE
                
                # Проверяем, что почва вскопана ('X') и на ней ничего не посажено ('P')
                if 'X' in self.grid[y][x] and 'P' not in self.grid[y][x]:
                    self.grid[y][x].append('P')
                    # ИСПРАВЛЕНИЕ: Передаем сам метод self.check_watered
                    Plant(seed, 
                          [self.all_sprites, self.plant_sprites,self.collision_sprites], 
                          soil_sprite, 
                          self.check_watered)
                    return True # Успешная посадка
        return False


    def remove_water(self):
        # 1. Удаление логического маркера 'W' из сетки
        for row in self.grid:
            for cell in row:
                if 'W' in cell:
                    cell.remove('W')
        
        # 2. Удаление спрайтов воды (WaterTile)
        for sprite in self.water_sprites.sprites():
            sprite.kill()
        self.water_sprites.empty()
        
        # 3. Пересоздание спрайтов почвы для визуального сброса (если нужно)
        # Этот шаг не обязателен, если спрайты воды покрывают спрайты почвы,
        # но может быть полезен, если логика water_all/remove_water меняется.
        # self.create_soil_tiles()
