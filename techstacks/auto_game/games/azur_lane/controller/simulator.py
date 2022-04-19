import random
import time

import numpy as np

from techstacks.auto_game.games.azur_lane.interface.entry import Gateway
from techstacks.auto_game.games.azur_lane.interface.scene import SceneUnknown
from util.win32 import win32gui
from util.win32.monitor import set_process_dpi_awareness
from util.win32.window import Window

set_process_dpi_awareness(2, silent=True)


class GameWindow(Window):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scene_prev = self.scene_cur = SceneUnknown

    @staticmethod
    def gen_random_xy(lt, rb):
        x, y = (random.randint(lt[0], rb[0]), random.randint(lt[1], rb[1]))
        return np.asarray((x, y), dtype=np.uint)

    def left_click(self, position, sleep=0):
        if not isinstance(position, np.ndarray):
            position = np.asarray(position, dtype=np.uint)

        if position.ndim == 2:
            position = self.gen_random_xy(*position)
        elif position.ndim == 1:
            pass
        else:
            raise NotImplementedError

        super().left_click(position, sleep=sleep)


class Bluestack:
    def __init__(self, window_name: str):
        self.window_sim = GameWindow(window_name=window_name)
        self.window_ctl = GameWindow(window_hwnd=win32gui.FindWindowEx(self.window_sim.hwnd, None, None, None))
        self.gateway = Gateway(self.window_ctl)


if __name__ == '__main__':
    bs = Bluestack(window_name="BS_AzurLane")
    while True:
        bs.gateway.detect_scene()
        print(bs.gateway.scene_cur)
        time.sleep(1)
