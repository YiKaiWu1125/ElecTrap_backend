from asyncio.windows_events import NULL
from os import lstat
from textwrap import indent
import cv2
from cv2 import sqrt
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose
import math
import time
import numpy as np
width = 1920
hight = 1080

half_track_width = 50

def zero_to_one(x):
    if x > 1.0 :
        x = 1.0
    if x < 0.0 :
        x = 0.0
    return x
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

def line_length(ax,ay,bx,by):
    return ((ax-bx)**2)+((ay-by)**2)

def draw_circle(img,coor_arr,nownumber):
    for i in range(len(coor_arr)):
        if nownumber == i:
            col = [255,255,255]
        elif nownumber == -1:
            col = [0,225,225]
        else :
            col = [0,255,0]
        img = cv2.circle(img, (coor_arr[i][0],coor_arr[i][1]), half_track_width, (col[0],col[1],col[2]), -1)
    if nownumber != -1:
        col = [255,255,255]
        img = cv2.circle(img, (coor_arr[nownumber][0],coor_arr[nownumber][1]), half_track_width, (col[0],col[1],col[2]), -1)
    return img

def draw_dot(img,coor_arr):
    for i in range(len(coor_arr)):
        cv2.rectangle(img,(coor_arr[i][0]-1,coor_arr[i][1]-1),(coor_arr[i][0]+1,coor_arr[i][1]+1),(0,0,255),3)   # 畫出觸碰區
    return img

def draw_and_save_circle_link_poly(img,coor_a,coor_b,index,binarization_arr,open_save): # get two crycle coordinate and let them link together
    w = coor_b[0] - coor_a[0]   # x
    h = coor_b[1] - coor_a[1]   # y
    dis_len = float((w**2) + (h**2))
    dis_len = math.sqrt(dis_len)
    if dis_len == 0:
        dis_len = 0.00000000001
    #print("half_track_width:"+str(half_track_width))
    #print("dis_len:"+str(dis_len))
    k = float(float(half_track_width) / float(dis_len))
    link_dot = []

    #right up
    x = int(coor_a[0] - (k*h))
    y = int(coor_a[1] + (k*w))
    #binarization_arr[1][x][y]=5
    link_dot.append([x,y])

    #right down
    x = int(coor_a[0] + (k*h))
    y = int(coor_a[1] - (k*w))
    #binarization_arr[1][x][y]=5
    link_dot.append([x,y])

    #left down
    x = int(coor_b[0] + (k*h))
    y = int(coor_b[1] - (k*w))
    #binarization_arr[1][x][y]=5
    link_dot.append([x,y])
    
    #left up
    x = int(coor_b[0] - (k*h))
    y = int(coor_b[1] + (k*w))
    #binarization_arr[1][x][y]=5
    link_dot.append([x,y])

    #draw line
    cv2.line(img, (link_dot[0][0], link_dot[0][1]), (link_dot[3][0], link_dot[3][1]), (0,0,0), 5)
    cv2.line(img, (link_dot[1][0], link_dot[1][1]), (link_dot[2][0], link_dot[2][1]), (0,0,0), 5)
    
    #full draw
    contours = np.array(link_dot)
    cv2.fillPoly(img, pts = [contours], color =(0,225,225))
    

    #save poly (need open save == 1)
    if open_save == 1:
        ma_x = max(link_dot[0][0],link_dot[1][0],link_dot[2][0],link_dot[3][0])
        ma_y = max(link_dot[0][1],link_dot[1][1],link_dot[2][1],link_dot[3][1])
        mi_x = min(link_dot[0][0],link_dot[1][0],link_dot[2][0],link_dot[3][0])
        mi_y = min(link_dot[0][1],link_dot[1][1],link_dot[2][1],link_dot[3][1])
        for i in range(mi_x,ma_x+1,1):
            for j in range(mi_y,ma_y+1,1):
                if(binarization_arr[index][i][j]==0):
                    if(is_in_poly([i,j],link_dot)==True):
                        binarization_arr[index][i][j]=1
        #print(ma_x,ma_y,mi_x,mi_y)
        return img,binarization_arr
    else :
        return img
      
def save_crycle_to_3_array(binarization_arr,coor_arr,index):
    binarization_arr.append([[0 for j in range(hight+10)]for i in range(width+10)]) #[x][y]
    x_begin = coor_arr[index][0]-half_track_width
    if x_begin < 0 :
        x_begin = 0
    x_end =  coor_arr[index][0]+half_track_width
    if x_end > width :
        x_end = width
    y_begin = coor_arr[index][1]-half_track_width
    if y_begin < 0 :
        y_begin = 0
    y_end =  coor_arr[index][1]+half_track_width
    if y_end > hight :
        y_end = hight
    #print(index,x_begin,x_end,y_begin,y_end)
    for i in range(x_begin,x_end):
        for j in range(y_begin,y_end):
            #if index == 0:
            #    print(i,j,coor_arr[index][0],coor_arr[index][1],)
            #    print(line_length(i,j,coor_arr[index][0],coor_arr[index][1]),half_track_width)
            if line_length(i,j,coor_arr[index][0],coor_arr[index][1]) < half_track_width**2:
                binarization_arr[index][i][j] = 1 # need care it is 0 base
                #if index == 0:
                #    print("+")
    return binarization_arr

def get_track(video_name):
    binarization_arr = [] # [nwo_number][hight][width]
    right_hand = []
    cap = cv2.VideoCapture(str(video_name))
    #挑整與顯示畫質
    wi = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    hi = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print("video init Image Size: %d x %d" % (wi, hi))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width) #設定解析度
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, hight) #設定解析度
    wi = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    hi = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print("video fix Image Size: %d x %d" % (wi, hi))

    with mp_pose.Pose(min_detection_confidence=0.5,min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            success, img = cap.read()
            #print(cap.rows,cap.rols)
            if not success:
                print("video end.")
                for i in range(len(right_hand)):
                    binarization_arr = save_crycle_to_3_array(binarization_arr,right_hand,i)
                for i in range(1,len(right_hand)):
                    image,binarization_arr=draw_and_save_circle_link_poly(image,right_hand[i-1],right_hand[i],i,binarization_arr,1)
                    cv2.imshow('MediaPipe Pose', image)
                    if cv2.waitKey(5) & 0xFF == 27:
                        break
                #time.sleep(5)
                cap.release()
                cv2.destroyAllWindows()
                return  right_hand , binarization_arr
            else:
                image = img
                #image = cv2.resize(img,(width,hight))
                #image = cv2.resize(img,(width,hight)) # set stand size is 640 * 480.
            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            
            
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = pose.process(image)
            size = image.shape   # 取得攝影機影像尺寸
            w = size[1]        # 取得畫面寬度
            h = size[0]        # 取得畫面高度
            #print("w:"+str(w)+" h:"+str(h))
            if results.pose_landmarks:
                #right hand
                rx = zero_to_one(results.pose_landmarks.landmark[20].x)
                ry = zero_to_one(results.pose_landmarks.landmark[20].y)
                right_hand.append([int(rx *w),int(ry *h)])
                ##left hand
                #left_hand.append([int(results.pose_landmarks.landmark[19].x *w),int(results.pose_landmarks.landmark[19].y *h)])
                ##right foot
                #right_foot.append([int(results.pose_landmarks.landmark[32].x *w),int(results.pose_landmarks.landmark[32].y *h)])
                ##left foot
                #left_foot.append([int(results.pose_landmarks.landmark[31].x *w),int(results.pose_landmarks.landmark[31].y *h)])

            # Draw the pose annotation on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()) 
            image = draw_circle(img,right_hand,-1)
            image = draw_dot(image,right_hand)
            # Flip the image horizontally for a selfie-view display.
            cv2.namedWindow('MediaPipe Pose', 0)
            cv2.resizeWindow('MediaPipe Pose', width,hight)
            cv2.imshow('MediaPipe Pose', image)
            if cv2.waitKey(5) & 0xFF == 27:
                break
    
#right_hand,binarization_arr=get_track("test1.mp4")
#print("successful end.")
#print("right_hand")
#print(right_hand)
#print("binarization_arr")
#for i in range(hight):
#    for j in range(width):
#        if (binarization_arr[1][j][i] == 1):
#            print("x:" + str(j) + " y:" + str(i))
#print("game over.")
#print(len(binarization_arr))
#print(len(right_hand))
#print(len(binarization_arr[0][1]))

#path = 'output.txt'
#f = open(path, 'w')
#for h in range (hight+5):
#    for w in range (width+5):
#        for i in range(len(binarization_arr)):
#            k = 0
#            if binarization_arr[i][w][h] == 1:
#                k = 1
#                break
#        print(str(k),end='', file=f)
#    print('', file=f)
#f.close()