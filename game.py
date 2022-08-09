import time

import cv2

from solution import Solution


class Game:
    """Game object handle basic game logic
        + Landmarks of pose calculation
        + Gaming time
        + FPS calculation
        calc() must be implemented in child class.
        Notice: The return value of draw() should be transformed to bytes.
    """

    def __init__(self, body='hands'):
        self.reset(body)

    def reset(self, body):
        self.x = self.y = -1  # detected point
        self.status = 'prepare_begin'
        self.pTime = self.cTIme = 0
        self.begin_time = self.end_time = 0
        self.solution = Solution(body)
        self.outtime = 0

    def capture(self, flip=False):
        if not hasattr(self, 'image'):
            raise AttributeError("No image")
        sol = self.solution.processor
        image = self.image.copy()
        # FIXME: Too high resolution cause low FPS, the client only need 1280x720.
        image = cv2.resize(image, (1920, 1080))
        self.h, self.w = image.shape[:2]
        image = cv2.flip(image, 1) if flip else image
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return sol.process(image), image

    def calc(self, results):
        raise NotImplementedError("calc not implemented")

    def draw(self, results, image):
        def calc_fps():
            if self.pTime == 0:
                self.pTime = time.time()
            else:
                self.cTIme = time.time()
                fps = 1 / (self.cTIme - self.pTime)
                self.pTime = self.cTIme
                return int(fps)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        cv2.putText(image, f'FPS: {calc_fps()}', (10, 70),
                    cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
        if getattr(results, self.solution.landmarks_name):
            self.solution.draw_landmarks(image, results)
        self.outtime -= 1
        return image
        # Child class should return as below:
        # return cv2.imencode('.jpg', image)[1].tobytes()

    def check_something(self, attr):
        if hasattr(self, attr):
            delattr(self, attr)
            return True
        else:
            return False

    def check_gameover(self):
        return self.check_something('gameover')

    def check_outpipe(self):
        return self.check_something('outpipe')
    