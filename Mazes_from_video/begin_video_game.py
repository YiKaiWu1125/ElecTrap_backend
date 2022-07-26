from os import lstat
from textwrap import indent
import cv2
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose
import math
import time
import numpy
import playvideo_and_getcoordinate as p_g


def draw(image,right_hand,binarization_arr,nownumber,half_track_width):
    
    for i in range(1,len(right_hand)):
        image=p_g.draw_and_save_circle_link_poly(image,right_hand[i-1],right_hand[i],i,binarization_arr,0,half_track_width)
    for i in range (len(right_hand)):
        image = p_g.draw_circle(image,right_hand,nownumber,half_track_width)
    return image

def judgment_status(image,right_hand,binarization_arr,x,y,now_number,sta,game_begin_time,game_end_time,half_track_width):
    front = (now_number-5)
    end = (now_number+5)
    if front < 0 :
        front = 0
    if end >= len(binarization_arr):
        end = len(binarization_arr)-1
    if now_number == len(binarization_arr)-1 : 
        sta = 'game_over'
        game_end_time = time.time() 
    if now_number == 0 :
        if binarization_arr[0][x][y] == 1:
            now_number = 1
            sta = 'playing'
            game_begin_time = time.time() 
    else :
        k = True
        for i in range (end,front-1,-1):
            if binarization_arr[i][x][y] == 1 :
                now_number = i
                k = False
                break
        if k == True:
            now_number = 0
            sta = 'prepare_begin'

    if sta != 'game_over':
        image = draw(image,right_hand,binarization_arr,now_number,half_track_width)   # 畫出電管
    if sta == 'prepare_begin':
        image = cv2.circle(image, (right_hand[0][0],right_hand[0][1]), half_track_width, (255,0,0), -1)# 畫出起始位置框
    if sta == 'playing':
        cv2.circle(image, (right_hand[len(right_hand)-1][0],right_hand[len(right_hand)-1][1]), half_track_width, (255,0,0), -1)   # 畫出終止位置框
    if sta == 'game_over':
        cv2.putText(image, "score:" + str(int(game_end_time - game_begin_time)) + " s.",
                    (0, 150), cv2.FONT_HERSHEY_PLAIN, 5, (260, 25, 240), 3)  # 檢視成績
        cv2.putText(image, "<Game over>", (0, 250),
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
    return image,now_number,sta,game_begin_time,game_end_time

def begin_video_game(width,hight,half_track_width,sample_video,video_id):

    right_hand,binarization_arr=p_g.get_track(sample_video,width,hight,half_track_width)
    print("successful get coordinate.")

    # For webcam input:
    cap = cv2.VideoCapture(video_id)
    #挑整與顯示畫質
    wi = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    hi = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print("webcam init Image Size: %d x %d" % (wi, hi))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width) #設定解析度
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, hight) #設定解析度
    wi = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    hi = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print("webcam fix Image Size: %d x %d" % (wi, hi))

    sta = 'prepare_begin'
    now_number = 0
    game_end_time = 0 
    game_begin_time = 0 
    x = y = 0


    with mp_pose.Pose(min_detection_confidence=0.5,min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                ##can use to debug map
                #for i in range(len(binarization_arr)):
                #    rmg = img
                #    for h in range (hight+5):
                #        for w in range (width+5):
                #            if binarization_arr[i][w][h] == 1 and i==0:
                #                rmg=cv2.rectangle(rmg,(w-1,h-1),(w+1,h+1),(255,150,200),8)   # 畫出手的位置
                #    cv2.imshow('show', rmg)
                #    if cv2.waitKey(5) & 0xFF == 27:
                #        break                          
                #time.sleep(5)

                print("Ignoring empty camera frame.")
                # If loading a video, use 'break' instead of 'continue'.
                time.sleep(5)
                break

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
                rx = p_g.zero_to_one(results.pose_landmarks.landmark[20].x)
                ry = p_g.zero_to_one(results.pose_landmarks.landmark[20].y)
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
            img,now_number,sta,game_begin_time,game_end_time = judgment_status(img,right_hand,binarization_arr,x,y,now_number,sta,game_begin_time,game_end_time,half_track_width)

            img=cv2.rectangle(img,(x-10,y-10),(x+10,y+10),(0,0,255),8)   # 畫出手的位置

            cv2.imshow('MediaPipe Pose', img)
            if cv2.waitKey(5) & 0xFF == 27:
                break
            if sta == 'game_over':
                time.sleep(5)
                break
    cap.release()
    cv2.destroyAllWindows()



if __name__ == '__main__':

    sample_video = "test1.mp4"
    video_id = 0#"test1.mp4" # if need use sample_video "test1.mp4" ,need to delete row:121 -> img=cv2.flip(img, 1) # 畫面翻轉
    width = 1920
    hight = 1080
    half_track_width = 50 # 電管'半徑'寬度
    
    begin_video_game(width,hight,half_track_width,sample_video,video_id)