import sys
import time

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
        self.input_rect = pygame.Rect(SCREEN_WIDTH//2-300, 240, 600, 50)
        self.border_color = COLORS["buttons"]["default"]
        self.show_leaderboard = False
        self.show_credits = False


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
        
        if self.show_leaderboard:
            ui.draw_text(self.surface, "Leaderboard", (SCREEN_WIDTH//2, 120), COLORS["title"], 
                        font=FONTS["big"], shadow=True, shadow_color=(255,255,255), pos_mode="center")
            ui.draw_text(self.surface, "1. work in progress", (SCREEN_WIDTH//2, 200), 
                        COLORS["title"], font=FONTS["small"], shadow=True, shadow_color=(255,255,255), pos_mode="center")
        elif self.show_credits:
            # Draw credits page
            ui.draw_text(self.surface, "Credits", (SCREEN_WIDTH//2, 120), COLORS["title"], 
                        font=FONTS["big"], shadow=True, shadow_color=(255,255,255), pos_mode="center")
            ui.draw_text(self.surface, "Game made by: Dastan Ozgeldi", (SCREEN_WIDTH//2, 200), 
                        COLORS["title"], font=FONTS["small"], shadow=True, shadow_color=(255,255,255), pos_mode="center")
            ui.draw_text(self.surface, "Game design: Alikhan Shikhiyev", (SCREEN_WIDTH//2, 235),
                        COLORS['title'], font=FONTS['small'], shadow=True, shadow_color=(255,255,255), pos_mode="center")
        else:
            # Draw main menu
            ui.draw_text(self.surface, GAME_TITLE, (SCREEN_WIDTH//2, 120), COLORS["title"], 
                        font=FONTS["big"], shadow=True, shadow_color=(255,255,255), pos_mode="center")
            
            # Draw improved input field
            pygame.draw.rect(self.surface, self.border_color, self.input_rect, 3, border_radius=10)
            pygame.draw.rect(self.surface, (255, 255, 255), self.input_rect.inflate(-3, -3), border_radius=10)

            # Draw text with cursor
            text_surface = FONTS["small"].render(self.player_name, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=self.input_rect.center)
            self.surface.blit(text_surface, text_rect)
            
            # Add blinking cursor if input is active
            if self.input_active and time.time() % 1 > 0.5:  # Blink every 0.5 seconds
                cursor_x = text_rect.right + 2
                if not self.player_name:  # Center cursor if no text
                    cursor_x = self.input_rect.centerx
                pygame.draw.line(self.surface, (0, 0, 0),
                               (cursor_x, self.input_rect.centery - 10),
                               (cursor_x, self.input_rect.centery + 10), 2)
            
            # Draw input label
            ui.draw_text(self.surface, "Enter your name:", (SCREEN_WIDTH//2, 220), 
                        COLORS["title"], font=FONTS["small"], pos_mode="center")

    def update(self):
        self.border_color = COLORS["buttons"]["second"] if self.input_active else COLORS["buttons"]["default"]
        self.draw()

        if self.show_leaderboard:
            if ui.back_button(self.surface, 50, 50):
                self.show_leaderboard = False
                return "menu"
        elif self.show_credits:
            if ui.back_button(self.surface, 50, 50):
                self.show_credits = False
                return "menu"
        else:
            if ui.button(self.surface, 320, "Start", click_sound=self.click_sound):
                self.game.player_name = self.player_name
                return "game"
            
            if ui.button(self.surface, 320+BUTTONS_SIZES[1]*1.25, "Leaderboard", click_sound=self.click_sound):
                self.show_leaderboard = True

            if ui.button(self.surface, 320+BUTTONS_SIZES[1]*2.5, "Credits", click_sound=self.click_sound):
                self.show_credits = True

            if ui.button(self.surface, 320+BUTTONS_SIZES[1]*3.75, "Quit", click_sound=self.click_sound):
                pygame.quit()
                sys.exit()
