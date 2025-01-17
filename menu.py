import sys
import time

import pygame
import requests

import ui
from background import Background
from settings import *


class Menu:
    def __init__(self, surface, game):
        self.window_width, self.window_height = pygame.display.get_window_size()
        self.surface = surface
        self.game = game
        self.background = Background((self.window_width, self.window_height))
        self.click_sound = pygame.mixer.Sound(f"assets/sounds/slap.wav")
        self.reset_input()
        self.input_rect = pygame.Rect(self.window_width // 2 - 300, 240, 600, 50)
        self.border_color = COLORS["buttons"]["default"]
        self.show_leaderboard = False
        self.leaderboard_fetched = False
        self.leaderboard_data = []
        self.show_credits = False
        self.show_settings = False

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
            if not self.leaderboard_fetched:
                response = requests.get("https://ozgeldi.tech/api/isjo")
                raw = response.json()
                self.leaderboard_fetched = True
                self.leaderboard_data = [
                    f"{index + 1}. {item['player_name']}: {item['score']}"
                    for index, item in enumerate(raw["data"])
                ]
            ui.draw_title_text(self.surface, "Leaderboard", x=self.window_width // 2)
            ui.draw_small_texts(
                self.surface, self.leaderboard_data, x=self.window_width // 2
            )
        elif self.show_credits:
            ui.draw_title_text(self.surface, "Credits", x=self.window_width // 2)
            ui.draw_small_texts(
                self.surface,
                [
                    "Dastan Ozgeldi",
                    "Alikhan Shikhiyev",
                    "Aizhan Abisheva",
                    "Alikhan Makhan"
                ],
                x=self.window_width // 2,
            )
        elif self.show_settings:
            ui.draw_title_text(self.surface, "Settings", x=self.window_width // 2)
            
            # Global declarations at the start
            global MUSIC_ENABLED, FULLSCREEN_MODE

            if ui.toggle_button(
                self.surface,
                self.window_width // 2 + 50,
                250,
                60,
                30,
                MUSIC_ENABLED,
                "Music"
            ):
                MUSIC_ENABLED = not MUSIC_ENABLED
                if MUSIC_ENABLED:
                    pygame.mixer.music.play(-1)
                else:
                    pygame.mixer.music.stop()

            if ui.toggle_button(
                self.surface,
                self.window_width // 2 + 50,
                300,
                60,
                30,
                FULLSCREEN_MODE,
                "Fullscreen"
            ):
                FULLSCREEN_MODE = not FULLSCREEN_MODE
                self.apply_screen_mode()
                self.window_width, self.window_height = pygame.display.get_window_size()
        else:
            # Draw main menu
            ui.draw_title_text(
                self.surface,
                GAME_TITLE,
                x=self.window_width // 2,
            )

            # Draw improved input field
            pygame.draw.rect(
                self.surface, self.border_color, self.input_rect, 3, border_radius=10
            )
            pygame.draw.rect(
                self.surface,
                (255, 255, 255),
                self.input_rect.inflate(-3, -3),
                border_radius=10,
            )

            # Draw text with cursor
            text_surface = FONTS["small"].render(self.player_name, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=self.input_rect.center)
            self.surface.blit(text_surface, text_rect)

            # Add blinking cursor if input is active
            if self.input_active and time.time() % 1 > 0.5:  # Blink every 0.5 seconds
                cursor_x = text_rect.right + 2
                if not self.player_name:  # Center cursor if no text
                    cursor_x = self.input_rect.centerx
                pygame.draw.line(
                    self.surface,
                    (0, 0, 0),
                    (cursor_x, self.input_rect.centery - 10),
                    (cursor_x, self.input_rect.centery + 10),
                    2,
                )

            # Draw input label
            ui.draw_text(
                self.surface,
                "Enter your name:",
                (self.window_width // 2, 220),
                COLORS["title"],
                font=FONTS["small"],
                pos_mode="center",
            )

    def update(self):
        self.border_color = (
            COLORS["buttons"]["second"]
            if self.input_active
            else COLORS["buttons"]["default"]
        )
        self.draw()

        if self.show_leaderboard:
            if ui.back_button(self.surface, 50, 100):
                self.show_leaderboard = False
                return "menu"
        elif self.show_credits:
            if ui.back_button(self.surface, 50, 100):
                self.show_credits = False
                return "menu"
        elif self.show_settings:
            if ui.back_button(self.surface, 50, 100):
                self.show_settings = False
                return "menu"
        else:
            # Only enable the Start button if there's a username
            if ui.button(
                self.surface,
                320,
                "Start",
                click_sound=self.click_sound if self.player_name.strip() else None,
                pos_x=self.window_width,
                disabled=not self.player_name.strip()
            ):
                self.game.player_name = self.player_name
                return "game"

            if ui.button(
                self.surface,
                320 + BUTTONS_SIZES[1] * 1.25,
                "Leaderboard",
                click_sound=self.click_sound,
                pos_x=self.window_width,
            ):
                self.show_leaderboard = True

            if ui.button(
                self.surface,
                320 + BUTTONS_SIZES[1] * 2.5,
                "Credits",
                click_sound=self.click_sound,
                pos_x=self.window_width,
            ):
                self.show_credits = True

            if ui.button(
                self.surface,
                320 + BUTTONS_SIZES[1] * 3.75,
                "Settings",
                click_sound=self.click_sound,
                pos_x=self.window_width,
            ):
                self.show_settings = True

            if ui.button(
                self.surface,
                320 + BUTTONS_SIZES[1] * 5,
                "Quit",
                click_sound=self.click_sound,
                pos_x=self.window_width,
            ):
                pygame.quit()
                sys.exit()

    def apply_screen_mode(self):
        global FULLSCREEN_MODE
        current_w, current_h = pygame.display.get_window_size()
        
        if FULLSCREEN_MODE:
            # Store current window size before going fullscreen
            self.window_size_before_fullscreen = (current_w, current_h)
            # Get the current display info
            display_info = pygame.display.Info()
            # Set fullscreen at native resolution
            self.surface = pygame.display.set_mode(
                (display_info.current_w, display_info.current_h),
                pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
            )
        else:
            # Restore previous window size
            size = getattr(self, 'window_size_before_fullscreen', (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surface = pygame.display.set_mode(
                size,
                pygame.HWSURFACE | pygame.DOUBLEBUF
            )
        
        # Update window dimensions
        self.window_width, self.window_height = pygame.display.get_window_size()
        
        # Update game references
        if hasattr(self, 'game'):
            self.game.surface = self.surface
            self.game.window_size = (self.window_width, self.window_height)
        
        # Only recreate background if dimensions changed
        if (current_w, current_h) != (self.window_width, self.window_height):
            self.background = Background((self.window_width, self.window_height))
            if hasattr(self, 'game'):
                self.game.background = Background((self.window_width, self.window_height))
