import pygame
from random import randint, choice
from settings import *
from support import *
from timer import Timer

class Generic(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, z=LAYERS['main']):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = z
        self.hitbox = self.rect.copy()

class Water(Generic):
    def __init__(self, pos, frames, groups):
        self.frames = frames
        self.frame_index = 0
        
        super().__init__(
            pos=pos,
            surf=self.frames[self.frame_index],
            groups=groups,
            z=LAYERS['water']
        )
    
    def animate(self, dt):
        self.frame_index += 5 * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]
    
    def update(self, dt):
        self.animate(dt)

class Wildflower(Generic):
    def __init__(self, pos, surf, groups):
        super().__init__(pos, surf, groups)
        self.hitbox = self.rect.copy().inflate(-20, -self.rect.height * 0.9)

class Tree(Generic):
    def __init__(self, pos, surf, groups, name):
        super().__init__(pos, surf, groups)
        
        # Tree attributes
        self.name = name
        self.health = 5
        self.alive = True
        stump_path = f'sproutland-main/graphics/stumps/{"small" if name == "small" else "large"}.png'
        self.stump_surf = pygame.image.load(stump_path).convert_alpha()
        self.invul_timer = Timer(200)

        # Apples
        self.apple_surf = pygame.image.load('sproutland-main/graphics/fruit/apple.png')
        self.apple_pos = APPLE_POS[name]
        self.apple_sprites = pygame.sprite.Group()
        self.create_fruit()
    
    def create_fruit(self):
    # Create apples at the defined positions with lower chance
        for pos in self.apple_pos:
            if randint(0, 10) > 8:  # Only 20% chance to spawn each apple
                x = self.rect.left + pos[0]
                y = self.rect.top + pos[1]
                Apple((x, y), self.apple_surf, [self.apple_sprites, self.groups()[0]])

    def damage(self):
        # Damaging the tree
        self.health -= 1

        # Remove an apple
        if len(self.apple_sprites.sprites()) > 0:
            random_apple = choice(self.apple_sprites.sprites())
            Particle(
                pos=random_apple.rect.topleft,
                surf=random_apple.image,
                groups=self.groups(),
                z=LAYERS['fruit'])
            random_apple.kill()

    def check_death(self):
        if self.health <= 0:
            self.alive = False
            self.image = self.stump_surf
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
    
    def update(self, dt):
        self.invul_timer.update()
        self.check_death()

class Apple(Generic):
    def __init__(self, pos, surf, groups):
        super().__init__(pos, surf, groups, LAYERS['fruit'])
        self.hitbox = self.rect.copy().inflate(-15, -15)

class Particle(Generic):
    def __init__(self, pos, surf, groups, z, duration=200):
        super().__init__(pos, surf, groups, z)
        self.start_time = pygame.time.get_ticks()
        self.duration = duration
    
    def update(self, dt):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time > self.duration:
            self.kill()