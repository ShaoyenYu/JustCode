from techstacks.auto_game.games.azur_lane.interface.scene import *

SCENES_REGISTERED = {x.name: x for x in globals().values() if type(x) is Scene.__class__ and issubclass(x, Scene)}


def update_scenes(self, scene_cur, scene_prev=None):
    self.window.scene_prev, self.window.scene_cur = scene_prev or self.window.scene_cur, scene_cur


class Gateway:
    def __init__(self, window):
        self.window = window
        self.scene_prev = self._scene_cur = SceneUnknown

    @property
    def scene_cur(self):
        return self.window.scene_cur

    def at(self, scene_name: str):
        return self.scene_cur is SCENES_REGISTERED[scene_name]

    def goto(self, scene_name: str, sleep=1, *args, **kwargs):
        has_arrived = self.scene_cur.goto(self.window, dest := SCENES_REGISTERED[scene_name], sleep, *args, **kwargs)
        if has_arrived:
            self.update_scenes(scene_cur=dest, scene_prev=self.scene_cur)
        return has_arrived

    def update_scenes(self, scene_cur, scene_prev=None):
        if self.window.scene_cur.at(scene_cur):
            return
        self.window.scene_prev, self.window.scene_cur = scene_prev or self.window.scene_cur, scene_cur
        print(f"SWITCH SCENE: {self.window.scene_prev} --> {self.window.scene_cur}")

    def detect_scene(self):
        self.update_scenes(self._detect_scene(self.window))
        return self.window.scene_cur

    @classmethod
    def _detect_scene(cls, window):
        for scene in SCENES_REGISTERED.values():
            if hasattr(scene, "at_this_scene") and scene.at_this_scene(window):
                return scene
        return SceneUnknown
