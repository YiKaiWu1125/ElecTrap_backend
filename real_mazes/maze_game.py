from os import lstat
from textwrap import indent
import cv2
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose
import time
from turtle import window_height
import matplotlib.pyplot as plt # plt 用於顯示圖片
import matplotlib.image as mpimg # mpimg 用於讀取圖片
import numpy as np

def record_fps(img,pTime):
    # 記錄執行時間
    cTime = time.time()
    # 計算fps
    fps = 1 / (cTime - pTime)
    # 重置起始時間
    pTime = cTime
    # 把fps顯示再窗口上；img畫板；取整的fps值；顯示位置的坐標；設置字體；字體比例；顏色；厚度
    cv2.putText(img, "fps:"+str(int(fps)), (1750, 70),
                cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
    return img,pTime


def zero_to_one(x): # 使其在0~1間
    if x > 1.0 :
        x = 1.0
    if x < 0.0 :
        x = 0.0
    return x

def read_picture(picture_name,width,hight):
    transparent = 125
    binarization_arr = [[0 for j in range(hight+10)]for i in range(width+10)]
    img = mpimg.imread(picture_name) 
    img*= transparent #float to change uint8 (原本是255但為了降透視度改用transparent 值越高越不透視)
    img = img.astype(np.uint8) #float to change uint8
    for h in range(len(img)):
        for w in range(len(img[0])):
            if img[h][w][0] == transparent and img[h][w][1] == transparent and img[h][w][2] == transparent :
                binarization_arr[w][h] = 1
    return binarization_arr,img

def is_in_begin(x,y):
    if x > 15 and x < 65 and y > 15 and y < 65:
        return True
    return False
    
def is_in_end(x,y):
    if x > 1835 and x < 1885 and y > 15 and y < 65:
        return True
    return False
def draw_maze(image,unit8_img):
    image = cv2.add(image,unit8_img)
    return image

def maze_judgment_status(img,unit8_img,binarization_arr,x,y,sta,game_begin_time,game_end_time):
    if is_in_end(x,y) == True and sta == 'playing': 
        sta = 'game_over'
        game_end_time = time.time() 
    elif is_in_begin(x,y) == True and sta != 'playing':
        sta = 'playing'
        game_begin_time = time.time() 
    elif sta == 'playing' :
        if binarization_arr[x][y] != 1:
            sta = 'prepare_begin'

    if sta != 'game_over':
        img = draw_maze(img,unit8_img)
    if sta == 'prepare_begin':
        # 畫出起始位置框
        img = cv2.rectangle(img, (15,15), (65,65), (255,255,0), thickness=-1)  # begin
        img = cv2.circle(img, (40,40), 20, (255,0,0), -1)#begin
        pass
    if sta == 'playing':
        # 畫出終止位置框
        img = cv2.rectangle(img, (1835,15), (1885,65), (255,255,0), thickness=-1)  # end
        img = cv2.circle(img, (x,y), 20, (255,0,0), -1)#end circle
        pass
    if sta == 'game_over':
        cv2.putText(img, "score:" + str(int(game_end_time - game_begin_time)) + " s.",
                    (0, 150), cv2.FONT_HERSHEY_PLAIN, 5, (260, 25, 240), 3)  # 檢視成績
        cv2.putText(img, "<Game over>", (0, 250),
                    cv2.FONT_HERSHEY_PLAIN, 5, (260, 25, 240), 3)
        #cv2.rectangle(image, (155, 280), (420, 330),
        #              (0, 25, 240), 5)   # 再玩一次
        #cv2.putText(image, "play again", (160, 320),
        #            cv2.FONT_HERSHEY_PLAIN, 3, (0, 25, 240), 3)  # 再玩一次
        #cv2.rectangle(image, (155, 350), (420, 400),
        #              (0, 25, 240), 5)   # 遊戲結束
        #cv2.putText(image, "end game", (160, 390),
        #            cv2.FONT_HERSHEY_PLAIN, 3, (0, 25, 240), 3)  # 遊戲結束
    #print("sta is :"+str(sta))
    return img,sta,game_begin_time,game_end_time

def begin_maze_gmae(camera_id,picture_name,width,hight):
    binarization_arr , unit8_img = read_picture(picture_name,width,hight)
    cap = cv2.VideoCapture(camera_id)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    #挑整與顯示畫質
    wi = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    hi = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print("video init Image Size: %d x %d" % (wi, hi))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width) #設定解析度
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, hight) #設定解析度
    wi = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    hi = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print("video fix Image Size: %d x %d" % (wi, hi))

    sta = 'prepare_begin'
    now_number = 0
    game_end_time = 0 
    game_begin_time = 0 
    x = y = 0
    pTime = 0 # 計算fps用

    with mp_pose.Pose(min_detection_confidence=0.5,min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                break
                ##is use to check map
                #for h in range (hight+5):
                #    for w in range (width+5):
                #        if binarization_arr[w][h] == 1:
                #            image=cv2.rectangle(image,(w-1,h-1),(w+1,h+1),(255,0,0),8)   
                #cv2.imshow('show', image)
                #if cv2.waitKey(5) & 0xFF == 27:
                #    break         

            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.

            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            img = image
            img=cv2.flip(img, 1) # 畫面翻轉
            #img = cv2.resize(image,(width,hight))  # 調整畫面尺寸
            results = pose.process(img)

            size = img.shape   # 取得攝影機影像尺寸
            w = size[1]        # 取得畫面寬度
            h = size[0]        # 取得畫面高度

            if results.pose_landmarks:
                rx = zero_to_one(results.pose_landmarks.landmark[21].x)
                ry = zero_to_one(results.pose_landmarks.landmark[21].y)
                x = int(rx *w)
                y = int(ry *h)
            else:
                #print("no hand.")
                pass
            # Draw the hand annotations on the image.
            img.flags.writeable = True
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            mp_drawing.draw_landmarks(
                img,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
            img,sta,game_begin_time,game_end_time = maze_judgment_status(img,unit8_img,binarization_arr,x,y,sta,game_begin_time,game_end_time)

            img=cv2.rectangle(img,(x-5,y-5),(x+5,y+5),(0,0,255),5)   # 畫出手的位置
            img,pTime=record_fps(img,pTime) #畫出fps

            cv2.imshow('maze_game', img)
            if cv2.waitKey(5) & 0xFF == 27:
                break
            if sta == 'game_over':
                time.sleep(5)
                break
    cap.release()
    cv2.destroyAllWindows()                 

if __name__ == '__main__':
    camera_id = 0#'test.mp4'
    picture_name = 'easy.png'
    width = 1920
    hight = 1080
    begin_maze_gmae(camera_id,picture_name,width,hight)
    print("game over . ")
