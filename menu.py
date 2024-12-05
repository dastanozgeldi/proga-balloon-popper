import sys

import pygame

import ui
from background import Background
from settings import *


class Menu:
    def __init__(self, surface, game):
        self.surface = surface
        self.game = game
        self.background = Background()
        self.click_sound = pygame.mixer.Sound(f"assets/sounds/slap.wav")
        self.reset_input()
        self.input_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 250, 200, 40)
        self.border_color = COLORS["buttons"]["default"]

    def reset_input(self):
        self.player_name = ""
        self.input_active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.input_rect.collidepoint(event.pos):
                self.input_active = True
            else:
                self.input_active = False
        
        if event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_RETURN:
                self.input_active = False
            elif event.key == pygame.K_BACKSPACE:
                self.player_name = self.player_name[:-1]
            elif len(self.player_name) < 15:  # Limit name length
                if event.unicode.isprintable():  # Only accept printable characters
                    self.player_name += event.unicode

    def draw(self):
        self.background.draw(self.surface)
        # draw title
        ui.draw_text(self.surface, GAME_TITLE, (SCREEN_WIDTH//2, 120), COLORS["title"], font=FONTS["big"],
                    shadow=True, shadow_color=(255,255,255), pos_mode="center")
        
        # draw input field
        pygame.draw.rect(self.surface, self.border_color, self.input_rect, 2)
        pygame.draw.rect(self.surface, (255, 255, 255), self.input_rect.inflate(-2, -2))
        text_surface = FONTS["small"].render(self.player_name, True, (0, 0, 0))
        self.surface.blit(text_surface, (self.input_rect.x + 5, self.input_rect.y + 5))
        
        # draw input label
        ui.draw_text(self.surface, "Enter your name:", (SCREEN_WIDTH//2, 220), 
                    COLORS["title"], font=FONTS["small"], pos_mode="center")

    def update(self):
        self.border_color = COLORS["buttons"]["second"] if self.input_active else COLORS["buttons"]["default"]
        self.draw()

        if ui.button(self.surface, 320, "START", click_sound=self.click_sound):
            self.game.player_name = self.player_name
            return "game"

        if ui.button(self.surface, 320+BUTTONS_SIZES[1]*1.5, "Quit", click_sound=self.click_sound):
            pygame.quit()
            sys.exit()
