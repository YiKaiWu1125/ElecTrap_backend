from turtle import begin_fill
import cv2
import mediapipe as mp
import time
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

re = 1
x = -100.0
y = -100.0 
pTime = 0 #處理一張圖像前的時間
cTime = 0 #一張圖處理完的時間
sta = 0
st = "Ready"
betime = 0
endtime = 0

## For static images:
#IMAGE_FILES = []
#with mp_hands.Hands(
#    static_image_mode=True,
#    max_num_hands=2,
#    min_detection_confidence=0.5) as hands:
#  for idx, file in enumerate(IMAGE_FILES):
#    # Read an image, flip it around y-axis for correct handedness output (see
#    # above).
#    image = cv2.flip(cv2.imread(file), 1)
#    # Convert the BGR image to RGB before processing.
#    results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
#
#    # Print handedness and draw hand landmarks on the image.
#    print('Handedness:', results.multi_handedness)
#    if not results.multi_hand_landmarks:
#      continue
#    image_height, image_width, _ = image.shape
#    annotated_image = image.copy()
#    for hand_landmarks in results.multi_hand_landmarks:
#      print('hand_landmarks:', hand_landmarks)
#      print(
#          f'Index finger tip coordinates: (',
#          f'{hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * image_width}, '
#          f'{hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * image_height})'
#      )
#      mp_drawing.draw_landmarks(
#          annotated_image,
#          hand_landmarks,
#          mp_hands.HAND_CONNECTIONS,
#          mp_drawing_styles.get_default_hand_landmarks_style(),
#          mp_drawing_styles.get_default_hand_connections_style())
#    cv2.imwrite(
#        '/tmp/annotated_image' + str(idx) + '.png', cv2.flip(annotated_image, 1))
#    # Draw hand world landmarks.
#    if not results.multi_hand_world_landmarks:
#      continue
#    for hand_world_landmarks in results.multi_hand_world_landmarks:
#      mp_drawing.plot_landmarks(
#        hand_world_landmarks, mp_hands.HAND_CONNECTIONS, azimuth=5)

# For webcam input:
cap = cv2.VideoCapture(0)
with mp_hands.Hands(
    max_num_hands=1,
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
  while cap.isOpened():
    success, image = cap.read()
    if not success:
      print("Ignoring empty camera frame.")
      # If loading a video, use 'break' instead of 'continue'.
      continue

    img = cv2.resize(image,(650,450))  # 調整畫面尺寸
    size = img.shape   # 取得攝影機影像尺寸
    w = size[1]        # 取得畫面寬度
    h = size[0]        # 取得畫面高度

    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    
    if results.multi_hand_landmarks:
      for hand_landmarks in results.multi_hand_landmarks:
        x = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_DIP].x *w  # 取得食指末端 x 座標
        y = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_DIP].y *h  # 取得食指末端 y 座標
        print(x,y)
        re = 1
    else:
      if(re == 1):
        print("not hand.")
        re = 0
        x = -100.0
        y = -100.0
    if(sta == 0 and x>=50 and x <= 100 and y >= 150 and y<= 200):
        sta = 1
        if(betime == 0):
            betime = time.time()
            st="begin"
        ss ="begin"
    if(sta == 1 and x>=550 and x <= 600 and y >= 150 and y<= 200):
        sta = 2
        endtime = time.time()
        st = "succesful"
    if(sta == 1 and not(x>=50 and x <= 600 and y >= 150 and y<= 200)):
        sta = 0
        print("-----------------------error x:"+str(x)+" y:"+str(y)+"--------------")
        ss = "Fail <again>"
    if(sta == 0 or sta == 1):
        if(betime != 0):
            st =ss +"<cost:"+ str(int(time.time()-betime))+">"
        #if(re == 1 ):
        #    st =ss +"not hand."
    # Draw the hand annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.multi_hand_landmarks:
      for hand_landmarks in results.multi_hand_landmarks:
        mp_drawing.draw_landmarks(
            image,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style())
    # Flip the image horizontally for a selfie-view display.
    if(x > 0.0 and y > 0.0):
      rx = int (x)
      ry = int (y)
      print(" x :"+str(rx)+" and y: "+str(ry))
      #cv2.circle(img, (rx, ry), 15, (255, 0, 255), cv2.FILLED)
      col = 255
      if(sta == 1):
          col = 100
      if(sta == -1):
          col = 175
      cv2.rectangle(image,(rx-10,ry-10),(rx+10,ry+10),(0,0,col),5)   # 畫出觸碰區
    try:
      # 記錄執行時間      
      cTime = time.time()      
      # 計算fps
      fps = 1/(cTime-pTime)
      # 重置起始時間
      pTime = cTime
      # 把fps顯示在窗口上；img畫板；取整的fps值；顯示位置的坐標；設置字體；字體比例；顏色；厚度
      cv2.putText(image, str(int(fps)), (10,70), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,0), 3)
      cv2.putText(image, st,(100,70), cv2.FONT_HERSHEY_PLAIN, 2, (255,0,0), 3)
      
    except:
      pass
    
    if(sta != 2):
        cv2.rectangle(image,(50,150),(600,200),(0,0,255),5)   # 畫出觸碰區
    if(sta == 0 ):
        cv2.rectangle(image,(50,150),(100,200),(0,255,0),5)   # 畫出觸碰區
    if(sta == 1 ):
        cv2.rectangle(image,(550,150),(600,200),(255,255,0),5)   # 畫出觸碰區
    if(sta == 2):
        cv2.putText(image, "score:"+str(int(endtime-betime))+" s.",(0,250), cv2.FONT_HERSHEY_PLAIN, 5, (260,25,240), 3)
        cv2.putText(image, "<Game over>",(0,350), cv2.FONT_HERSHEY_PLAIN, 5, (260,25,240), 3)
    cv2.imshow('MediaPipe Hands',image)# cv2.flip(image, 1))
    if cv2.waitKey(5) & 0xFF == 27:
      break
cap.release()