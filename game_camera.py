from base_camera import BaseCamera
from tube_game import TubeGame
from maze_game import MazeGame
from video_game import VideoGame
from battle_game import BattleGame


class Camera(BaseCamera):
    game_mapping = {'tube': TubeGame(), 'maze': MazeGame(), 'video': VideoGame(), 'battle': BattleGame()}
    game_type = 'maze'
    
    def __init__(self):
        super(Camera, self).__init__()

    @staticmethod
    def frames():
        while True:
            try:
                game = Camera.game_mapping[Camera.game_type]
                results, image = game.capture(flip=True)
                if (Camera.game_type == 'video' or Camera.game_type == 'battle') and game.read == 1:
                    if Camera.game_type == 'video':
                        re_results, re_image = game.video_capture(flip=True)
                        if re_results != "":
                            image = re_image
                            results = re_results   
                    if game.read == 1:
                        image = game.video_draw(results, image)
                if (Camera.game_type == 'tube' or Camera.game_type == 'maze') or ((Camera.game_type == 'video' or Camera.game_type == 'battle') and game.read == 0):
                    game.calc(results)
                    image = game.draw(results, image)
                yield image
            except AttributeError as n:
                print("錯誤原因:",n)

    @staticmethod
    def set_image(image):
        Camera.game_mapping[Camera.game_type].image = image

    @staticmethod
    def get_game():
        return Camera.game_mapping[Camera.game_type]

    @staticmethod
    def change_game(game_type, game_body):
        if game_type not in Camera.game_mapping.keys():
            raise ValueError('Invalid game type')
        Camera.game_type = game_type
        Camera.game_mapping[Camera.game_type].reset(game_body)
