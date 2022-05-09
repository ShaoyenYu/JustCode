from techstacks.auto_game.util.window import GameWindow
from util.concurrent import KillableThread, PauseEventHandler


def wait(*to_wait):
    def _wait(f):
        def wrapper(*args, **kwargs):
            this = args[0]  # type: BaseTask
            this.event_handler.wait(*to_wait)
            return f(*args, **kwargs)

        return wrapper

    return _wait


def switch_scene(window: GameWindow, scene_from, scene_to):
    if window.scene_cur.at(scene_from):
        has_arrived = window.scene_cur.goto(window, scene_to)
        return has_arrived
    return False


class ConfigManager:
    def __init__(self, **configs):
        self.config = {**configs}

    def set(self, attr, value):
        self.config[attr] = value

    def set_batch(self, configs: dict):
        self.config.update(configs)


class BaseTask(KillableThread):
    def __init__(self, window: GameWindow = None):
        KillableThread.__init__(self)
        self.event_handler = PauseEventHandler("can_run")
        self.config_manager = ConfigManager()
        self.window = window

    def start(self) -> None:
        self.event_handler.resume()
        super().start()

    def stop(self):
        if self.is_alive():
            self.terminate()

    @property
    def scene_cur(self):
        return self.window.scene_cur

    @property
    def scene_prev(self):
        return self.window.scene_prev
