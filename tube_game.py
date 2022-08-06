import time

import cv2

from game import Game


class TubeGame(Game):
    def __init__(self, body='hands'):
        self.reset(body)

    def reset(self, body):
        super().reset(body)
        self.run = 0
        self.run_val = 0.5  # speed of the tube moving
        self.up_down_range = 100  # range of the tube moving

    def calc(self, results):
        self.x = self.y = -1
        if getattr(results, self.solution.landmarks_name):
            self.x, self.y = self.solution.get_landmarks(
                self.w, self.h, results)
        if self.x != -1 and self.y != -1:
            if self.status == 'prepare_begin' and 50 <= self.x <= 100 and 150 + self.run <= self.y <= 200 + self.run:
                self.status = 'playing'
                if self.begin_time == 0:
                    self.begin_time = time.time()
                    self.print_string = 'begin'
                self.r_string = 'begin'
            if self.status == 'playing':
                if 550 <= self.x <= 600 and 150 + self.run <= self.y <= 200 + self.run:
                    self.status = 'game_over'
                    self.gameover = True
                    self.end_time = time.time()
                    self.print_string = 'successful'
                if not(50 <= self.x <= 600 and 150 + self.run <= self.y <= 200 + self.run):
                    self.outpipe = True
                    self.status = 'prepare_begin'
                    self.r_string = 'Fail <again>'
            if self.status in ['prepare_begin', 'playing'] and self.begin_time != 0:
                self.print_string = self.r_string + "<cost:" + \
                    str(int(time.time() - self.begin_time)) + ">"
        elif self.status == 'playing':
            self.outpipe = True
            self.status = 'prepare_begin'
            self.r_string = 'Fail <again>'

    def draw(self, results, image):
        image = super().draw(results, image)
        if self.x > 0.0 and self.y > 0.0:
          col = 255
          if self.status == 'playing':
              col = 20
          else:
              col = 175
          cv2.rectangle(image, (self.x - 10, self.y - 10),
                        (self.x + 10, self.y + 10), (0, 0, col), 5)   # 畫出觸碰區

        if self.status != "game_over":
            cv2.rectangle(image, (50, 150 + int(self.run)), (600, 200 + int(self.run)),
                          (0, 0, 255), 5)   # 畫出電管
        if self.status == 'prepare_begin':
            cv2.rectangle(image, (50, 150 + int(self.run)), (100, 200 + int(self.run)),
                          (0, 255, 0), 5)   # 畫出起始位置框
        if self.status == 'playing':
            self.run += self.run_val
            if self.run > self.up_down_range or self.run < self.up_down_range * -1:
              self.run_val = self.run_val * -1
            cv2.rectangle(image, (550, 150 + int(self.run)), (600, 200 + int(self.run)),
                          (255, 255, 0), 5)   # 畫出終止位置框
        if self.status == 'game_over':
            cv2.putText(image, "score:" + str(int(self.end_time - self.begin_time)) + " s.",
                        (0, 150), cv2.FONT_HERSHEY_PLAIN, 5, (260, 25, 240), 3)  # 檢視成績
            cv2.putText(image, "<Game over>", (0, 250),
                        cv2.FONT_HERSHEY_PLAIN, 5, (260, 25, 240), 3)
        image = cv2.resize(image, (1280, 720))
        return cv2.imencode('.jpg', image)[1].tobytes()
