import image
from settings import *


class Background:
    def __init__(self, window_size):
        self.w, self.h = window_size
        self.image = image.load(
            "assets/background.jpg",
            size=(self.w, self.h),
            convert="default",
        )

    def draw(self, surface):
        image.draw(
            surface,
            self.image,
            (self.w // 2, self.h // 2),
            pos_mode="center",
        )
