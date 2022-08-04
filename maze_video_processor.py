import time

import numpy as np
import cv2
import math

from base_camera import BaseCamera
from solution import Solution

class Processor:
    def __init__(self, mode):
        self.level = 'Mazes_from_video/test1.mp4'
        self.x = -1
        self.y = -1
        self.sta = 'prepare_begin'
        self.now_number = 0
        self.pTime = 0  # 處理一張圖像前的時間
        self.cTime = 0  # 一張圖處理完的時間
        self.game_begin_time = 0
        self.game_end_time = 0
        self.right_hand = []
        self.binarization_arr = []
        self.half_track_width = 50
        self.img = ''
        self.solution = Solution(mode)
    
    def change_sol(self, mode):
        self.next_sol_mode = mode
    
    def change_level(self, level):
        self.next_sol_level = level

    def check_status(self):
        if hasattr(self, 'next_sol_mode'):
            self.solution = Solution(self.next_sol_mode)
            delattr(self, 'next_sol_mode')

        if hasattr(self, 'next_sol_level'):
            self.level = self.next_sol_level
            delattr(self, 'next_sol_level')

    def model_or_level_have_change(self):
        if hasattr(self, 'next_sol_mode') or hasattr(self, 'next_sol_level'):
            return True
        return False

    def reset(self):
        print("----------------------go reset---------------------")
        self.sta = 'prepare_begin'
        self.game_begin_time = self.game_end_time = 0
        self.now_number = 0
        self.right_hand = []
        self.binarization_arr = []
        self.cap = cv2.VideoCapture(str(self.level))

#camera---------------------------------------------------------------------------
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
            print("no image")
            raise AttributeError("no image")

    def parse(self,results):
        self.x = self.y = -1
        if getattr(results, self.solution.landmarks_name):
            self.x, self.y = self.solution.get_landmarks(self.w, self.h, results)
        if self.x == -1 and self.y == -1 :
            if self.sta != "game_over":
                if self.sta != "prepare_begin":
                    self.now_number = 0
                    self.out_pipe = True
                    self.sta = "prepare_begin"
        else :
            front = self.now_number - 5
            end = self.now_number + 5
            if front < 0:
                front = 0
            if end >= len(self.binarization_arr):
                end = len(self.binarization_arr) - 1
            if len(self.binarization_arr) == 0:
                pass
            elif self.now_number == len(self.binarization_arr) - 1:
                if self.sta != "game_over":
                    self.sta = "game_over"
                    self.gameover = True
                    self.game_end_time = time.time()
            elif self.now_number == 0:
                if self.binarization_arr[0][self.x][self.y] == True:
                    if self.game_begin_time == 0:
                        self.game_begin_time = time.time()
                    self.now_number = 1
                    self.sta = "playing"
                    
            else:
                k = True
                for i in range(end, front - 1, -1):
                    if self.binarization_arr[i][self.x][self.y] == True:
                        self.now_number = i
                        k = False
                        break
                if k == True:
                    self.now_number = 0
                    self.out_pipe = True
                    self.sta = "prepare_begin"

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
                cv2.putText(image, "fps:"+str(int(fps)), (1750, 70),cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
            except:
                pass

        def draw_pipe(image):#image,coor_a, coor_b, index, open_save
            for i in range(len(self.right_hand)-1,0,-1):
                image = self.draw_and_save_circle_link_poly(image,i,0)
            image = self.draw_circle(image)
            return image

        # Draw the hand annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        record_fps() #繪製貞數
        if getattr(results, self.solution.landmarks_name):
            self.solution.draw_landmarks(image, results)
        # Flip the image horizontally for a selfie-view display.
        if len(self.right_hand) == 0:
            return image
        if self.sta != "game_over":
            image = draw_pipe(image)  # 畫出電管
        if self.sta == "prepare_begin":
            image = cv2.circle(
                image,
                (self.right_hand[0][0], self.right_hand[0][1]),
                self.half_track_width,
                (255, 0, 0),
                -1,
            )  # 畫出起始位置框
        if self.sta == "playing":
            cv2.circle(
                image,
                (self.right_hand[len(self.right_hand) - 1][0], self.right_hand[len(self.right_hand) - 1][1]),
                self.half_track_width,
                (255, 0, 0),
                -1,
            )  # 畫出終止位置框
        if self.sta == "game_over":
            cv2.putText(
                image,
                "score:" + str(int(self.game_end_time - self.game_begin_time)) + " s.",
                (0, 150),
                cv2.FONT_HERSHEY_PLAIN,
                5,
                (260, 25, 240),
                3,
            )  # 檢視成績
            cv2.putText(
                image, "<Game over>", (0, 250), cv2.FONT_HERSHEY_PLAIN, 5, (260, 25, 240), 3
            )
        if self.x != -1 and self.y != -1:
            image=cv2.rectangle(image,(self.x-5,self.y-5),(self.x+5,self.y+5),(0,0,255),5)   # 畫出手的位置
        return image
#video--------------------------------------------------------------------
    def video_capture(self, flip=False):
        sol = self.solution.processor
        while self.cap.isOpened():
            success, image = self.cap.read()
            if not success:
                break
            if flip:
                image = cv2.flip(image, 1)
            size = image.shape   # 取得攝影機影像尺寸
            self.w = size[1]        # 取得畫面寬度
            self.h = size[0]        # 取得畫面高度

            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
            return sol.process(image), image
        self.cap.release()
        return "video end.",self.img

    def video_draw(self, results, image):
        def draw_dot(image):
            for i in range(len(self.right_hand)):
                cv2.rectangle(image,(self.right_hand[i][0] - 1, self.right_hand[i][1] - 1),(self.right_hand[i][0] + 1, self.right_hand[i][1] + 1),(0, 0, 255),3,)  # 畫出觸碰區
            return image

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        if getattr(results, self.solution.landmarks_name):
            self.x, self.y = self.solution.get_landmarks(self.w, self.h, results)
            self.solution.draw_landmarks(image, results)
            if self.x != -1 and self.y != -1:
                self.right_hand.append([self.x,self.y])
        image = self.draw_circle(image)
        image = draw_dot(image)
        self.img = image
        return image

    def video_end(self,image):
        def line_length(ax, ay, bx, by):
            return ((ax - bx) ** 2) + ((ay - by) ** 2)

        def save_crycle_to_3_array(index):
            self.binarization_arr.append([[False for ii in range(1090)] for jj in range(1930)])  # [x][y]
            x_begin = self.right_hand[index][0] - self.half_track_width
            if x_begin < 0:
                x_begin = 0
            x_end = self.right_hand[index][0] + self.half_track_width
            if x_end > 1920:
                x_end = 1920
            y_begin = self.right_hand[index][1] - self.half_track_width
            if y_begin < 0:
                y_begin = 0
            y_end = self.right_hand[index][1] + self.half_track_width
            if y_end > 1080:
                y_end = 1080
            for i in range(x_begin, x_end):
                for j in range(y_begin, y_end):
                    if (line_length(i, j, self.right_hand[index][0], self.right_hand[index][1])< self.half_track_width**2):
                        self.binarization_arr[index][i][j] = True  # is 0-base
        
        for i in range(len(self.right_hand)):
            save_crycle_to_3_array(i)
        for i in range(1, len(self.right_hand)):
            image = self.draw_and_save_circle_link_poly(
                image,
                i,
                1
            )
        return image
#-------------------------------------------------------------
#---------will use model--------------------------------------
#-------------------------------------------------------------
    def draw_and_save_circle_link_poly(self, image, index, open_save):  # get two crycle coordinate and let them link together
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
     
        # draw line
        cv2.line(
            image,
            (link_dot[0][0], link_dot[0][1]),
            (link_dot[3][0], link_dot[3][1]),
            (0, 0, 0),
            5,
        )
        cv2.line(
            image,
            (link_dot[1][0], link_dot[1][1]),
            (link_dot[2][0], link_dot[2][1]),
            (0, 0, 0),
            5,
        )

        # full draw
        contours = np.array(link_dot)
        cv2.fillPoly(image, pts=[contours], color=(0, 225, 225))

        # save poly in binarization_arr(need save ? open_save = 1 : open_save = 0)
        if open_save == 1:
            ma_x = max(link_dot[0][0], link_dot[1][0], link_dot[2][0], link_dot[3][0])
            ma_y = max(link_dot[0][1], link_dot[1][1], link_dot[2][1], link_dot[3][1])
            mi_x = min(link_dot[0][0], link_dot[1][0], link_dot[2][0], link_dot[3][0])
            mi_y = min(link_dot[0][1], link_dot[1][1], link_dot[2][1], link_dot[3][1])
            for i in range(mi_x, ma_x + 1, 1):
                for j in range(mi_y, ma_y + 1, 1):
                    if self.binarization_arr[index][i][j] == False:
                        if is_in_poly([i, j], link_dot) == True:
                            self.binarization_arr[index][i][j] = True
        return image

    def draw_circle(self,image):
        if len(self.right_hand) == 0:
            return image
        for i in range(len(self.right_hand)-1,-1,-1):
            if self.now_number == i:
                col = [255, 255, 255]
            else:
                col = [0, 225, 225]
            image = cv2.circle(image,(self.right_hand[i][0], self.right_hand[i][1]),self.half_track_width,(col[0], col[1], col[2]),-1,)
        col = [255, 255, 255]
        image = cv2.circle(image,(self.right_hand[self.now_number][0], self.right_hand[self.now_number][1]),self.half_track_width,(col[0], col[1], col[2]),-1,)
        return image

class Camera(BaseCamera):
    processor = Processor('hands')
    def __init__(self):
        super(Camera, self).__init__()
    
    @staticmethod
    def frames():
        while True:
            Camera.processor.check_status()
            Camera.processor.reset()
            while True:
                if Camera.processor.model_or_level_have_change() == True:
                    break
                results, image = Camera.processor.video_capture(flip=True)
                if results == "video end.":
                    image = Camera.processor.video_end(image)
                    break
                image = Camera.processor.video_draw(results, image)
                yield cv2.imencode('.jpg', cv2.resize(image,(1280,720)))[1].tobytes()
            while True:
                if Camera.processor.model_or_level_have_change() == True:
                    break
                results, image = Camera.processor.capture(flip=True)
                Camera.processor.parse(results)
                image = Camera.processor.draw(results, image)
                yield cv2.imencode('.jpg', cv2.resize(image,(1280,720)))[1].tobytes()

