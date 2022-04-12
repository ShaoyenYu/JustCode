import random
import time

import numpy as np

from techstacks.auto_game.games.azur_lane.config import CONFIG_SCENE
from techstacks.auto_game.games.azur_lane.controller import scene
from techstacks.auto_game.util.proto import TwoDimArrayLike
from util.io import load_yaml
from util.win32 import win32gui
from util.win32.monitor import set_process_dpi_awareness
from util.win32.window import Window, parse_int_bgr2rgb

set_process_dpi_awareness(2, silent=True)

SCENES = load_yaml(CONFIG_SCENE)


class AzurLaneWindow(Window):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scene_prev = self.scene_cur = scene.SceneUnknown(self)

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

    def compare_with_pixel(self, pixels: TwoDimArrayLike, tolerance=0) -> bool:
        template = pixels[:, 0:2]
        real = np.apply_along_axis(lambda xy: self.pixel_from_window(*xy, as_int=True), axis=1, arr=template)
        return (np.array(parse_int_bgr2rgb(real ^ template)).T <= tolerance).all()

    def compare_with_template(self, rect: list, template, threshold=1.00) -> bool:
        lt, rb = rect
        origin = self.screenshot(lt[0], lt[1], rb[0] - lt[0], rb[1] - lt[1])
        min_value, max_value, min_loc, max_loc = scene.match_single_template(origin, template)
        print(min_value, max_value)
        return min_value >= threshold


class Bluestack:
    def __init__(self, window_name: str):
        self.window_sim = AzurLaneWindow(window_name=window_name)
        self.window_ctl = AzurLaneWindow(window_hwnd=win32gui.FindWindowEx(self.window_sim.hwnd, None, None, None))


if __name__ == '__main__':
    w = AzurLaneWindow(window_name="BS_AzurLane")
    while True:
        w.scene_cur.detect_scene()
        print(w.scene_cur)
        time.sleep(1)
