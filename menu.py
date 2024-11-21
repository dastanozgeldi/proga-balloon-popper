import sys

import pygame

import ui
from background import Background
from settings import *


class Menu:
    def __init__(self, surface):
        self.surface = surface
        self.background = Background()
        self.click_sound = pygame.mixer.Sound(f"assets/sounds/slap.wav")


    def draw(self):
        self.background.draw(self.surface)
        # draw title
        ui.draw_text(self.surface, GAME_TITLE, (SCREEN_WIDTH//2, 120), COLORS["title"], font=FONTS["big"],
                    shadow=True, shadow_color=(255,255,255), pos_mode="center")


    def update(self):
        self.draw()
        if ui.button(self.surface, 320, "START", click_sound=self.click_sound):
            return "game"

        if ui.button(self.surface, 320+BUTTONS_SIZES[1]*1.5, "Quit", click_sound=self.click_sound):
            pygame.quit()
            sys.exit()
