import json
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
        self.surface = surface
        self.menu = menu
        self.background = Background()
        self.score_saved = False
        self.player_name = ""

        # Load camera
        self.cap = cv2.VideoCapture(1)

        self.sounds = {}
        self.sounds["slap"] = pygame.mixer.Sound(f"assets/sounds/slap.wav")
        self.sounds["slap"].set_volume(SOUNDS_VOLUME)
        self.sounds["screaming"] = pygame.mixer.Sound(f"assets/sounds/screaming.wav")
        self.sounds["screaming"].set_volume(SOUNDS_VOLUME)

    def reset(self):  # reset all the needed variables
        self.hand_tracking = HandTracking()
        self.hand = Hand()
        self.insects = []
        self.insects_spawn_timer = 0
        self.score = 0
        self.game_start_time = time.time()

    def spawn_insects(self):
        t = time.time()
        if t > self.insects_spawn_timer:
            self.insects_spawn_timer = t + BALLOONS_SPAWN_TIME

            # increase the probability that the insect will be a bee over time
            nb = (
                (GAME_DURATION - self.time_left) / GAME_DURATION * 100 / 2
            )  # increase from 0 to 50 during all  the game (linear)
            if random.randint(0, 100) < nb:
                self.insects.append(Bee())
            else:
                self.insects.append(Balloon())

            # spawn a other balloon after the half of the game
            if self.time_left < GAME_DURATION / 2:
                self.insects.append(Balloon())

    def load_camera(self):
        _, self.frame = self.cap.read()

    def set_hand_position(self):
        self.frame = self.hand_tracking.scan_hands(self.frame)
        (x, y) = self.hand_tracking.get_hand_center()
        self.hand.rect.center = (x, y)

    def draw(self):
        # draw the background
        self.background.draw(self.surface)
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
            font=FONTS["medium"],
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
            (SCREEN_WIDTH // 2, 5),
            timer_text_color,
            font=FONTS["medium"],
            shadow=True,
            shadow_color=(255, 255, 255),
        )

    def game_time_update(self):
        self.time_left = max(
            round(GAME_DURATION - (time.time() - self.game_start_time), 1), 0
        )

    def update_scores(self, score, file_path="scores.json"):
        try:
            with open(file_path, "r") as file:
                scores = json.load(file)
        except FileNotFoundError:
            scores = []

        new_score = {
            "player_name": self.player_name if self.player_name else "Anonymous",
            "score": score,
        }
        scores.append(new_score)

        with open(file_path, "w") as file:
            json.dump(scores, file, indent=4)

        try:
            response = requests.post(
                "https://ozgeldi.tech/api/isjo",
                json=new_score,
                headers={"Content-Type": "application/json"},
                timeout=5,
            )
            response.raise_for_status()

            print("Sent to API successfully")
        except Exception as e:
            print(f"Failed to send score to API: {e}")

    def update(self):
        self.load_camera()
        self.set_hand_position()
        self.game_time_update()

        self.draw()

        if self.time_left > 0:
            self.spawn_insects()
            (x, y) = self.hand_tracking.get_hand_center()
            self.hand.rect.center = (x, y)
            self.hand.left_click = self.hand_tracking.hand_closed
            # print("Hand closed", self.hand.left_click)
            if self.hand.left_click:
                self.hand.image = self.hand.image_smaller.copy()
            else:
                self.hand.image = self.hand.orig_image.copy()
            self.score = self.hand.kill_insects(self.insects, self.score, self.sounds)
            for insect in self.insects:
                insect.move()

        else:  # when the game is over
            if not self.score_saved:
                self.update_scores(self.score)
                self.score_saved = True

            if ui.button(
                self.surface, 540, "Continue", click_sound=self.sounds["slap"]
            ):
                self.menu.reset_input()
                return "menu"

        # cv2.imshow("Frame", self.frame)
        cv2.waitKey(1)
