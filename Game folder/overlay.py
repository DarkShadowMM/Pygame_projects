import pygame
from settings import *

class Overlay:
    def __init__(self,player):

        self.display_surface=pygame.display.get_surface()
        self.player=player

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

    def display(self):
        tool_surf = self.tools_surf[self.player.selected_tool] 
        tool_rect = tool_surf.get_rect(midbottom = OVERPLAY_POSITITON['tool'])
        self.display_surface.blit(tool_surf,tool_rect)

        seed_surf = self.seeds_surf[self.player.selected_seed] 
        seed_rect = seed_surf.get_rect(midbottom = OVERPLAY_POSITITON['seed'])
        self.display_surface.blit(seed_surf,seed_rect)