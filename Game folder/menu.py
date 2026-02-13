import pygame
from timer import Timer
from settings import *

class Menu:
    def __init__(self, player, toggle_menu):
        self.player = player
        self.toggle_menu = toggle_menu
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font('sproutland-main/font/LycheeSoda.ttf', 30)
        
        # Размеры и отступы
        self.width = 400
        self.space = 10
        self.padding = 12
        
        self.options = list(self.player.item_inventory.keys()) + list(self.player.seed_inventory.keys())
        self.sell_border = len(self.player.item_inventory) # Исправленная граница
        self.setup()
        self.index = 0
        self.timer = Timer(200)
        
    def setup(self):
        self.text_surfs = []
        self.total_height = 0

        for item in self.options:
            text_surf = self.font.render(item.capitalize(), False, '#333333')
            self.text_surfs.append(text_surf)
            self.total_height += text_surf.get_height() + (self.padding * 2)
            
        self.total_height += (len(self.text_surfs) - 1) * self.space  
        self.menu_top = SCREEN_HEIGHT / 2 - self.total_height / 2
        self.main_rect = pygame.Rect(SCREEN_WIDTH / 2 - self.width / 2, self.menu_top, self.width, self.total_height)
        
        self.buy_text = self.font.render("BUY", False, '#27ae60')
        self.sell_text = self.font.render("SELL", False, '#c0392b')
        
    def display_money(self):
        amount_surf = self.font.render(f'Balance: ${self.player.money}', False, '#333333')
        amount_rect = amount_surf.get_rect(midbottom=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 35))

        bg_rect = amount_rect.inflate(40, 20)
        pygame.draw.rect(self.display_surface, 'White', bg_rect, 0, 10)
        pygame.draw.rect(self.display_surface, '#dddddd', bg_rect, 3, 10)
        self.display_surface.blit(amount_surf, amount_rect)
       
    def show_entry(self, text_surf, amount, top, selected):
        bg_rect = pygame.Rect(self.main_rect.left, top, self.width, text_surf.get_height() + (self.padding * 2))
        
        # Отрисовка строки
        color = 'White' if selected else '#f9f9f9'
        pygame.draw.rect(self.display_surface, color, bg_rect, 0, 8)

        text_rect = text_surf.get_rect(midleft=(self.main_rect.left + 30, bg_rect.centery))
        self.display_surface.blit(text_surf, text_rect)

        amount_surf = self.font.render(f'x{amount}', False, '#666666')
        amount_rect = amount_surf.get_rect(midright=(self.main_rect.right - 30, bg_rect.centery))
        self.display_surface.blit(amount_surf, amount_rect)
       
        if selected:
            pygame.draw.rect(self.display_surface, '#3498db', bg_rect, 4, 8)
            # Отображение действия по центру
            if self.index < self.sell_border:
                pos_rect = self.sell_text.get_rect(center=(self.main_rect.centerx, bg_rect.centery))
                self.display_surface.blit(self.sell_text, pos_rect)
            else:
                pos_rect = self.buy_text.get_rect(center=(self.main_rect.centerx, bg_rect.centery))
                self.display_surface.blit(self.buy_text, pos_rect)
       
    def input(self):    
        keys = pygame.key.get_pressed()
        self.timer.update()

        # Закрыть меню на Enter или Escape
        if (keys[pygame.K_ESCAPE] or keys[pygame.K_RETURN]) and not self.timer.active:
            self.toggle_menu()
            self.timer.activate()
            
        if not self.timer.active:
            if keys[pygame.K_UP]:
                self.index -= 1
                self.timer.activate()
            if keys[pygame.K_DOWN]:
                self.index += 1
                self.timer.activate()
                
            if keys[pygame.K_SPACE]:
                self.timer.activate()
                current_item = self.options[self.index]

                if self.index < self.sell_border: # Продажа
                    if self.player.item_inventory[current_item] > 0:
                        self.player.item_inventory[current_item] -= 1
                        self.player.money += SALE_PRICES[current_item]
                else: # Покупка
                    seed_price = PURCHASE_PRICES[current_item]
                    if self.player.money >= seed_price:
                        self.player.seed_inventory[current_item] += 1
                        self.player.money -= seed_price

        if self.index < 0: self.index = len(self.options) - 1
        if self.index > len(self.options) - 1: self.index = 0

    def update(self):
        self.input()
        self.display_money()
        for text_index, text_surf in enumerate(self.text_surfs):
            top = self.main_rect.top + text_index * (text_surf.get_height() + (self.padding * 2) + self.space)
            amount_list = list(self.player.item_inventory.values()) + list(self.player.seed_inventory.values())
            amount = amount_list[text_index]
            self.show_entry(text_surf, amount, top, self.index == text_index)