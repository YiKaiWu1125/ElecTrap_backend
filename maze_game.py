import time

import cv2

from game import Game


class MazeGame(Game):
    def __init__(self, body='hands', level='easy'):
        self.reset(body, level)

    def reset(self, body, level='easy'):
        def remove_background(image):
            tmp = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            _, alpha = cv2.threshold(tmp, 0, 255, cv2.THRESH_BINARY)
            b, g, r = cv2.split(image)
            rgba = [b, g, r, alpha]
            dst = cv2.merge(rgba, 4)
            return dst

        super().reset(body)
        self.level = level
        self.maze_img = cv2.imread(
            'static/images/' + self.level + '.png', cv2.IMREAD_UNCHANGED)
        self.show_img = self.maze_img.copy()
        #self.show_img = remove_background(self.show_img)
        self.outpipe_img = cv2.imread(
            'static/images/outpipe_' + self.level + '.png', cv2.IMREAD_UNCHANGED)
        self.playing_img = cv2.imread(
            'static/images/playing_' + self.level + '.png', cv2.IMREAD_UNCHANGED)
        
    def calc(self, results):
        def is_in_begin(x, y):
            if 15 < x < 65 and 15 < y < 65:
                return True
            return False

        def is_in_end(x, y):
            if 1835 < x < 1885 and 15 < y < 65:
                return True
            return False

        def is_touched(x, y):
            return not bool(self.maze_img[y][x][0])

        self.x = self.y = -1
        if getattr(results, self.solution.landmarks_name):
            self.x, self.y = self.solution.get_landmarks(
                self.w, self.h, results)
        if self.x != -1 and self.y != -1:
            if is_in_end(self.x, self.y) == True and self.status == 'playing':
                self.status = 'game_over'
                self.gameover = True
                self.end_time = time.time()
            elif is_in_begin(self.x, self.y) == True and self.status == 'prepare_begin':
                self.status = 'playing'
                if self.begin_time == 0:
                    self.begin_time = time.time()
            elif self.status == 'playing':
                if is_touched(self.x, self.y):
                    self.outpipe = True
                    self.outtime = 10
                    self.status = 'prepare_begin'
        elif self.status == 'playing':
            self.status = 'prepare_begin'
            self.outtime = 10

    def draw(self, results, image):
        image = super().draw(results, image)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)

        if self.x != -1 and self.y != -1:
            image = cv2.rectangle(image, (self.x - 5, self.y - 5),
                                  (self.x + 5, self.y + 5), (0, 0, 255), 5)   # 畫出手的位置
        if self.status != 'game_over':
            if self.outtime > 0:
                image = cv2.addWeighted(image, 0.3, self.outpipe_img, 0.7, 0)
            elif self.status == 'playing':
                image = cv2.addWeighted(image, 0.6, self.playing_img, 0.4, 0)
            else:
                image = cv2.addWeighted(image, 0.6, self.show_img, 0.4, 0)
        if self.status == 'prepare_begin':
            # 畫出起始位置框
            image = cv2.rectangle(image, (15, 15), (65, 65),
                                  (255, 255, 0), thickness=-1)  # begin
            image = cv2.circle(image, (40, 40), 20, (255, 0, 0), -1)  # begin
        if self.status == 'playing':
            # 畫出終止位置框
            image = cv2.rectangle(
                image, (1835, 15), (1885, 65), (255, 255, 0), thickness=-1)  # end
            image = cv2.circle(image, (self.x, self.y), 20,
                               (255, 0, 0), -1)  # end circle
        if self.status == 'game_over':
            cv2.putText(image, "score:" + str(int(self.end_time - self.begin_time)) + " s.",
                        (0, 150), cv2.FONT_HERSHEY_PLAIN, 5, (260, 25, 240), 3)  # 檢視成績
            cv2.putText(image, "<Game over>", (0, 250),
                        cv2.FONT_HERSHEY_PLAIN, 5, (260, 25, 240), 3)
        image = cv2.resize(image, (1280, 720))
        return cv2.imencode('.jpg', image)[1].tobytes()
