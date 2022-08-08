import cv2
import numpy as np

from base_video_game import BaseVideoGame


class VideoGame(BaseVideoGame):
    def __init__(self, body='hands', level='easy'):
        self.reset(body, level)

    def reset(self, body, level='easy'):
        super().reset(body, level)
        self.cap = cv2.VideoCapture(f'static/video/{self.level}.mp4')

    def capture(self, flip=False):
        if self.reading:
            sol = self.solution.processor
            ret, image = self.cap.read()
            if not ret or len(self.right_hand) >= self.level_max:
                self.reading = False
                self.cap.release()
                return super().capture(flip)
            self.h, self.w = image.shape[:2]
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            return sol.process(image), image
        return super().capture(flip)

    def calc(self, results):
        if self.now_number == len(self.right_hand) - 1 and not self.reading and self.status != 'game_over':
            self.gameover = True
        super().calc(results)

    def draw(self, results, image):
        image = super().video_draw(
            results, image) if self.reading else super().draw(results, image)
        image = cv2.resize(image, (1280, 720))
        return cv2.imencode('.jpg', image)[1].tobytes()
