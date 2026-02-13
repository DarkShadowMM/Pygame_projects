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

class Interaction(Generic):
    def __init__(self, pos, size, groups,name):
        surf=pygame.Surface(size)
        super().__init__(pos, surf, groups)
        self.name=name
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
    def __init__(self, pos, surf, groups, name, player_add):
        super().__init__(pos, surf, groups)
        
        # Tree attributes
        self.name = name
        self.health = 5
        self.alive = True
        stump_path = f'sproutland-main/graphics/stumps/{"small" if name == "Small" else "large"}.png'
        self.stump_surf = pygame.image.load(stump_path).convert_alpha()
        self.invul_timer = Timer(200)

        # Apples
        self.apple_surf = pygame.image.load('sproutland-main/graphics/fruit/apple.png').convert_alpha()
        self.apple_pos = APPLE_POS[name]
        self.apple_sprites = pygame.sprite.Group()
        self.player_add = player_add
        
        self.axe_sound=pygame.mixer.Sound('sproutland-main/audio/axe.mp3')

        # Create apples on the tree
        self.create_fruit()
    
    def create_fruit(self):
        """Create apples on the tree with random chance and correct z-layer."""
        for pos in self.apple_pos:
            if randint(0, 10) > 8:  # 80% chance to spawn each apple
                x = self.rect.left + pos[0]
                y = self.rect.top + pos[1]
                # apples visible above trees
                Apple((x, y), self.apple_surf, [self.apple_sprites, *self.groups()], z=LAYERS['fruit'])

    def damage(self):
        """Handle when the tree is hit by the axe."""
        self.health -= 1
        
        self.axe_sound.play()
        
        # Remove an apple and add to inventory
        if len(self.apple_sprites.sprites()) > 0:
            random_apple = choice(self.apple_sprites.sprites())
            # particle effect when apple drops
            Particle(
                pos=random_apple.rect.topleft,
                surf=random_apple.image,
                groups=self.groups(),
                z=LAYERS['fruit'])
            self.player_add('apple')
            random_apple.kill()

    def check_death(self):
        """Change image to stump if tree dies."""
        if self.health <= 0 and self.alive:
            # Particle(self.rect.topleft, self.image, self.groups()[0], LAYERS['fruit'],300)
            self.alive = False
            self.image = self.stump_surf
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
            self.player_add('wood')
            # Remove all apples when tree is dead
            for apple in self.apple_sprites.sprites():
                apple.kill()
    
    def update(self, dt):
        self.invul_timer.update()
        self.check_death()

class Apple(Generic):
    def __init__(self, pos, surf, groups, z=LAYERS['fruit']):
        super().__init__(pos, surf, groups, z)
        self.hitbox = self.rect.copy().inflate(-15, -15)

class Particle(Generic):
    def __init__(self, pos, surf, groups, z, duration=200):
        super().__init__(pos, surf, groups, z)
        self.start_time = pygame.time.get_ticks()
        self.duration = duration
        
        # Ensure pos is a Vector2 for accurate movement calculations
        self.pos = pygame.math.Vector2(self.rect.topleft)
        # Negative Y velocity moves upwards
        self.velocity = -80 
    
    def update(self, dt):
        """Particle moves upwards and disappears after duration."""
        current_time = pygame.time.get_ticks()
        
        # Update position based on velocity and delta time
        self.pos.y += self.velocity * dt 
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))
        
        if current_time - self.start_time > self.duration:
            self.kill()
            
# Вставьте это в конец sprites.py

class PoisonMushroom(Generic):
    def __init__(self, pos, surf, groups):
        super().__init__(pos, surf, groups, z=LAYERS['main'])
        # Уменьшаем хитбокс, чтобы игрок должен был наступить прямо на гриб
        self.hitbox = self.rect.copy().inflate(-20, -20)
        
    def update(self, dt):
        # Здесь можно добавить анимацию пульсации, если захотите
        pass
