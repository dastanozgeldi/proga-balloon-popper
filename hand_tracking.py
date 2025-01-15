import cv2
import mediapipe as mp

from settings import *

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands


class HandTracking:
    def __init__(self, window_size):
        self.window_size = window_size
        self.hand_tracking = mp_hands.Hands(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            max_num_hands=1,  # Only track one hand to improve performance
            model_complexity=0,  # Use a lighter model (0 is fastest, 1 is balanced, 2 is most accurate)
        )
        self.hand_x = 0
        self.hand_y = 0
        self.results = None
        self.hand_closed = False

    def scan_hands(self, image):
        # Reduce image resolution for processing
        image = cv2.resize(image, (160, 90))  # Lower resolution for processing

        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        self.results = self.hand_tracking.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        self.hand_closed = False

        if self.results.multi_hand_landmarks:
            hand_landmarks = self.results.multi_hand_landmarks[
                0
            ]  # Only process first hand
            x, y = hand_landmarks.landmark[9].x, hand_landmarks.landmark[9].y

            self.hand_x = int(x * self.window_size[0])
            self.hand_y = int(y * self.window_size[1])

            x1, y1 = hand_landmarks.landmark[12].x, hand_landmarks.landmark[12].y

            if y1 > y:
                self.hand_closed = True

            # Only draw landmarks if FPS is above threshold
            if DRAW_FPS:
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style(),
                )
        return image

    def get_hand_center(self):
        return (self.hand_x, self.hand_y)

    def display_hand(self):
        cv2.imshow("image", self.image)
        cv2.waitKey(1)
