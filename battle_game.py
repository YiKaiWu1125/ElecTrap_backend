import time

import cv2
import numpy as np
import math

from base_video_game import BaseVideoGame

class BattleGame(BaseVideoGame):
    def __init__(self, body='hands', level='easy'):
        self.reset(body, level)
        self.player1 = 1
        self.player2 = 2

    def reset(self, body, level='easy'):
        def set_level_max(level):
            if level == 'easy' :
                return 50

        super().reset(body)
        self.right_hand = []
        self.half_track_width = 50
        self.read = 1
        self.now_number = 0
        self.level = level 
        self.body = body
        self.level_max = set_level_max(level)
        self.binarization_arr = np.zeros(self.level_max*1930*1090).reshape((self.level_max,1930,1090))

    def calc(self, results):
        if self.now_number == len(self.right_hand) - 1:
            if self.status != "game_over":
                self.reset_time = 100
        super().calc(results)

    def draw(self, results, image):
        image = super().draw(results, image)
        if self.status == "game_over":
            self.reset_time -= 1
            if self.reset_time == 0:
                k =self.player1
                self.player1 = self.player2
                self.player2 = k
                self.read = 1
                self.reset(self.body,self.level)

        image=cv2.putText(image, "It's player "+str(self.player2)+"'s turn to solve the problem", (200, 60),cv2.FONT_HERSHEY_PLAIN, 5, (60, 25, 240), 3)
        
        image = cv2.resize(image, (1280, 720))
        return cv2.imencode('.jpg', image)[1].tobytes()

# ------------- video --------------------------------------------------
    def video_draw(self, results, image):
        image = super().video_draw(results, image)

        image=cv2.putText(image, "It's player "+str(self.player1)+"'s turn to ask questions", (0, 60),cv2.FONT_HERSHEY_PLAIN, 5, (60, 25, 240), 3)
        image = cv2.resize(image, (1280, 720))
        return cv2.imencode('.jpg', image)[1].tobytes()

