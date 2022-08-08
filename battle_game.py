import cv2

from base_video_game import BaseVideoGame


class BattleGame(BaseVideoGame):
    def __init__(self, body='hands', level='easy'):
        self.reset(body, level)
        self.player1 = 1
        self.player2 = 2

    def reset(self, body, level='easy'):
        super().reset(body)
        self.level_max = 50  # only easy implemented

    def calc(self, results):
        if self.reading:
            return
        if self.now_number == len(self.right_hand) - 1:
            if self.status != "game_over":
                self.reset_time = 100
        super().calc(results)

    def draw(self, results, image):
        if self.reading:
            image = super().video_draw(results, image)
            image = cv2.putText(image, f"It's player {self.player1}'s turn to draw the maze",
                                (0, 60), cv2.FONT_HERSHEY_PLAIN, 5, (60, 25, 240), 3)
        else:
            image = super().draw(results, image)
            if self.status == "game_over":
                self.reset_time -= 1
                if self.reset_time == 0:
                    k = self.player1
                    self.player1 = self.player2
                    self.player2 = k
                    self.reading = True
                    self.reset(self.body, self.level)

            image = cv2.putText(image, "It's player " + str(self.player2) +
                                "'s turn to solve the problem", (200, 60), cv2.FONT_HERSHEY_PLAIN, 5, (60, 25, 240), 3)

        image = cv2.resize(image, (1280, 720))
        return cv2.imencode('.jpg', image)[1].tobytes()
