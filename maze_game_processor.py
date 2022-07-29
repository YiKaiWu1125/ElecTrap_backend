import time

import matplotlib.image as mpimg # mpimg 用於讀取圖片
import numpy as np

import mediapipe as mp
import cv2

from base_camera import BaseCamera
from solution import Solution


class Processor:
    def __init__(self, mode):
        def init_val():
            self.camera_id = 1#'real_mazes/test.mp4'
            self.picture_name = 'real_mazes/1.png'
            self.x = 0
            self.y = 0
            self.sta = 'prepare_begin'
            self.width = 1920
            self.height = 1080
            self.pTime = 0  # 處理一張圖像前的時間
            self.cTime = 0  # 一張圖處理完的時間
            self.game_begin_time = 0
            self.game_end_time = 0
            self.transparent = 125
            open_camera() 
            self.solution = Solution(mode)

        def open_camera():
            self.cap = cv2.VideoCapture(self.camera_id)
            #挑整與顯示畫質
            wi = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            hi = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            print("video init Image Size: %d x %d" % (wi, hi))
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width) #設定解析度
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height) #設定解析度
            wi = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            hi = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            print("video fix Image Size: %d x %d" % (wi, hi))
        
        def read_picture():
            self.binarization_arr = [[0 for j in range(self.height+10)]for i in range(self.width+10)]
            self.maze_img = mpimg.imread(self.picture_name) 
            self.maze_img*= self.transparent #float to change uint8 (原本是255但為了降透視度改用transparent 值越高越不透視)
            self.maze_img = self.maze_img.astype(np.uint8) #float to change uint8
            for h in range(len(self.maze_img)):
                for w in range(len(self.maze_img[0])):
                    if self.maze_img[h][w][0] == self.transparent and self.maze_img[h][w][1] == self.transparent and self.maze_img[h][w][2] == self.transparent :
                        self.binarization_arr[w][h] = 1 

        init_val()
        read_picture()

    def capture(self, flip=False):
        if hasattr(self, 'next_sol_mode'):
            self.solution = Solution(self.next_sol_mode)
            delattr(self, 'next_sol_mode')
        sol = self.solution.processor
        while self.cap.isOpened():
            success, image = self.cap.read()
            
            if not success:
              print("Ignoring empty camera frame.")
              # If loading a video, use 'break' instead of 'continue'.
              continue

            if flip:
                image = cv2.flip(image, 1)
            size = image.shape   # 取得攝影機影像尺寸
            self.w = size[1]        # 取得畫面寬度
            self.h = size[0]        # 取得畫面高度

            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Return mediapipe results
            return sol.process(image), image

    def parse(self, results):
        def is_in_begin(x,y):
            if x > 15 and x < 65 and y > 15 and y < 65:
                return True
            return False

        def is_in_end(x,y):
            if x > 1835 and x < 1885 and y > 15 and y < 65:
                return True
            return False
        if getattr(results, self.solution.landmarks_name):
            self.x, self.y = self.solution.get_landmarks(self.w, self.h, results)
        if self.x != -1 and self.y != -1:
            if is_in_end(self.x,self.y) == True and self.sta == 'playing': 
                self.sta = 'game_over'
                self.game_end_time = time.time() 
            elif is_in_begin(self.x,self.y) == True and self.sta != 'playing':
                self.sta = 'playing'
                self.game_begin_time = time.time() 
            elif self.sta == 'playing' :
                if self.binarization_arr[self.x][self.y] != 1:
                    self.sta = 'prepare_begin'
        else:
            self.sta = 'prepare_begin'

    def draw(self, results, image):
        def record_fps():
            # 記錄執行時間
            self.cTime = time.time()
            # 計算fps
            fps = 1 / (self.cTime - self.pTime)
            # 重置起始時間
            self.pTime = self.cTime
            # 把fps顯示再窗口上；img畫板；取整的fps值；顯示位置的坐標；設置字體；字體比例；顏色；厚度
            cv2.putText(image, "fps:"+str(int(fps)), (1750, 70),cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
        def draw_maze(image,unit8_img):
            image = cv2.add(image,unit8_img)
            return image
        # Draw the hand annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        record_fps() #繪製貞數
        if getattr(results, self.solution.landmarks_name):
            self.solution.draw_landmarks(image, results)
        # Flip the image horizontally for a selfie-view display.
        if self.x != -1 and self.y != -1:
            image=cv2.rectangle(image,(self.x-5,self.y-5),(self.x+5,self.y+5),(0,0,255),5)   # 畫出手的位置
        if self.sta != 'game_over':
            image = draw_maze(image,self.maze_img)
        if self.sta == 'prepare_begin':
            # 畫出起始位置框
            image = cv2.rectangle(image, (15,15), (65,65), (255,255,0), thickness=-1)  # begin
            image = cv2.circle(image, (40,40), 20, (255,0,0), -1)#begin
        if self.sta == 'playing':
            # 畫出終止位置框
            image = cv2.rectangle(image, (1835,15), (1885,65), (255,255,0), thickness=-1)  # end
            image = cv2.circle(image, (self.x,self.y), 20, (255,0,0), -1)#end circle
            pass
        if self.sta == 'game_over':
            cv2.putText(image, "score:" + str(int(self.game_end_time - self.game_begin_time)) + " s.",
                        (0, 150), cv2.FONT_HERSHEY_PLAIN, 5, (260, 25, 240), 3)  # 檢視成績
            cv2.putText(image, "<Game over>", (0, 250),
                        cv2.FONT_HERSHEY_PLAIN, 5, (260, 25, 240), 3)
        return image

    def change_sol(self, mode):
        self.next_sol_mode = mode


class Camera(BaseCamera):
    processor = Processor('hands')

    def __init__(self):
        super(Camera, self).__init__()
    
    @staticmethod
    def frames():
        while True:
            results, image = Camera.processor.capture(flip=True)
            Camera.processor.parse(results)
            image = Camera.processor.draw(results, image)
            yield cv2.imencode('.jpg', image)[1].tobytes()
