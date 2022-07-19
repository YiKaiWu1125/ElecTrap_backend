import time

import mediapipe as mp
import cv2

from base_camera import BaseCamera
from solution import Solution


class Processor:
    def __init__(self, type):
        self.mp_pose = mp.solutions.pose
        self.solution = Solution(type)

        self.camera_id = 0  # 選擇電腦相機id
        self.re = 1
        self.x = -100.0
        self.y = -100.0
        self.pTime = 0  # 處理一張圖像前的時間
        self.cTime = 0  # 一張圖處理完的時間
        self.sta = 0
        self.st = "Ready"
        self.betime = 0
        self.endtime = 0
        self.run = 0
        self.run_val = 1
        self.up_down_range = 100
        self.cap = cv2.VideoCapture(self.camera_id)

    def capture(self, flip=False):
        if hasattr(self, 'next_sol_type'):
            self.solution = Solution(self.next_sol_type)
            delattr(self, 'next_sol_type')
        with self.solution.sol_func(**self.solution.sol_args) as sol:
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
        if getattr(results, self.solution.landmarks_name):
            self.x, self.y = self.solution.get_landmarks(
                self.w, self.h, results)
            self.re = 1
        elif self.re == 1:
            pass
            # print(f'Not {self.solution.type}')
        if self.sta == 0 and self.x >= 50 and self.x <= 100 and self.y >= 150 + self.run and self.y <= 200 + self.run:
            self.sta = 1
            if self.betime == 0:
                self.betime = time.time()
                self.st = "begin"
            self.ss = "begin"
        if self.sta == 1 and self.x >= 550 and self.x <= 600 and self.y >= 150 + self.run and self.y <= 200 + self.run:
            self.sta = 2
            self.endtime = time.time()
            self.st = "succesful"
        if self.sta == 1 and not(self.x >= 50 and self.x <= 600 and self.y >= 150 + self.run and self.y <= 200 + self.run):
            self.sta = 0
            print("-----------------------error x:" +
                  str(self.x) + " y:" + str(self.y) + "--------------")
            self.ss = "Fail <again>"
        if self.sta == 0 or self.sta == 1:
            if self.betime != 0:
                self.st = self.ss + "<cost:" + \
                    str(int(time.time() - self.betime)) + ">"
            # if(re == 1 ):
            #    st =ss +"not hand."
        if self.sta == 2:  # 遊戲結束
            if self.x >= 155 and self.x <= 420 and self.y >= 280 and self.y <= 330:  # 再玩一次
                self.re = 1
                self.x = -100.0
                self.y = -100.0
                self.pTime = 0  # 處理一張圖像前的時間
                self.cTime = 0  # 一張圖處理完的時間
                self.sta = 0
                self.st = "Restart"
                self.betime = 0
                self.endtime = 0
                self.run = 0
                self.run_val = 1
            if self.x >= 155 and self.x <= 420 and self.y >= 350 and self.y <= 400:  # 遊戲結束
                print("close game.")
                self.cap.release()
                # cv2.destroyAllWindows()

    def draw(self, results, image):
        def record_fps():
            try:
                # 記錄執行時間
                self.cTime = time.time()
                # 計算fps
                fps = 1 / (self.cTime - self.pTime)
                # 重置起始時間
                self.pTime = self.cTime
                # 把fps顯示在窗口上；img畫板；取整的fps值；顯示位置的坐標；設置字體；字體比例；顏色；厚度
                cv2.putText(image, str(int(fps)), (10, 70),
                            cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
                cv2.putText(image, self.st, (100, 70),
                            cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 3)
            except:
                pass

        # Draw the hand annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if getattr(results, self.solution.landmarks_name):
            self.solution.draw_landmarks(image, results)
        # Flip the image horizontally for a selfie-view display.
        if self.x > 0.0 and self.y > 0.0:
          rx = int(self.x)
          ry = int(self.y)
          #print(" x :" + str(rx) + " and y: " + str(ry))
          # cv2.circle(img, (rx, ry), 15, (255, 0, 255), cv2.FILLED)
          col = 255
          if self.sta == 1:
              col = 100
          if self.sta == -1:
              col = 175
          cv2.rectangle(image, (rx - 10, ry - 10),
                        (rx + 10, ry + 10), (0, 0, col), 5)   # 畫出觸碰區

        record_fps()

        if self.sta != 2:
            cv2.rectangle(image, (50, 150 + self.run), (600, 200 + self.run),
                          (0, 0, 255), 5)   # 畫出觸碰區
        if self.sta == 0:
            cv2.rectangle(image, (50, 150 + self.run), (100, 200 + self.run),
                          (0, 255, 0), 5)   # 畫出觸碰區
        if self.sta == 1:
            self.run += self.run_val
            if self.run > self.up_down_range or self.run < self.up_down_range * -1:
              self.run_val = self.run_val * -1
            cv2.rectangle(image, (550, 150 + self.run), (600, 200 + self.run),
                          (255, 255, 0), 5)   # 畫出觸碰區
        if self.sta == 2:
            cv2.putText(image, "score:" + str(int(self.endtime - self.betime)) + " s.",
                        (0, 150), cv2.FONT_HERSHEY_PLAIN, 5, (260, 25, 240), 3)
            cv2.putText(image, "<Game over>", (0, 250),
                        cv2.FONT_HERSHEY_PLAIN, 5, (260, 25, 240), 3)
            cv2.rectangle(image, (155, 280), (420, 330),
                          (0, 25, 240), 5)   # 在玩一次
            cv2.putText(image, "play again", (160, 320),
                        cv2.FONT_HERSHEY_PLAIN, 3, (0, 25, 240), 3)  # 在玩一次
            cv2.rectangle(image, (155, 350), (420, 400),
                          (0, 25, 240), 5)   # 遊戲結束
            cv2.putText(image, "end game", (160, 390),
                        cv2.FONT_HERSHEY_PLAIN, 3, (0, 25, 240), 3)  # 遊戲結束
        return image
        # cv2.imshow('MediaPipe Hands', image)
        # if cv2.waitKey(5) & 0xFF == 27:
            # break

    def change_sol(self, type):
        self.next_sol_type = type


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
