import pygame
from player import Player
from settings import *
from overlay import Overlay
from sprites import Generic,Water,Wildflower,Tree,Interaction
from pytmx.util_pygame import load_pygame
from support import *
from transition import Transition
from soil import SoilLayer
from sky import *
from random import randint

class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.all_sprites = CameraGroup()
        self.collision_sprites=pygame.sprite.Group()
        self.tree_sprites=pygame.sprite.Group()
        self.interaction_sprites=pygame.sprite.Group()
        
        self.soil_layer=SoilLayer(self.all_sprites)
        self.setup()
        self.overlay=Overlay(self.player)
        self.transition=Transition(self.reset,self.player)
        self.rain=Rain(self.all_sprites)
        self.raining=randint(0,10)>3
        self.soil_layer.raining=self.raining

    def setup(self):
    
        
    
        tmx_data=load_pygame('sproutland-main/data/swmap.tmx')
        
        # House
        for layer in ['HouseFloor','HouseFurnitureBottom']:
            for x,y,surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x*TILE_SIZE,y*TILE_SIZE), surf, self.all_sprites,LAYERS['house bottom'])
                              
        for layer in ['HouseWalls','HouseFurnitureTop']:
            for x,y,surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x*TILE_SIZE,y*TILE_SIZE), surf, [self.all_sprites, self.collision_sprites])
        
        # Fence
        for x,y,surf in tmx_data.get_layer_by_name('Fence').tiles():
            Generic((x*TILE_SIZE,y*TILE_SIZE), surf, [self.all_sprites,self.collision_sprites])
        
        # Water
        water_frames = import_folder('sproutland-main/graphics/water')
        for x,y,surf in tmx_data.get_layer_by_name('Water').tiles():
            Water((x*TILE_SIZE,y*TILE_SIZE), water_frames, self.all_sprites)
        
        # Trees
        for obj in tmx_data.get_layer_by_name('Trees'):
            Tree(
                pos=(obj.x,obj.y), 
                surf=obj.image, 
                groups=[self.all_sprites, self.collision_sprites, self.tree_sprites], 
                name=obj.name,
                player_add=self.player_add)
            
        # Wildflower
        for obj in tmx_data.get_layer_by_name('Decoration'):
            Wildflower((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites])
        
        # Collision
        for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
            Generic((x * TILE_SIZE, y * TILE_SIZE), pygame.Surface((TILE_SIZE, TILE_SIZE)), self.collision_sprites)

        # Player
        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name=="Start":
                self.player=Player(
                    pos=(obj.x,obj.y), 
                    group=self.all_sprites,
                    collision_sprites=self.collision_sprites,
                    tree_sprites=self.tree_sprites,
                    interaction=self.interaction_sprites,
                    soil_layer=self.soil_layer)
            
            
            
            if obj.name=='bed':
                # ИСПРАВЛЕНИЕ: Опечатка 'obj.heigth' заменена на 'obj.height'
                Interaction((obj.x,obj.y),(obj.width,obj.height), self.interaction_sprites,obj.name)
        
        # Ground
        Generic(
            pos=(0,0), 
            surf=pygame.image.load('sproutland-main/graphics/world/ground.png').convert_alpha(), 
            groups=self.all_sprites, 
            z=LAYERS['ground'])

    def player_add(self,item):
        self.player.item_inventory[item]+=1
        
    def run(self, dt):
        self.display_surface.fill((50, 100, 50))
        self.all_sprites.custom_draw(self.player)
        self.all_sprites.update(dt)
        self.overlay.display()
        if self.player.sleep:
            self.transition.play(dt)
        
        
        if self.raining:
            self.rain.update()
    
    # level.py
    # level.py

    def reset(self):
        
        self.soil_layer.remove_water()
        self.raining=randint(0,10)>3
        self.soil_layer.raining=self.raining
        
        if self.raining:
            self.soil_layer.water_all()
        
        for tree in self.tree_sprites.sprites():
            # ИСПРАВЛЕНИЕ: Проверяем, является ли объект деревом (имеет ли он атрибут apple_sprites)
            if hasattr(tree, 'apple_sprites'):
                # Теперь мы уверены, что tree является объектом Tree
                for apple in tree.apple_sprites.sprites():
                    apple.kill()
                tree.create_fruit()
class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface=pygame.display.get_surface()
        self.offset=pygame.math.Vector2()
        
    def custom_draw(self,player):
        self.offset.x=player.rect.centerx-SCREEN_WIDTH/2
        self.offset.y=player.rect.centery-SCREEN_HEIGHT/2

        for layer in LAYERS.values():
            for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery ):
                if sprite.z == layer:
                    offset_rect=sprite.rect.copy()
                    offset_rect.center-=self.offset
                    self.display_surface.blit(sprite.image,offset_rect)
