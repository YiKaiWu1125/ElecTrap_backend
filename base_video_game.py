import time
import math

import cv2
import numpy as np

from game import Game


class BaseVideoGame(Game):
    def __init__(self, body='hands', level='easy'):
        self.reset(body, level)

    def reset(self, body, level='easy'):
        super().reset(body)
        self.right_hand = []
        self.reading = True
        self.now_number = 0  # 紀錄玩家這關當前的過關進度 當now_number == len(right_hand)-1 為抵達終點
        self.level = level
        self.body = body
        self.half_track_width = 50
        self.level_max = 500
        self.color = (100 ,100 ,100)
        self.binarization_arr = np.zeros(
            self.level_max * 1930 * 1090).reshape((self.level_max, 1930, 1090))

    def calc(self, results):
        self.x = self.y = -1
        self.color = (100 ,100 ,100)
        if not self.reading:
            if getattr(results, self.solution.landmarks_name):
                self.x, self.y = self.solution.get_landmarks(
                    self.w, self.h, results)

            if self.x == -1 and self.y == -1:
                if self.status == "playing":
                    self.now_number = 0
                    self.outpipe = True
                    self.life -= 1
                    self.outtime = 20
                    self.status = "prepare_begin"

            else:
                front = self.now_number - 3
                end = self.now_number + 3
                front = max(0, front)
                end = min(end, len(self.right_hand) - 1)

                if self.now_number == len(self.right_hand) - 1:
                    if self.status != "game_over":
                        self.status = "game_over"
                        # self.gameover = True
                        self.end_time = time.time()

                elif self.now_number == 0:
                    if self.binarization_arr[0][self.x][self.y]:
                        if self.begin_time == 0:
                            self.begin_time = time.time()
                        self.now_number = 1
                        self.status = "playing"

                elif self.status == 'playing':
                    is_out_of_bounds = True
                    for i in range(end, front - 1, -1):
                        if self.binarization_arr[i][self.x][self.y]:
                            self.now_number = i
                            is_out_of_bounds = False
                            break

                    if is_out_of_bounds == True:
                        self.now_number = 0
                        self.outpipe = True
                        self.life -= 1
                        self.outtime = 20
                        self.status = "prepare_begin"

            if self.outtime > 0:
                self.color = (3, 1, 231) 

    def draw(self, results, image):
        def draw_pipe(image):  # image,coor_a, coor_b, index, open_save
            image = self.draw_circle(image)
            for i in range(len(self.right_hand) - 1, 0, -1):
                image = self.draw_and_save_circle_link_poly(image, i, 0)
            image = cv2.circle(image, (self.right_hand[self.now_number][0], self.right_hand[self.now_number]
                           [1]), self.half_track_width, (255, 255, 255), -1,) # 畫出玩家須前往的方向(小白球)
            return image
        image = super().draw(results, image)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)

        if len(self.right_hand) == 0:
            return cv2.imencode('.jpg', image)[1].tobytes()

        if self.life <= 0 :
            if self.status != 'game_over':
                self.gameover = True
                self.status = "game_over"
            image = cv2.putText(image, "<Game over>", (0, 250),
                            cv2.FONT_HERSHEY_PLAIN, 5, (260, 25, 240), 3)

        else:
            if self.status != "game_over":
                image = draw_pipe(image)  # 畫出電管

            if self.status == "prepare_begin":
                image = cv2.circle(
                    image,
                    (self.right_hand[0][0], self.right_hand[0][1]),
                    self.half_track_width,
                    (255, 0, 0),
                    -1,
                )  # 畫出起始位置框

            if self.status == "playing":
                cv2.circle(
                    image,
                    (self.right_hand[len(self.right_hand) - 1][0],
                     self.right_hand[len(self.right_hand) - 1][1]),
                    self.half_track_width,
                    (255, 0, 0),
                    -1,
                )  # 畫出終止位置框

            if self.status == "game_over":
                cv2.putText(
                    image,
                    "score:" + str(int(self.end_time - self.begin_time)) + " s.",
                    (0, 150),
                    cv2.FONT_HERSHEY_PLAIN,
                    5,
                    (260, 25, 240),
                    3,
                )  # 檢視成績
                cv2.putText(image, "<Game over>", (0, 250),
                            cv2.FONT_HERSHEY_PLAIN, 5, (260, 25, 240), 3)

            if self.x != -1 and self.y != -1:
                image = cv2.rectangle(image, (self.x - 5, self.y - 5),
                                      (self.x + 5, self.y + 5), (0, 0, 255), 5)   # 畫出手的位置
        return image


# ------------- video --------------------------------------------------


    def video_draw(self, results, image):
        def draw_dot(image):
            for i in range(len(self.right_hand)):
                cv2.rectangle(image, (self.right_hand[i][0] - 1, self.right_hand[i][1] - 1), (
                    self.right_hand[i][0] + 1, self.right_hand[i][1] + 1), (0, 0, 255), 3,)  # 畫出觸碰區
            return image

        def line_length(ax, ay, bx, by):
            return ((ax - bx) ** 2) + ((ay - by) ** 2)

        def save_crycle_to_3_array(index):
            # print("index is :",index)
            x_begin = max(0, self.right_hand[index][0] - self.half_track_width)
            x_end = min(
                1920, self.right_hand[index][0] + self.half_track_width)
            y_begin = max(0, self.right_hand[index][1] - self.half_track_width)
            y_end = min(
                1080, self.right_hand[index][1] + self.half_track_width)
            for i in range(x_begin, x_end):
                for j in range(y_begin, y_end):
                    if (line_length(i, j, self.right_hand[index][0], self.right_hand[index][1]) < self.half_track_width**2):
                        self.binarization_arr[index][i][j] = 1  # is 0-base

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        if getattr(results, self.solution.landmarks_name):
            self.x, self.y = self.solution.get_landmarks(
                self.w, self.h, results)
            self.solution.draw_landmarks(image, results)
            if self.x != -1 and self.y != -1:
                # print("append right hand.",self.x,self.y)
                self.right_hand.append([self.x, self.y])
        image = self.draw_circle(image)
        image = draw_dot(image)
        if len(self.right_hand) >= 1:
            save_crycle_to_3_array(len(self.right_hand) - 1)
        if len(self.right_hand) > 1:
            image = self.draw_and_save_circle_link_poly(
                image,
                len(self.right_hand) - 1,
                1
            )

        if len(self.right_hand) >= self.level_max:
            self.reading = False
        return image

# -------------------------------------------------------------
# ---------will use model--------------------------------------
# -------------------------------------------------------------
    # get two crycle coordinate and let them link together
    def draw_and_save_circle_link_poly(self, image, index, open_save):
        def is_in_poly(point, poly):
            px, py = point
            is_in = False
            for i, corner in enumerate(poly):
                next_i = i + 1 if i + 1 < len(poly) else 0
                x1, y1 = corner
                x2, y2 = poly[next_i]
                if (x1 == px and y1 == py) or (x2 == px and y2 == py):  # if point is on vertex
                    is_in = True
                    break
                if min(y1, y2) < py <= max(y1, y2):  # find horizontal edges of polygon
                    x = x1 + (py - y1) * (x2 - x1) / (y2 - y1)
                    if x == px:  # if point is on edge
                        is_in = True
                        break
                    elif x > px:  # if point is on left-side of line
                        is_in = not is_in
            return is_in

        coor_a = self.right_hand[index - 1]
        coor_b = self.right_hand[index]
        w = coor_b[0] - coor_a[0]  # x
        h = coor_b[1] - coor_a[1]  # y
        dis_len = float((w**2) + (h**2))
        dis_len = math.sqrt(dis_len)
        if dis_len == 0:
            dis_len = 0.00000000001
        k = float(float(self.half_track_width) / float(dis_len))
        link_dot = []

        # right up
        x = int(coor_a[0] - (k * h))
        y = int(coor_a[1] + (k * w))
        link_dot.append([x, y])

        # right down
        x = int(coor_a[0] + (k * h))
        y = int(coor_a[1] - (k * w))
        link_dot.append([x, y])

        # left down
        x = int(coor_b[0] + (k * h))
        y = int(coor_b[1] - (k * w))
        link_dot.append([x, y])

        # left up
        x = int(coor_b[0] - (k * h))
        y = int(coor_b[1] + (k * w))
        link_dot.append([x, y])

        # full draw
        contours = np.array(link_dot)
        cv2.fillPoly(image, pts=[contours], color=self.color)

        # save poly in binarization_arr(need save ? open_save = 1 : open_save = 0)
        if open_save == 1:
            ma_x = max(link_dot[0][0], link_dot[1][0],
                       link_dot[2][0], link_dot[3][0])
            ma_y = max(link_dot[0][1], link_dot[1][1],
                       link_dot[2][1], link_dot[3][1])
            mi_x = min(link_dot[0][0], link_dot[1][0],
                       link_dot[2][0], link_dot[3][0])
            mi_y = min(link_dot[0][1], link_dot[1][1],
                       link_dot[2][1], link_dot[3][1])
            for i in range(max(mi_x, 0), min(ma_x + 1, 1920), 1):
                for j in range(max(mi_y, 0), min(ma_y + 1, 1080), 1):
                    if self.binarization_arr[index][i][j] == 0:
                        if is_in_poly([i, j], link_dot) == True:
                            self.binarization_arr[index][i][j] = 1

         # draw line
        if open_save == 0 and index - self.now_number < 3 and index - self.now_number >= 0:
            cv2.line(
                image,
                (link_dot[0][0], link_dot[0][1]),
                (link_dot[3][0], link_dot[3][1]),
                (0, 255, 255),
                5,
            )
            cv2.line(
                image,
                (link_dot[1][0], link_dot[1][1]),
                (link_dot[2][0], link_dot[2][1]),
                (0, 255, 255),
                5,
            )

        return image

    def draw_circle(self, image):
        if len(self.right_hand) == 0:
            return image
        for i in range(len(self.right_hand) - 1, -1, -1):
            image = cv2.circle(
                image, (self.right_hand[i][0], self.right_hand[i][1]), self.half_track_width, self.color, -1,)
        return image
        
