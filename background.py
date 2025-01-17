import image
from settings import *


class Background:
    _image_cache = {}  # Class-level cache for loaded images

    def __init__(self, window_size):
        self.w, self.h = window_size
        cache_key = f"{self.w}x{self.h}"

        # Try to get from cache first
        if cache_key in Background._image_cache:
            self.image = Background._image_cache[cache_key]
        else:
            # Load and cache if not present
            self.image = image.load(
                "assets/background.jpg",
                size=(self.w, self.h),
                convert="default",
            )
            Background._image_cache[cache_key] = self.image

            # Clear cache if it gets too large (keep last 3 sizes)
            if len(Background._image_cache) > 3:
                oldest_key = list(Background._image_cache.keys())[0]
                del Background._image_cache[oldest_key]

    def draw(self, surface):
        image.draw(
            surface,
            self.image,
            (self.w // 2, self.h // 2),
            pos_mode="center",
        )
