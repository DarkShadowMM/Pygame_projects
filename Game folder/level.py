import pygame
from player import Player
from settings import *
from overlay import Overlay
from sprites import Generic, Water, Wildflower, Tree, Interaction, Particle,PoisonMushroom
from pytmx.util_pygame import load_pygame
from support import *
from transition import Transition
from soil import SoilLayer
from sky import *
from random import randint
from menu import Menu
# --- CHANGED: Import Timer ---
from timer import Timer 

class Level:
    def __init__(self):
        # Основные настройки поверхности и групп
        self.display_surface = pygame.display.get_surface()
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group()
        self.tree_sprites = pygame.sprite.Group()
        self.interaction_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()
        self.mushroom_sprites = pygame.sprite.Group()
        self.mushroom_surf = pygame.image.load('sproutland-main/Poison_m.png').convert_alpha()
        self.game_over = False
        self.font = pygame.font.Font('sproutland-main/font/LycheeSoda.ttf', 100)
        self.sub_font = pygame.font.Font('sproutland-main/font/LycheeSoda.ttf', 50)
        self.spawn_mushrooms(15) # Укажите желаемое количество грибов
        self.shop_active = False
        self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites)
        
        # --- NEW: UI Damage Flickering Variables ---
        self.damage_flicker_timer = Timer(1000) # Flicker for 1 second
        self.is_flickering = False
        self.heart_to_flicker = None # The image of the heart BEFORE damage
        self.flicker_frequency = 100 # How fast it blinks (ms)

        self.setup()
        
        self.overlay = Overlay(self.player)
        self.transition = Transition(self.reset, self.player)
        self.rain = Rain(self.all_sprites)
        self.raining = randint(0, 10) > 3
        self.soil_layer.raining = self.raining
        self.sky = Sky()
        self.menu = Menu(self.player, self.toggle_shop)
        
        # --- СОЗДАНИЕ ИНФОРМАЦИОННОЙ ПАНЕЛИ ---
        # --- CHANGED: Modified UI loading process ---
        try:
            # 1. Load base assets
            self.info_surf_base = pygame.image.load('sproutland-main/info.png').convert_alpha()
            char_surf = pygame.image.load('sproutland-main/common_e.png').convert_alpha()
            char_surf = pygame.transform.scale(char_surf, (25, 29))
            
            # 2. Load Heart Assets (Assuming they are in sproutland-main/graphics/)
            # Scale them up slightly to fit nicely in the UI box (e.g., 2x scaling)
            heart_scale = 2.35
            self.heart_full = pygame.image.load('sproutland-main/heart_1.png').convert_alpha()
            self.heart_full = pygame.transform.scale_by(self.heart_full, heart_scale)
            
            self.heart_half = pygame.image.load('sproutland-main/heart_2.png').convert_alpha()
            self.heart_half = pygame.transform.scale_by(self.heart_half, heart_scale)
            
            self.heart_empty = pygame.image.load('sproutland-main/heart_3.png').convert_alpha()
            self.heart_empty = pygame.transform.scale_by(self.heart_empty, heart_scale)

            # 3. Create the static background part of the UI (bg + character)
            self.ui_base = self.info_surf_base.copy()
            self.ui_base.blit(char_surf, (16,16))
            
            # Heart position on the unscaled UI surface
            self.heart_pos = (63, 19) 

        except FileNotFoundError as e:
            print(f"UI Asset missing: {e}")
            # Backup simple colored box if files fail
            self.ui_base = pygame.Surface((100, 30))
            self.ui_base.fill((150, 100, 50))
            self.heart_full = self.heart_half = self.heart_empty = pygame.Surface((10,10))
            self.heart_full.fill('red')
            self.heart_half.fill('orange')
            self.heart_empty.fill('black')
            self.heart_pos = (40, 10)

        self.success = pygame.mixer.Sound('sproutland-main/audio/success.wav')
        self.success.set_volume(0.3)
        
        # Sound for getting hurt (optional, you can add one)
        # self.hurt_sound = pygame.mixer.Sound('sproutland-main/audio/hurt.wav')
    # Добавить новый метод в класс Level:
    def spawn_mushrooms(self, amount):
        for _ in range(amount):
            # Генерируем случайные координаты в пределах карты (настройте под размер вашей карты)
            # Обычно это от 0 до TILE_SIZE * количество тайлов
            x = randint(500, 2000) 
            y = randint(500, 2000)
            
            # Создаем группу для грибов, если её еще нет, или просто в all_sprites
            PoisonMushroom((x, y), self.mushroom_surf, [self.all_sprites])
    def setup(self):
        tmx_data = load_pygame('sproutland-main/data/new_map.tmx')
        
        for layer in ['HouseFloor', 'HouseFurnitureBottom']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, LAYERS['house bottom'])
                              
        for layer in ['HouseWalls', 'HouseFurnitureTop']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, [self.all_sprites, self.collision_sprites])
        
        for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
            Generic((x * TILE_SIZE, y * TILE_SIZE), surf, [self.all_sprites, self.collision_sprites])
            
        water_frames = import_folder('sproutland-main/graphics/water')
        for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
            Water((x * TILE_SIZE, y * TILE_SIZE), water_frames, [self.all_sprites, self.water_sprites])
        
        for obj in tmx_data.get_layer_by_name('Trees'):
            Tree(
                pos=(obj.x, obj.y), 
                surf=obj.image, 
                groups=[self.all_sprites, self.collision_sprites, self.tree_sprites], 
                name=obj.name,
                player_add=self.player_add)
            
        for obj in tmx_data.get_layer_by_name('Decoration'):
            Wildflower((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites])
        
        for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
            Generic((x * TILE_SIZE, y * TILE_SIZE), pygame.Surface((TILE_SIZE, TILE_SIZE)), self.collision_sprites)

        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name == "Start":
                self.player = Player(
                    pos=(obj.x, obj.y), 
                    group=self.all_sprites,
                    collision_sprites=self.collision_sprites,
                    tree_sprites=self.tree_sprites,
                    interaction=self.interaction_sprites,
                    soil_layer=self.soil_layer,
                    toggle_shop=self.toggle_shop,
                    water_sprites=self.water_sprites,
                    # --- CHANGED: Pass the damage callback ---
                    on_damage_callback=self.on_player_damage 
                )
            
            if obj.name in ['bed', 'Trader']:
                Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)
        
        Generic(
            pos=(0, 0), 
            surf=pygame.image.load('sproutland-main/graphics/world/ground.png').convert_alpha(), 
            groups=self.all_sprites, 
            z=LAYERS['ground'])

    # --- NEW: Callback function called by Player when damaged ---
    def on_player_damage(self, old_health):
        # Determine which heart image we should flicker (the state BEFORE damage)
        if old_health > 2:
            self.heart_to_flicker = self.heart_full
        elif old_health > 1:
            self.heart_to_flicker = self.heart_half
        else:
            # Should rarely happen if max health is 3, but good fallback
            self.heart_to_flicker = self.heart_empty 
            
        self.is_flickering = True
        self.damage_flicker_timer.activate()
        # self.hurt_sound.play() # Optional sound

    def player_add(self, item):
        self.player.item_inventory[item] += 1
        self.success.play()
    
    def toggle_shop(self):
        self.shop_active = not self.shop_active

    # --- NEW: Method to draw the dynamic UI ---
    def draw_ui(self):
        # 1. Start with the base UI (bg + char)
        current_ui = self.ui_base.copy()
        
        # 2. Determine Heart Logic
        current_heart_image = None

        if self.is_flickering:
            # Calculate flicker state based on time
            current_time = pygame.time.get_ticks()
            # If result is < half frequency, draw the image, else draw nothing (blink)
            if (current_time % self.flicker_frequency) < (self.flicker_frequency / 2):
                 current_heart_image = self.heart_to_flicker
            else:
                current_heart_image = None # Don't draw anything this frame

        else:
            # Standard state: show heart based on current health
            if self.player.health > 2:
                current_heart_image = self.heart_full
            elif self.player.health > 0:
                 current_heart_image = self.heart_half
            else:
                 current_heart_image = self.heart_empty

        # 3. Blit the determined heart onto the unscaled UI surface
        if current_heart_image:
            # Center the heart image vertically relative to the defined position
            y_offset = self.heart_pos[1] + (self.heart_full.get_height() // 2) - (current_heart_image.get_height() // 2)
            current_ui.blit(current_heart_image, (self.heart_pos[0], y_offset))

        # 4. Scale the final composite UI and draw to screen
        # Scaling by 2.0 as in your original code
        final_ui_surface = pygame.transform.scale_by(current_ui, 2.0)
        self.display_surface.blit(final_ui_surface, (20, 20))

    def run(self, dt):
        self.display_surface.fill((50, 100, 50))
        self.all_sprites.custom_draw(self.player)
        
        # Update flicker timer
        if self.is_flickering:
            self.damage_flicker_timer.update()
            if not self.damage_flicker_timer.active:
                self.is_flickering = False

        if self.shop_active:
            self.menu.update()
        else:
            self.all_sprites.update(dt)
            self.plant_collision()
            self.mushroom_collision()
        self.display_surface.fill((50, 100, 50))
        self.all_sprites.custom_draw(self.player)
        
        if self.game_over:
            self.display_game_over()
            # Optional: Allow restart by pressing Enter
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RETURN]:
                # You could call a full reset here if desired
                pass
            return # Stop updating everything else    
        self.overlay.display()
        
        # --- CHANGED: Call the new dynamic UI drawing method ---
        self.draw_ui()
        
        if self.player.sleep:
            self.transition.play(dt)
        
        if self.raining and not self.shop_active:
            self.rain.update()
            
        self.sky.display(dt)

    def plant_collision(self):
        if self.soil_layer.plant_sprites:
            for plant in self.soil_layer.plant_sprites.sprites():
                if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
                    self.player_add(plant.plant_type)
                    plant.kill()
                    Particle(plant.rect.topleft, plant.image, self.all_sprites, z=LAYERS['main'])
                    self.soil_layer.grid[plant.rect.centery // TILE_SIZE][plant.rect.centerx // TILE_SIZE].remove('P')
        
    def spawn_mushrooms(self, amount):
        for _ in range(amount):
            # Random position within map bounds (adjust numbers based on your map size)
            x = randint(400, 2000)
            y = randint(400, 2000)
            PoisonMushroom((x, y), self.mushroom_surf, [self.all_sprites, self.mushroom_sprites])

    def mushroom_collision(self):
        if not self.game_over:
            for sprite in self.mushroom_sprites.sprites():
                if sprite.hitbox.colliderect(self.player.hitbox):
                    sprite.kill()
                    self.player.take_damage(1)
                    self.player.mushrooms_eaten += 1
                    
                    if self.player.mushrooms_eaten >= 3:
                        self.game_over = True

    def display_game_over(self):
        # Darken the background
        black_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        black_surf.set_alpha(150)
        self.display_surface.blit(black_surf, (0,0))

        # Game Over Text
        text_surf = self.font.render('GAME OVER', False, 'White')
        text_rect = text_surf.get_rect(center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50))
        
        # Reason Text
        reason_surf = self.sub_font.render('Too many poisonous mushrooms!', False, '#ff6666')
        reason_rect = reason_surf.get_rect(center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50))

        self.display_surface.blit(text_surf, text_rect)
        self.display_surface.blit(reason_surf, reason_rect)
    def reset(self):
        # --- NEW: Reset health on new day ---
        self.player.health = self.player.max_health
        self.is_flickering = False
        
        self.soil_layer.update_plants()
        self.soil_layer.remove_water()
        self.raining = randint(0, 10) > 3
        self.soil_layer.raining = self.raining
        
        if self.raining:
            self.soil_layer.water_all()
        
        for tree in self.tree_sprites.sprites():
            if hasattr(tree, 'apple_sprites'):
                for apple in tree.apple_sprites.sprites():
                    apple.kill()
                tree.create_fruit()
                
        self.sky.start_color = [255, 255, 255]
        self.sky.current_stage = 2 
                    
class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()
        
    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

        for layer in LAYERS.values():
            for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)
