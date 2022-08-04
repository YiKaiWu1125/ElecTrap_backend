import time

import mediapipe as mp
import cv2

from base_camera import BaseCamera
from solution import Solution


class Processor:
    def __init__(self, mode):
        self.x = -1
        self.y = -1
        self.pTime = 0  # 處理一張圖像前的時間
        self.cTime = 0  # 一張圖處理完的時間
        self.sta = 'prepare_begin'
        self.print_string = "Ready"
        self.game_begin_time = 0
        self.game_end_time = 0
        self.run = 0  # 當前電管位置 與 起始電管位置 間的距離
        self.run_val = 0.5  # 電管移動的速度
        self.up_down_range = 100  # 電管上下可移動的範圍
        self.solution = Solution(mode)

    def reset(self):
        self.sta = 'prepare_begin'
        self.game_begin_time = self.game_end_time = 0
        self.x = self.y = -100.0

    def check_status(self):
        if hasattr(self, 'next_sol_mode'):
            print("-----------------------")
            self.solution = Solution(self.next_sol_mode)
            delattr(self, 'next_sol_mode')
            self.reset()

    def capture(self, flip=False):
        if hasattr(self, 'image'):
            sol = self.solution.processor
            image = self.image.copy()
            image = cv2.resize(image,(1920,1080))
            size = image.shape
            self.w = size[1]
            self.h = size[0]
            if flip:
                image = cv2.flip(image, 1)

            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            return sol.process(image), image
        else:
            raise AttributeError("no image")

    def parse(self, results):
        self.x = self.y = -1
        if getattr(results, self.solution.landmarks_name):
            self.x, self.y = self.solution.get_landmarks(
                self.w, self.h, results)
        if self.x != -1 and self.y != -1:
            if self.sta == 'prepare_begin' and self.x >= 50 and self.x <= 100 and self.y >= 150 + self.run and self.y <= 200 + self.run:
                self.sta = 'playing'
                if self.game_begin_time == 0:
                    self.game_begin_time = time.time()
                    self.print_string = "begin"
                self.r_string = "begin"
            if self.sta == 'playing' and self.x >= 550 and self.x <= 600 and self.y >= 150 + self.run and self.y <= 200 + self.run:
                self.sta = 'game_over'
                self.gameover = True
                self.game_end_time = time.time()
                self.print_string = "succesful"
            if self.sta == 'playing' and not(self.x >= 50 and self.x <= 600 and self.y >= 150 + self.run and self.y <= 200 + self.run):
                self.sta = 'prepare_begin'
                self.out_pipe = True
                self.r_string = "Fail <again>"
            if self.sta == 'prepare_begin' or self.sta == 'playing':
                if self.game_begin_time != 0:
                    self.print_string = self.r_string + "<cost:" + \
                        str(int(time.time() - self.game_begin_time)) + ">"
        else : 
            if self.sta == 'playing':
                self.out_pipe = True
                self.sta = 'prepare_begin'
                self.r_string = "Fail <again>"

    def draw(self, results, image):
        def record_fps():
            try:
                # 記錄執行時間
                self.cTime = time.time()
                # 計算fps
                fps = 1 / (self.cTime - self.pTime)
                # 重置起始時間
                self.pTime = self.cTime
                # 把fps顯示再窗口上；img畫板；取整的fps值；顯示位置的坐標；設置字體；字體比例；顏色；厚度
                cv2.putText(image, str(int(fps)), (10, 70),
                            cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
                cv2.putText(image, self.print_string, (100, 70),
                            cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 3)
            except:
                pass

        # Draw the hand annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if getattr(results, self.solution.landmarks_name):
            self.solution.draw_landmarks(image, results)

        if self.x > 0.0 and self.y > 0.0:
          col = 255
          if self.sta == 'playing':
              col = 20
          else :
              col = 175
          cv2.rectangle(image, (self.x - 10, self.y - 10),
                        (self.x + 10, self.y + 10), (0, 0, col), 5)   # 畫出觸碰區

        record_fps()

        if self.sta != "game_over":
            cv2.rectangle(image, (50, 150 + int(self.run)), (600, 200 + int(self.run)),
                          (0, 0, 255), 5)   # 畫出電管
        if self.sta == 'prepare_begin':
            cv2.rectangle(image, (50, 150 + int(self.run)), (100, 200 + int(self.run)),
                          (0, 255, 0), 5)   # 畫出起始位置框
        if self.sta == 'playing':
            self.run += self.run_val
            if self.run > self.up_down_range or self.run < self.up_down_range * -1:
              self.run_val = self.run_val * -1
            cv2.rectangle(image, (550, 150 + int(self.run)), (600, 200 + int(self.run)),
                          (255, 255, 0), 5)   # 畫出終止位置框
        if self.sta == 'game_over':
            cv2.putText(image, "score:" + str(int(self.game_end_time - self.game_begin_time)) + " s.",
                        (0, 150), cv2.FONT_HERSHEY_PLAIN, 5, (260, 25, 240), 3)  # 檢視成績
            cv2.putText(image, "<Game over>", (0, 250),
                        cv2.FONT_HERSHEY_PLAIN, 5, (260, 25, 240), 3)
        return cv2.resize(image,(1280,720))

    def change_sol(self, mode):
        self.next_sol_mode = mode


class Camera(BaseCamera):
    processor = Processor('hands')

    def __init__(self):
        super(Camera, self).__init__()

    @staticmethod
    def frames():
        while True:
            try:
                Camera.processor.check_status()
                results, image = Camera.processor.capture(flip=True)
                Camera.processor.parse(results)
                image = Camera.processor.draw(results, image)
                yield cv2.imencode('.jpg', image)[1].tobytes()
            except AttributeError:
                pass
