import datetime as dt
import time
from pathlib import Path
from threading import Thread

from pynput import keyboard

from techstacks.auto_game.games.azur_lane.config import CONFIG_SCENE
from techstacks.auto_game.games.azur_lane.controller.simulator import GameWindow
from techstacks.auto_game.games.azur_lane.interface import scene
from util.io import load_yaml
from util.win32 import win32gui

BASE_DIR = f"{Path.home().as_posix()}/Pictures/AutoGame/AzurLane"
EVENT_NAME = "苍红的回响"
STAGE = input("Input Stage Name:\n")
RESULT_DIR = f"{BASE_DIR}/{EVENT_NAME}/{STAGE}"
STAGE_RECT = (1429, 457)

print(f"Result Directory: {RESULT_DIR}")
if (to_continue := input("Input y to continue, other to cancel: ")).lower() != "y":
    raise ValueError("exit...")
Path(RESULT_DIR).mkdir(parents=True, exist_ok=True)

scenes = load_yaml(CONFIG_SCENE)
w1 = GameWindow(window_name="BS_AzurLane")
w2 = GameWindow(window_hwnd=win32gui.FindWindowEx(w1.hwnd, None, None, None))


def log(s, log_level="INFO"):
    text = f"{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|{log_level:<4}|{s}"
    print(text)
    return text


class Config:
    sleep_time = 1
    ended = False
    paused = True
    paused_after_battle = False
    paused_by_mood = False

    is_outside_campaign = True

    battle_counts_on_way = 5
    duty = 0


class EventHandler:
    def __init__(self):
        self._listener_keyboard = None

    def start(self):
        self._listener_keyboard = keyboard.Listener(on_release=self.on_keyboard_release)
        self._listener_keyboard.start()

    def on_keyboard_release(self, key):
        if key is keyboard.Key.f7:
            Config.paused = True
            log(f"Input a new sleep time (current {Config.sleep_time}):\n", "CMD")
            Config.sleep_time = float(input())
            Config.paused = False

        if key is keyboard.Key.f8:
            if Config.paused_by_mood:
                log("Cancel Paused(low mood)...", "CMD")
                Config.paused_by_mood = False

        elif key is keyboard.Key.f9:
            Config.paused_after_battle = not Config.paused_after_battle
            if Config.paused_after_battle:
                log("Paused(after battle)...", "CMD")
            else:
                log("Cancel Paused(after battle)...", "CMD")

        elif key is keyboard.Key.f10:
            Config.paused = not Config.paused
            if Config.paused:
                log("Paused", "CMD")
            else:
                log("Continued", "CMD")


class Operation:
    def __init__(self, window: GameWindow):
        self.window = window
        self.battle_counts = 0

    def scene_main_to_stage(self):
        # RE-IMPLEMENTED
        self.window.left_click((1636, 532))  # weigh anchor
        time.sleep(1.5)
        self.window.left_click((1096, 348))  # enter campaign
        time.sleep(1)

    def go_to_sp3(self, automatic=True):
        self.window.left_click(STAGE_RECT)  # click SP-3
        time.sleep(1)
        if automatic:
            if self.window.pixel_from_window(1308, 894, True) != 5958556:  # which means automatic search is not on
                self.window.left_click((1308, 894))
                time.sleep(.25)

        self.window.left_click((1406, 784))  # click Immediate Start 1
        time.sleep(1)

        log(f"Choose Stage --> SP-3...")

    def choose_fleet(self, team_1=None, team_2=None):
        positions = {
            0: {
                0: (1639, 391),
                1: (1637, 457),
                2: (1642, 520),
                3: (1624, 581),
                4: (1644, 637),
                5: (1642, 705),
            },
            1: {
                0: (1616, 591),
                1: (1648, 659),
                2: (1635, 722),
                3: (1645, 778),
                4: (1645, 842),
                5: (1646, 905),
            },
        }
        if team_1 is not None:
            self.window.left_click((1595, 303))  # Fleet 1
            time.sleep(.5)
            self.window.left_click(positions[0][team_1])
            time.sleep(.5)

        if team_2 is not None:
            self.window.left_click((1593, 489))  # Fleet 1
            time.sleep(.5)
            self.window.left_click(positions[1][team_2])
            time.sleep(.5)

        log(f"Set Team One --> Fleet-{team_1 + 1}, Team Two--> Fleet-{team_2 + 1}...")

    def choose_duty(self, fleet_1_duty=0):
        """
            Args:
                fleet_1_duty: int, optional {0, 1, 2, 3}
                    0: "道中战斗";
                    1: "旗舰战斗";
                    2: "全部战斗";
                    3: "待机";

            Returns:

            """
        duties = {
            0: (754, 294),
            1: (962, 295),
            2: (1256, 298),
            3: (1404, 297),
        }
        duty_name = {
            0: "Normal Battle",
            1: "Flag Ship Battle",
            2: "All Battle",
            3: "Stand By",
        }
        self.window.left_click((1827, 598))  # select Duty
        time.sleep(.75)
        self.window.left_click(duties[fleet_1_duty])  # select Duty
        time.sleep(.5)

        log(f"Set Team One Duty --> {duty_name[fleet_1_duty]:<4}")

    def go_to_sp3_battle(self):
        self.window.left_click((1631, 909))  # click Immediate Start 2
        time.sleep(1)
        self.battle_counts += 1
        log(f"{'-' * 32}Battle_{self.battle_counts:0>3} Started{'-' * 32}")


def loop_farm():
    operator = Operation(w2)

    while True:
        while not (Config.paused or Config.paused_by_mood):
            if scene.PopupCampaignReward.at_this_scene_impl(w1):
                time.sleep(5)
                log("Saving Rewards...")
                w1.screenshot(
                    x=547, y=98,
                    width=1397 - 547, height=982 - 98,
                    save_path=f"{RESULT_DIR}/{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                )
                w2.left_click((1850, 300))  # just an empty space
                time.sleep(1)
                Config.is_outside_campaign = True
            elif scene.PopupCampaignRewardWithMeta.at_this_scene_impl(w1):
                time.sleep(5)
                log("Saving Rewards...")
                w1.screenshot(
                    x=444, y=98,
                    width=1504 - 444, height=982 - 98,
                    save_path=f"{RESULT_DIR}/{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                )
                w2.left_click((1850, 300))  # just an empty space
                time.sleep(1)
                Config.is_outside_campaign = True
            elif scene.SceneMain.at_this_scene_impl(w1):
                operator.scene_main_to_stage()
                Config.is_outside_campaign = True
            elif scene.SceneBattle.at_this_scene_impl(w1) or scene.SceneCampaign.at_this_scene_impl(w1):
                time.sleep(5)
                Config.is_outside_campaign = False
            elif scene.PopupCampaignInfo.at_this_scene_impl(w1):
                scene.PopupCampaignInfo.goto_campaign(w2)
                Config.is_outside_campaign = False
            else:
                Config.is_outside_campaign = False

            if Config.is_outside_campaign:
                while Config.paused_after_battle:
                    log("Paused, press F9 to continue...")
                    time.sleep(10)

                w2.left_click((1460, 115))  # just an empty space
                time.sleep(1.5)

                operator.go_to_sp3(automatic=False)

                Config.duty = int(not bool(Config.duty))
                operator.choose_duty(Config.duty)
                operator.go_to_sp3_battle()

                Config.is_outside_campaign = False

            time.sleep(Config.sleep_time)

        time.sleep(Config.sleep_time)


if __name__ == "__main__":
    eh = EventHandler()
    eh.start()

    thread = Thread(target=loop_farm)
    thread.start()
    thread.join()
