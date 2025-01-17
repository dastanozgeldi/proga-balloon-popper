import datetime
import random
import time

import requests
import cv2
import pygame

import ui
from background import Background
from balloon import Balloon
from bee import Bee
from hand import Hand
from hand_tracking import HandTracking
from settings import *


class Game:
    def __init__(self, surface, menu):
        self.window_size = pygame.display.get_window_size()
        self.surface = surface
        self.menu = menu
        self.background = Background(self.window_size)
        self.score_saved = False
        self.player_name = ""

        # Load camera
        self.cap = cv2.VideoCapture(0)

        self.sounds = {}
        self.sounds["slap"] = pygame.mixer.Sound(f"assets/sounds/slap.wav")
        self.sounds["slap"].set_volume(SOUNDS_VOLUME)
        self.sounds["screaming"] = pygame.mixer.Sound(f"assets/sounds/screaming.wav")
        self.sounds["screaming"].set_volume(SOUNDS_VOLUME)

        self.paused = False

    def reset(self):  # reset all the needed variables
        self.hand_tracking = HandTracking(self.window_size)
        self.hand = Hand(self.window_size)
        self.insects = []
        self.insects_spawn_timer = 0
        self.score = 0
        self.game_start_time = time.time()
        self.score_saved = False

    def spawn_insects(self):
        t = time.time()
        if t > self.insects_spawn_timer:
            self.insects_spawn_timer = t + BALLOONS_SPAWN_TIME

            # increase the probability that the insect will be a bee over time
            nb = (
                (GAME_DURATION - self.time_left) / GAME_DURATION * 100 / 2
            )  # increase from 0 to 50 during all  the game (linear)
            if random.randint(0, 100) < nb:
                self.insects.append(Bee(self.window_size))
            else:
                self.insects.append(Balloon(self.window_size))

            # spawn a other balloon after the half of the game
            if self.time_left < GAME_DURATION / 2:
                self.insects.append(Balloon(self.window_size))

    def load_camera(self):
        _, frame = self.cap.read()
        self.frame = cv2.resize(frame, (300, 169))

    def set_hand_position(self):
        self.frame = self.hand_tracking.scan_hands(self.frame)
        (x, y) = self.hand_tracking.get_hand_center()
        self.hand.rect.center = (x, y)

    def draw(self):
        # draw the background
        self.background.draw(self.surface)

        # Convert camera frame to Pygame surface and draw it
        if hasattr(self, "frame"):
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            # Create Pygame surface from camera frame
            frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
            # Position in top right corner with 20px padding
            self.surface.blit(frame_surface, (self.window_size[0] - 300, 0))

        # draw the insects
        for insect in self.insects:
            insect.draw(self.surface)
        # draw the hand
        self.hand.draw(self.surface)
        # draw the score
        ui.draw_text(
            self.surface,
            f"Score : {self.score}",
            (5, 5),
            COLORS["score"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )
        # draw the time left
        timer_text_color = (
            (160, 40, 0) if self.time_left < 5 else COLORS["timer"]
        )  # change the text color if less than 5 s left
        ui.draw_text(
            self.surface,
            f"Time left : {self.time_left}",
            (self.window_size[0] // 2, 5),
            timer_text_color,
            shadow=True,
            shadow_color=(255, 255, 255),
        )

        # Draw game over screen if time is up
        if self.time_left <= 0:
            if not self.score_saved:
                self.update_scores(self.score)
                self.score_saved = True
            # Create blurred background
            blurred = self.create_blur_surface(self.surface.copy())
            self.surface.blit(blurred, (0, 0))

            # Draw Game Over title
            ui.draw_title_text(
                self.surface,
                "GAME OVER",
                color="white",
                x=self.window_size[0] // 2,
                y=250,
            )

            # Draw final score
            ui.draw_text(
                self.surface,
                f"Final Score: {self.score}",
                (self.window_size[0] // 2, 350),
                "white",
                pos_mode="center",
                shadow=True,
                shadow_color=(255, 255, 255),
            )

    def game_time_update(self):
        if not self.paused:  # Only update time if game is not paused
            self.time_left = max(
                round(GAME_DURATION - (time.time() - self.game_start_time), 1), 0
            )

    def update_scores(self, score):
        new_score = {
            "player_name": self.player_name,
            "score": score,
        }

        try:
            response = requests.post(
                "https://ozgeldi.tech/api/isjo",
                json=new_score,
                headers={"Content-Type": "application/json"},
                timeout=5,
            )
            response.raise_for_status()

            print(f"[{datetime.datetime.now()}] {self.player_name} - {self.score}. Sent to API successfully")
        except Exception as e:
            print(f"Failed to send score to API: {e}")

    def create_blur_surface(self, surface):
        # Create a copy of the surface at 1/4 size
        small = pygame.transform.scale(
            surface, (self.window_size[0] // 4, self.window_size[1] // 4)
        )
        # Scale back up - this creates the blur effect
        blurred = pygame.transform.scale(small, self.window_size)
        # Add semi-transparent overlay to darken
        overlay = pygame.Surface(self.window_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # black with 50% transparency
        blurred.blit(overlay, (0, 0))
        return blurred

    def update(self):
        self.load_camera()
        self.set_hand_position()
        self.game_time_update()

        # Draw the game normally first
        self.draw()

        if self.paused:
            # Create blurred background from current display
            blurred = self.create_blur_surface(self.surface.copy())
            # Draw the blurred background
            self.surface.blit(blurred, (0, 0))

            # Draw pause menu
            ui.draw_title_text(
                self.surface, "PAUSED", color="white", x=self.window_size[0] // 2, y=300
            )
            ui.draw_text(
                self.surface,
                f"Current Score: {self.score}",
                (self.window_size[0] // 2, 360),
                "white",
                pos_mode="center",
                shadow=True,
                shadow_color=(255, 255, 255),
            )

            if ui.button(
                self.surface,
                400,
                "Continue",
                click_sound=self.sounds["slap"],
                pos_x=self.window_size[0],
            ):
                self.paused = False
                return None

            if ui.button(
                self.surface,
                400 + BUTTONS_SIZES[1] * 1.25,
                "Main Menu",
                click_sound=self.sounds["slap"],
                pos_x=self.window_size[0],
            ):
                self.menu.reset_input()
                return "menu"

            return None

        if self.time_left > 0:
            self.spawn_insects()
            (x, y) = self.hand_tracking.get_hand_center()
            self.hand.rect.center = (x, y)
            self.hand.left_click = self.hand_tracking.hand_closed
            if self.hand.left_click:
                self.hand.image = self.hand.image_smaller.copy()
            else:
                self.hand.image = self.hand.orig_image.copy()
            self.score = self.hand.kill_insects(self.insects, self.score, self.sounds)
            for insect in self.insects:
                insect.move()
        else:
            # Add Play Again button
            if ui.button(
                self.surface,
                450,
                "Play Again",
                click_sound=self.sounds["slap"],
                pos_x=self.window_size[0],
            ):
                self.reset()
                return None

            if ui.button(
                self.surface,
                550,
                "Main Menu",
                click_sound=self.sounds["slap"],
                pos_x=self.window_size[0],
            ):
                self.menu.reset_input()
                return "menu"
