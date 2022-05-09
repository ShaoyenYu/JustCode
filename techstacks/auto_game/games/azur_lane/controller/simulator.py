from techstacks.auto_game.games.azur_lane.entry import Gateway
from techstacks.auto_game.util.window import GameWindow
from util.win32 import win32gui
from util.win32.monitor import set_process_dpi_awareness

set_process_dpi_awareness(2, silent=True)


class Bluestack:
    def __init__(self, window_name: str):
        self.window_sim = GameWindow(window_name=window_name)
        self.window_ctl = GameWindow(window_hwnd=win32gui.FindWindowEx(self.window_sim.hwnd, None, None, None))
        self.gateway = Gateway(self.window_ctl)
