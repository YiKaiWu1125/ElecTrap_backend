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

    def __init__(self, body):
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_drawing = mp.solutions.drawing_utils
        self.body = body

    def get_landmarks(self, w, h, results):
        def limit(x, w, y, h):
            if x < 0 or x > 1 or y < 0 or y > 1:
                return -1, -1
            return int(x * w), int(y * h)
        if self.body == 'hands':
            landmark = results.multi_hand_landmarks[-1].landmark[8]
        elif self.body == 'foot':
            landmark = results.pose_landmarks.landmark[31]
        elif self.body == 'head':
            landmark = results.pose_landmarks.landmark[0]
        elif self.body == 'elbow':
            landmark = results.pose_landmarks.landmark[13]
        # 當為(-1,-1)時，代表偵測部位已超出鏡頭視野
        return limit(landmark.x, w, landmark.y, h)

    def draw_landmarks(self, image, results):
        if self.body == 'hands':
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp.solutions.hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
        elif self.body in ['foot', 'head', 'elbow']:
            self.mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp.solutions.pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
            )

    @property
    def processor(self):
        if self.body == 'hands':
            return Solution.HANDS
        elif self.body == 'head' or self.body == 'foot' or self.body == 'elbow':
            return Solution.POSE

    @property
    def body(self):
        return self._mode

    @body.setter
    def body(self, new_mode):
        if new_mode == 'hands':
            self.landmarks_name = 'multi_hand_landmarks'
        elif new_mode == 'foot' or new_mode == 'head' or new_mode == 'elbow':
            self.landmarks_name = 'pose_landmarks'
        else:
            raise ValueError(f'No such type: "{new_mode}"')
        self._mode = new_mode
