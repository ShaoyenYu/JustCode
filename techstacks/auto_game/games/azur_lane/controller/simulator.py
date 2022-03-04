import random
import time
from typing import Dict, Tuple, Union

from techstacks.auto_game.games.azur_lane.config import CONFIG_SCENE
from techstacks.auto_game.games.azur_lane.controller import scene
from util.io import load_yaml
from util.win32 import win32gui
from util.win32.monitor import set_process_dpi_awareness
from util.win32.window import Window, parse_rbg_int2tuple

set_process_dpi_awareness(2, silent=True)

SCENES = load_yaml(CONFIG_SCENE)


class AzurLaneWindow(Window):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scene_prev = self.scene_cur = scene.SceneUnknown(self)
        self.debug = kwargs.get("debug", False)

    def left_click(self, coordinate: Union[Tuple[int, int], Dict[str, list]], sleep=0, add_random=True):
        if isinstance(coordinate, dict):
            lt, rb = coordinate["__Rect"][:2]
            x, y = (random.randint(lt[0], rb[0]), random.randint(lt[1], rb[1])) if random else (lt[0], rb[0])
        elif isinstance(coordinate, tuple):
            x, y = coordinate
        else:
            raise NotImplementedError
        super().left_click((x, y), sleep)

    def compare_with_pixel(self, pixels, threshold=1, debug=False) -> bool:
        correct, wrong = 0, 0
        for x, y, rgb_int in pixels:
            if (pixel := self.pixel_from_window(x, y, as_int=True)) != rgb_int:
                if debug:
                    print(f"WRONG: {x, y}, RGB: {parse_rbg_int2tuple(rgb_int)}(Required) != {parse_rbg_int2tuple(pixel)}(Real)")
                wrong += 1
            else:
                correct += 1

        if correct == 0:
            return False
        if wrong == 0:
            return True
        return (correct / (correct + wrong)) >= threshold

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
