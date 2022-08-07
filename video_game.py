import time

import cv2
import numpy as np
import math

from base_video_game import BaseVideoGame


class VideoGame(BaseVideoGame):
    def __init__(self, body='hands', level='easy'):
        self.reset(body, level)

    def reset(self, body, level='easy'):
        def reset_cap():
            level_name = 'static/video/' + self.level + '.mp4'
            self.cap = cv2.VideoCapture(level_name)
        super().reset(body)
        self.right_hand = []
        self.binarization_arr = []
        self.half_track_width = 50
        self.read = 1
        self.now_number = 0
        self.level = level
        self.level_max = 100
        self.binarization_arr = np.zeros(self.level_max*1930*1090).reshape((self.level_max,1930,1090))
        reset_cap()


    def calc(self, results):
        if self.now_number == len(self.right_hand) - 1:
            if self.status != "game_over":
                self.gameover = True
        super().calc(results)

    def draw(self, results, image):
        image = super().draw(results, image)
        image = cv2.resize(image, (1280, 720))
        return cv2.imencode('.jpg', image)[1].tobytes()

# ------------- video --------------------------------------------------
    def video_capture(self, flip=False):
        sol = self.solution.processor
        while self.cap.isOpened():
            success, image = self.cap.read()
            if not success:
                self.cap.release()
                self.read = 0
                break
            if len(self.right_hand) >= self.level_max:
                self.cap.release()
                self.read = 0
                break
            if flip:
                image = cv2.flip(image, 1)
            size = image.shape   # 取得攝影機影像尺寸
            self.w = size[1]        # 取得畫面寬度
            self.h = size[0]        # 取得畫面高度

            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
            return sol.process(image), image
        return "",""

    def video_draw(self, results, image):
        image = super().video_draw(results, image)

        image = cv2.resize(image, (1280, 720))
        return cv2.imencode('.jpg', image)[1].tobytes()
