import mediapipe as mp


class Solution:
    HANDS = mp.solutions.hands.Hands(
        max_num_hands=1,
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    POSE = mp.solutions.pose.Pose(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    def __init__(self, mode):
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_drawing = mp.solutions.drawing_utils
        self.mode = mode

    def get_landmarks(self, w, h, results):
        if self.mode == 'hands':
            landmark = results.multi_hand_landmarks[-1].landmark[8]
        elif self.mode == 'foot':
            landmark = results.pose_landmarks.landmark[31]
        elif self.mode == 'head':
            landmark = results.pose_landmarks.landmark[0]
        return Solution.is_in_range(landmark.x, w, landmark.y, h) # 當為(-1,-1)時，代表偵測部位已超出鏡頭視野

    def draw_landmarks(self, image, results):
        if self.mode == 'hands':
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp.solutions.hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
        elif self.mode == 'foot' or self.mode == 'head':
            self.mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp.solutions.pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
            )
    
    def is_in_range(x,w,y,h): 
        if x < 0 or x > 1 or y < 0 or y > 1 :
            return -1,-1
        return int(x * w),int(y * h) 

    @property
    def processor(self):
        if self.mode == 'hands':
            return Solution.HANDS
        elif self.mode == 'head' or self.mode == 'foot':
            return Solution.POSE

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, new_mode):
        if new_mode == 'hands':
            self.landmarks_name = 'multi_hand_landmarks'
        elif new_mode == 'foot' or new_mode == 'head':
            self.landmarks_name = 'pose_landmarks'
        else:
            raise ValueError(f'No such type: "{new_mode}"')
        self._mode = new_mode
