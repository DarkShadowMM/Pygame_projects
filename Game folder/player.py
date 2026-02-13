import pygame
import os
from settings import *
from support import *
from timer import Timer

class Player(pygame.sprite.Sprite):
    # --- CHANGED: Added on_damage_callback to arguments ---
    def __init__(self, pos, group, collision_sprites, tree_sprites, interaction, soil_layer, toggle_shop, water_sprites, on_damage_callback):
        super().__init__(group)

        self.import_assets()
        self.status = 'down_idle'
        self.frame_index = 0
    
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center = pos)
        
        # --- NEW: Health System ---
        self.max_health = 3
        self.health = self.max_health
        # --- NEW: Mushroom Tracker ---
        self.mushrooms_eaten = 0
        # Callback function to tell the Level class that damage occurred
        self.on_damage_callback = on_damage_callback 
        
        self.hitbox = self.rect.copy().inflate((-126, -70))
        self.z = LAYERS['main']
        
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 200
        
        self.collision_sprites = collision_sprites
        self.water_sprites = water_sprites
        
        self.timers = {
            'tool use': Timer(350, self.use_tool),
            'tool switch': Timer(200),
            'seed use': Timer(350, self.use_seed),
            'seed switch': Timer(200),
            'fishing': Timer(800) 
        }
        
        self.tools = ['hoe', 'axe', 'water']
        self.tool_index = 0 
        self.selected_tool = self.tools[self.tool_index]
        
        self.seeds = ['corn', 'tomato']
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]
        
        self.item_inventory = {'wood': 0, 'apple': 0, 'corn': 0, 'tomato': 0}
        self.seed_inventory = {'corn': 5, 'tomato': 5}
        self.money = 200
        
        self.tree_sprites = tree_sprites
        self.interaction = interaction
        self.sleep = False
        self.soil_layer = soil_layer
        self.toggle_shop = toggle_shop
        self.target_pos = self.rect.center

    # --- NEW: Method to handle taking damage ---
    def take_damage(self, amount=1):
        if self.health > 0:
            # Store health before hit to know what heart to flicker
            old_health = self.health
            self.health -= amount
            if self.health < 0:
                self.health = 0
            
            # Notify the level that damage happened, passing the old health value
            self.on_damage_callback(old_health)

    def use_tool(self):
        if self.selected_tool == 'hoe':
            self.soil_layer.get_hit(self.target_pos)
        elif self.selected_tool == 'axe':
            for tree in self.tree_sprites.sprites():
                if tree.rect.collidepoint(self.target_pos):
                    tree.damage()
        elif self.selected_tool == 'water':
            self.soil_layer.water(self.target_pos)
            
    def get_target_pos(self):
        status_prefix = self.status.split('_')[0]
        if status_prefix in PLAYER_TOOL_OFFSET:
            self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[status_prefix]
           
    def use_seed(self):
        if self.seed_inventory[self.selected_seed] > 0:
            self.seed_inventory[self.selected_seed] -= 1
            self.soil_layer.plant_seed(self.target_pos, self.selected_seed)
        
    def import_assets(self):
        base_path = os.path.dirname(__file__)  
        graphics_path = os.path.join(base_path, 'sproutland-main', 'graphics', 'character') 
        self.animations = {
            'down': [], 'down_axe': [], 'down_hoe': [], 'down_idle': [], 'down_water': [], 
            'left': [], 'left_axe': [], 'left_hoe': [], 'left_idle': [], 'left_water': [], 
            'right': [], 'right_axe': [], 'right_hoe': [], 'right_idle': [], 'right_water': [], 
            'up': [], 'up_idle': [], 'up_axe': [], 'up_hoe': [], 'up_water': [], 
            "down_idle_swim": [],
            "fishing": [],
            "fishing_idle": [] 
        }
        
        for animation in self.animations.keys():
            full_path = os.path.join(graphics_path, animation)
            frames = import_folder(full_path)
            
            if "fishing" in animation:
                self.animations[animation] = [pygame.transform.scale_by(f, 4.0) for f in frames]
            else:
                self.animations[animation] = frames
    
    def animate(self, dt):
        animation_speed = 12 if 'fishing' in self.status else 4
        self.frame_index += animation_speed * dt
        
        if self.frame_index >= len(self.animations[self.status]):
            if self.status == 'fishing':
                self.status = 'fishing_idle'
                self.frame_index = 0
            else:
                self.frame_index = 0
        
        current_center = self.hitbox.center
        self.image = self.animations[self.status][int(self.frame_index)]
        self.rect = self.image.get_rect(center = current_center)

    def input(self):
        keys = pygame.key.get_pressed()

        # Выход из режима рыбалки при движении
        if self.status == 'fishing_idle':
            if keys[pygame.K_UP] or keys[pygame.K_DOWN] or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
                self.status = 'down_idle'

        if not self.timers['tool use'].active and not self.timers['fishing'].active and not self.sleep:
            self.direction.x = 0
            self.direction.y = 0

            if keys[pygame.K_UP]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_DOWN]:
                self.direction.y = 1
                self.status = 'down' 
            
            if keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.status = 'left' 
            elif keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.status = 'right'
                
                
            if keys[pygame.K_s]:
                self.timers['seed use'].activate()
                self.direction=pygame.math.Vector2()
                self.frame_index=0
                
            if keys[pygame.K_SPACE]:
                self.timers['tool use'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0

            if keys[pygame.K_b]:
                self.timers['fishing'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0

            # ОТКРЫТИЕ МЕНЮ НА ENTER
            if keys[pygame.K_RETURN]:
                self.toggle_shop()
                
            if keys[pygame.K_q] and not self.timers['tool switch'].active:
                self.timers['tool switch'].activate()
                self.tool_index = (self.tool_index + 1) % len(self.tools)
                self.selected_tool = self.tools[self.tool_index]

            # --- NEW: Test key to take damage (Remove later) ---
            if keys[pygame.K_t]:
                 # Simple debounce to prevent taking 60 damage per second
                if not hasattr(self, '_test_damage_pressed') or not self._test_damage_pressed:
                    self.take_damage(1)
                    self._test_damage_pressed = True
            else:
                self._test_damage_pressed = False

    def get_status(self):
        is_swimming = False
        for water in self.water_sprites:
            if water.rect.colliderect(self.hitbox):
                is_swimming = True
                break
        
        if is_swimming:
            self.status = 'down_idle_swim'
            self.speed = 100
        else:
            self.speed = 200
            
            if self.timers['fishing'].active:
                self.status = 'fishing'
            elif self.status == 'fishing_idle' and self.direction.magnitude() == 0:
                pass 
            elif self.timers['tool use'].active:
                self.status = self.status.split('_')[0] + '_' + self.selected_tool
            else:
                if self.direction.magnitude() == 0:
                    if 'idle' not in self.status:
                        self.status = self.status.split('_')[0] + '_idle'

    def collision(self, direction):
        for sprite in self.collision_sprites.sprites():
            if hasattr(sprite, 'hitbox'):
                if sprite.hitbox.colliderect(self.hitbox):
                    if direction == 'horizontal':
                        if self.direction.x > 0: self.hitbox.right = sprite.hitbox.left
                        if self.direction.x < 0: self.hitbox.left = sprite.hitbox.right
                    if direction == 'vertical':
                        if self.direction.y > 0: self.hitbox.bottom = sprite.hitbox.top
                        if self.direction.y < 0: self.hitbox.top = sprite.hitbox.bottom
        self.pos.x = self.hitbox.centerx
        self.pos.y = self.hitbox.centery
                     
    def move(self, dt):
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()
        
        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.collision('horizontal')
        
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.collision('vertical')
        
        self.rect.center = self.hitbox.center
        
    def update(self, dt):
        self.input()
        for timer in self.timers.values(): timer.update()
        self.get_status()
        self.get_target_pos()
        self.move(dt)
        self.animate(dt)
