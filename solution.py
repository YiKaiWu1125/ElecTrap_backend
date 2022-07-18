import mediapipe as mp


class Solution:
    def __init__(self, type):
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_drawing = mp.solutions.drawing_utils
        self.type = type
        if self.type == 'hands':
            self.mp_sol = mp.solutions.hands
            self.sol_func = self.mp_sol.Hands
            self.sol_args = {
                'max_num_hands': 1,
                'model_complexity': 0,
                'min_detection_confidence': 0.5,
                'min_tracking_confidence': 0.5
            }
            self.landmarks_name = 'multi_hand_landmarks'
        elif self.type == 'foot' or self.type == 'head':
            self.mp_sol = mp.solutions.pose
            self.sol_func = self.mp_sol.Pose
            self.sol_args = {
                'model_complexity': 0,
                'min_detection_confidence': 0.5,
                'min_tracking_confidence': 0.5
            }
            self.landmarks_name = 'pose_landmarks'
        else:
            raise ValueError(f'No such type: "{type}"')

    def get_landmarks(self, w, h, results):
        if self.type == 'hands':
            landmark = results.multi_hand_landmarks[-1].landmark[8]
        elif self.type == 'foot':
            landmark = results.pose_landmarks.landmark[31]
        elif self.type == 'head':
            landmark = results.pose_landmarks.landmark[0]
        return landmark.x * w, landmark.y * h

    def draw_landmarks(self, image, results):
        if self.type == 'hands':
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    self.mp_sol.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
        elif self.type == 'foot' or self.type == 'head':
            self.mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                self.mp_sol.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
            )
