import time

import matplotlib.image as mpimg # mpimg 用於讀取圖片
import numpy as np

import mediapipe as mp
import cv2

from base_camera import BaseCamera
from solution import Solution


class Processor:
    def __init__(self, mode):
        self.level = 'real_mazes/easy.png'
        self.x = -1
        self.y = -1
        self.sta = 'prepare_begin'
        self.pTime = 0  # 處理一張圖像前的時間
        self.cTime = 0  # 一張圖處理完的時間
        self.game_begin_time = 0
        self.game_end_time = 0
        self.transparent = 125
        self.life_value = 5
        self.solution = Solution(mode)
        self.reset_level()
         
    def reset(self):
        self.sta = 'prepare_begin'
        self.game_begin_time = self.game_end_time = 0
    
    def check_status(self):
        if hasattr(self, 'next_sol_mode'):
            self.solution = Solution(self.next_sol_mode)
            delattr(self, 'next_sol_mode')
            self.reset()

    def capture(self, flip=False):
        if hasattr(self, 'image'):
            sol = self.solution.processor
            image = self.image.copy()
            image=cv2.resize(image,(1920,1080))
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
        def is_in_begin(x,y):
            if x > 15 and x < 65 and y > 15 and y < 65:
                return True
            return False

        def is_in_end(x,y):
            if x > 1835 and x < 1885 and y > 15 and y < 65:
                return True
            return False
        self.x = self.y = -1
        if getattr(results, self.solution.landmarks_name):
            self.x, self.y = self.solution.get_landmarks(self.w, self.h, results)
        if self.x != -1 and self.y != -1:
            if is_in_end(self.x,self.y) == True and self.sta == 'playing': 
                self.sta = 'game_over'
                self.gameover = True
                self.game_end_time = time.time() 
            elif is_in_begin(self.x,self.y) == True and self.sta == 'prepare_begin':
                self.sta = 'playing'
                if self.game_begin_time == 0:
                    self.game_begin_time = time.time() 
            elif self.sta == 'playing' :
                if self.binarization_arr[self.x][self.y] != True:
                    self.out_pipe = True
                    self.sta = 'prepare_begin'
        else:
            if self.sta != 'game_over':
                self.sta = 'prepare_begin'

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
        if self.sta == 'game_over':
            cv2.putText(image, "score:" + str(int(self.game_end_time - self.game_begin_time)) + " s.",
                        (0, 150), cv2.FONT_HERSHEY_PLAIN, 5, (260, 25, 240), 3)  # 檢視成績
            cv2.putText(image, "<Game over>", (0, 250),
                        cv2.FONT_HERSHEY_PLAIN, 5, (260, 25, 240), 3)
        return cv2.resize(image,(1280,720))

    def change_sol(self, mode):
        self.next_sol_mode = mode
    
    def change_level(self, level):
        self.level = level
        self.reset_level()
    
    def reset_level(self):
        self.binarization_arr = [[False for j in range(1090)]for i in range(1930)]
        self.maze_img = mpimg.imread(self.level) 
        self.maze_img*= self.transparent #float to change uint8 (原本是255但為了降透視度改用transparent 值越高越不透視)
        self.maze_img = self.maze_img.astype(np.uint8) #float to change uint8
        for h in range(len(self.maze_img)):
            for w in range(len(self.maze_img[0])):
                if self.maze_img[h][w][0] == self.transparent and self.maze_img[h][w][1] == self.transparent and self.maze_img[h][w][2] == self.transparent :
                    self.binarization_arr[w][h] = True




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
