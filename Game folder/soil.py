## soil.py
import pygame
from settings import *
from pytmx import load_pygame
from support import *
from random import choice 


class SoilTile(pygame.sprite.Sprite):
    def __init__(self,pos,surf, groups):
        super().__init__(groups)
        self.image=surf
        self.rect=self.image.get_rect(topleft=pos)
        self.z=LAYERS['soil']
        

class WaterTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = LAYERS['soil water']


class Plant(pygame.sprite.Sprite):
    def __init__(self, plant_type,groups,soil):
        super().__init__(groups)
        self.plant_type=plant_type
        self.frames=import_folder(f'sproutland-main/graphics/fruit/{plant_type}')
        
        
        self.age=0
        self.max_age=len(self.frames)-1
        self.grow_speed=GROW_SPEED[plant_type]
        self.soil=soil
        
        
        self.image=self.frames[self.age]
        self.y_offset=-16 if plant_type=='corn' else -8
        self.rect=self.image.get_rect(midbottom=soil.rect.midbottom+pygame.math.Vector2(0,self.y_offset))
        self.z=LAYERS['ground plant']
        
        
class SoilLayer():
    def __init__(self,all_sprites):
        
        self.all_sprites=all_sprites
        self.soil_sprites=pygame.sprite.Group()
        self.water_sprites=pygame.sprite.Group()
        self.plant_sprites=pygame.sprite.Group()
        
        
        self.soil_surf=pygame.image.load("sproutland-main/graphics/soil/o.png")
        self.soil_surfs=import_folder_dict("sproutland-main/graphics/soil/")
        self.water_surfs=import_folder("sproutland-main/graphics/soil_water")
        
        
        
        self.create_soil_grid()
        self.create_hit_rects()
        
    def create_soil_grid(self):
        ground=pygame.image.load("sproutland-main/graphics/world/ground.png")
        h_tiles,v_tiles=ground.get_width()//TILE_SIZE,ground.get_height()//TILE_SIZE
        
        self.grid=[[[] for col in range(h_tiles)] for row in range(v_tiles)]
        for x, y, _ in load_pygame('sproutland-main/data/new_map.tmx').get_layer_by_name('Farmable').tiles():
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
    
                    
    
    
    def get_hit(self, point):
       for rect in self.hit_rects:
           if rect.collidepoint(point):
               x = rect.x // TILE_SIZE
               y = rect.y // TILE_SIZE
               if 'F' in self.grid[y][x]:
                   self.grid[y][x].append('X')
                   self.create_soil_tiles()
                   if self.raining:
                       self.water_all()
                   

    def create_soil_tiles(self):
        self.soil_sprites.empty()
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'X' in cell:
                    # Проверки границ, чтобы избежать ошибок IndexError
                    t = 'X' in self.grid[index_row - 1][index_col] if index_row > 0 else False
                    b = 'X' in self.grid[index_row + 1][index_col] if index_row < len(self.grid) - 1 else False
                    r = 'X' in row[index_col + 1] if index_col < len(row) - 1 else False
                    l = 'X' in row[index_col - 1] if index_col > 0 else False
                    
                    tile_type='o'
                    
                    if all((t, r, b, l)):
                        tile_type = 'x'

                    # horizontal tiles only
                    if l and not any((t, r, b)):
                        tile_type = 'r'
                    if r and not any((t, l, b)):
                        tile_type = 'l'
                    if r and l and not any((t, b)):
                        tile_type = 'lr'
                        
                    # vertical only
                    if t and not any((r, l, b)):
                        tile_type = 'b'
                    if b and not any((r, l, t)):
                        tile_type = 't'
                    if b and t and not any((r, l)):
                        tile_type = 'tb'

                    # corners
                    if l and b and not any((t, r)):
                        tile_type = 'tr'
                    if r and b and not any((t, l)):
                        tile_type = 'tl'
                    if l and t and not any((b, r)):
                        tile_type = 'br'
                    if r and t and not any((b, l)):
                        tile_type = 'bl'

                    # T shapes
                    if all((t, b, r)) and not l:
                        tile_type = 'tbr'
                    if all((t, b, l)) and not r:
                        tile_type = 'tbl'
                    if all((l, r, t)) and not b:
                        tile_type = 'lrb'
                    if all((l, r, b)) and not t:
                        tile_type = 'lrt'

                    SoilTile(pos=(index_col * TILE_SIZE, index_row * TILE_SIZE),
                             surf=self.soil_surfs[tile_type],
                             groups=[self.all_sprites, self.soil_sprites])    
                    
                    
    def water(self, target_pos):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target_pos):
                x = soil_sprite.rect.x // TILE_SIZE
                y = soil_sprite.rect.y // TILE_SIZE
                self.grid[y][x].append('W') 
                
                pos = soil_sprite.rect.topleft
                surf = choice(self.water_surfs) 
                WaterTile(pos, surf, [self.all_sprites, self.water_sprites])
                
    
    def water_all(self):
        for index_row,row in enumerate(self.grid):
            for index_col,cell in enumerate(row):
                if 'X' in cell and 'W' not in cell:
                    cell.append('W')
                    x=index_col*TILE_SIZE
                    y=index_row*TILE_SIZE
                    
                    
                    WaterTile((x,y),choice(self.water_surfs) , [self.all_sprites, self.water_sprites])
    
    def plant_seed(self,target_pos,seed):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target_pos):
                x=soil_sprite.rect.x//TILE_SIZE
                y=soil_sprite.rect.y//TILE_SIZE
                
                if 'P' not in self.grid[y][x]:
                    self.grid[y][x].append('P')
                    Plant(seed,[self.all_sprites,self.plant_sprites],soil_sprite,)
    def remove_water(self):
        
        # 1. Удаление логического маркера 'W' из сетки
        for row in self.grid:
            for cell in row:
                if 'W' in cell:
                    cell.remove('W')
        
        # 2. Усиленное удаление спрайтов воды (WaterTile) с экрана.
        # Явный вызов kill() для гарантированного удаления из self.all_sprites.
        for sprite in self.water_sprites.sprites():
            sprite.kill()
        # Очищаем группу после убийства спрайтов.
        self.water_sprites.empty()
        
        # 3. ПЕРЕСОЗДАНИЕ спрайтов почвы (SoilTile) для визуального сброса
        self.create_soil_tiles()