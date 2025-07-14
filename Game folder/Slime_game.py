import pygame
import sys


pygame.init()

# Game window
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Slime Animation")

# Load sprite sheet
slime_sheet = pygame.image.load("slime_sheet_v4.png").convert_alpha()
goblin_sheet=pygame.image.load("goblin_sheet_1.png").convert_alpha()
bg=pygame.image.load("Premium Vector _ Pixel game background with ground grass sky and props and character.jpeg").convert_alpha()


m = 1
v = 10
jump = 0
SPRITE_SIZE = 16
SPRITE_SPACING = 2
SCALED_SIZE = 64
FPS = 10


def get_animation_frames(sheet, row, frame_count):
    frames = []
    for i in range(frame_count):
        x = i * (SPRITE_SIZE + SPRITE_SPACING)
        y = row * (SPRITE_SIZE + SPRITE_SPACING)
        frame = sheet.subsurface(pygame.Rect(x, y, SPRITE_SIZE, SPRITE_SIZE))
        frame = pygame.transform.scale(frame, (SCALED_SIZE, SCALED_SIZE))
        frames.append(frame)
    return frames



slime_run_right = get_animation_frames(slime_sheet, row=1, frame_count=5)
slime_run_left = [pygame.transform.flip(frame, True, False) for frame in slime_run_right]


goblin_appear=get_animation_frames(goblin_sheet, row=0, frame_count=4)
goblin_appear = [pygame.transform.flip(frame, True, False) for frame in goblin_appear]

# 
current_frames = slime_run_right
frame_index = 0
goblin_index = 0
goblin_x = 500
goblin_y = HEIGHT // 2
x_pos = 100
y_pos = HEIGHT // 2
velocity = 20
direction = "right"

clock = pygame.time.Clock()


running = True
while running:
    clock.tick(FPS)

  
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        x_pos -= velocity
        direction = "left"
        current_frames = slime_run_left
    elif keys[pygame.K_RIGHT]:
        x_pos += velocity
        direction = "right"
        current_frames = slime_run_right


    if jump == 0:
        if keys[pygame.K_SPACE]:
            jump = 1
 
    if jump == 1:
        k = 0.25 * m * v**2  
        y_pos -= k  
        v -= 1  
        if v < 0:
            m = -1  
        if v == -11:
            m = 1  
            v = 10
            jump = 0 
   
 
    frame_index = (frame_index + 1) % len(current_frames)
    goblin_index = (goblin_index + 1) % len(goblin_appear)
 
    screen.fill((20, 20, 30))
    screen.blit(bg, (4, 0))  
    screen.blit(current_frames[frame_index], (x_pos, y_pos))
    screen.blit(goblin_appear[goblin_index], (goblin_x, goblin_y))
    
    

    pygame.display.update()

pygame.quit()
sys.exit()