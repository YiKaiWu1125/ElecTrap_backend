from tube_game import TubeGame
from base_camera import BaseCamera


class Camera(BaseCamera):
    game_mapping = {'tube': TubeGame()}
    game_type = 'tube'

    def __init__(self):
        super(Camera, self).__init__()

    @staticmethod
    def frames():
        while True:
            try:
                game = Camera.game_mapping[Camera.game_type]
                results, image = game.capture(flip=True)
                game.calc(results)
                image = game.draw(results, image)
                yield image
            except AttributeError:
                pass

    @staticmethod
    def set_image(image):
        Camera.game_mapping[Camera.game_type].image = image

    @staticmethod
    def get_game():
        return Camera.game_mapping[Camera.game_type]
