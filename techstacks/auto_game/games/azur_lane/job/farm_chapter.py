import datetime as dt
import time
from collections import deque
from pathlib import Path

from techstacks.auto_game.games.azur_lane.controller.common import KeyboardHandler
from techstacks.auto_game.games.azur_lane.controller.simulator import Bluestack
from techstacks.auto_game.games.azur_lane.interface import scene
from techstacks.auto_game.games.azur_lane.interface.scene import Namespace, base, am
from util.concurrent import KillableThread

BASE_DIR = f"{Path.home().as_posix()}/Pictures/AutoGame/AzurLane"
EVENT_NAME = "CampaignChapter"


class TaskFarmChapter(KillableThread, KeyboardHandler):
    def __init__(self, simulator: Bluestack, refresh_scene=False, *args, **kwargs):
        KillableThread.__init__(self, *args, **kwargs)
        KeyboardHandler.__init__(self)

        self.refresh = refresh_scene
        self.simulator = simulator
        self.simulator.window_ctl.scene_cur = base.SceneUnknown(self.simulator.window_ctl)

        self.refresh_handler = None
        self.cur_chapter = None

        self.team_01s = deque([4, 5])
        self.target_stage = "13-4"

        self.result_dir = f"{BASE_DIR}/{EVENT_NAME}/{self.target_stage}"
        Path(self.result_dir).mkdir(parents=True, exist_ok=True)
        self.cur_farm_time = 0
        self.max_farm_time = int(input("Input Max Farm Times: "))

    def start(self) -> None:
        super().start()
        self.start_listening()
        self.simulator.gateway.scene_manager.detect_scene()
        self.refresh_handler = KillableThread(target=self.refresh_scene)
        self.refresh_handler.start()

        self.event_handler.resume()

    def stop(self):
        if self.refresh and self.refresh_handler.is_alive():
            self.refresh_handler.terminate()
        if self.is_alive():
            self.terminate()

    def refresh_scene(self):
        while True:
            self.event_handler.wait("can_run")

            self.simulator.gateway.scene_manager.detect_scene()
            time.sleep(1)

    def switch_to_chapter(self, target_chapter_no):
        self.event_handler.wait("can_run")

        self.cur_chapter = self.simulator.window_ctl.scene_cur.recognize_chapter_title(self.simulator.window_ctl)

        delta_no = target_chapter_no - self.cur_chapter
        for _ in range(abs(delta_no)):
            if delta_no > 0:
                self.simulator.window_ctl.left_click([(1807, 513), (1889, 645)], sleep=.3)
            else:
                self.simulator.window_ctl.left_click([(46, 512), (122, 663)], sleep=.3)

    def from_main_to_anchor_aweigh(self):
        self.event_handler.wait("can_run")
        if self.simulator.window_ctl.scene_cur.at(scene.SceneMain):
            self.simulator.gateway.scene_manager.goto(Namespace.scene_anchor_aweigh)

    def from_anchor_aweigh_to_campaign_chapter(self, target_chapter_no=13):
        self.event_handler.wait("can_run")

        if self.simulator.window_ctl.scene_cur.at(scene.SceneAnchorAweigh):
            self.simulator.gateway.scene_manager.goto(Namespace.scene_campaign_chapter)
        if self.simulator.window_ctl.scene_cur.at(scene.SceneCampaignChapter):
            self.switch_to_chapter(target_chapter_no)

    def from_campaign_chapter_to_stage_info(self):
        self.event_handler.wait("can_run")
        chapter_no, stage_no = (int(x) for x in self.target_stage.split("-"))
        if self.simulator.window_ctl.scene_cur.at(scene.SceneCampaignChapter) and self.cur_chapter == chapter_no:
            self.simulator.gateway.scene_manager.goto(Namespace.popup_stage_info, sleep=1, chapter_no=self.target_stage)

    def from_stage_info_to_campaign(self):
        self.event_handler.wait("can_run")
        if self.simulator.window_ctl.scene_cur.at(scene.PopupStageInfo):
            self.simulator.window_ctl.scene_cur.set_automation(self.simulator.window_ctl, turn_on=True)
            self.simulator.gateway.scene_manager.goto(Namespace.popup_fleet_selection_arbitrate)

        if self.simulator.window_ctl.scene_cur.at(scene.PopupFleetSelectionArbitrate):
            self.team_01s.append(cur_team := self.team_01s.popleft())
            self.simulator.window_ctl.scene_cur.choose_team(self.simulator.window_ctl, team_one=cur_team, team_two=6)
            self.simulator.gateway.scene_manager.goto(Namespace.scene_campaign)

    def wait_for_farming(self):
        self.event_handler.wait("can_run")
        if self.simulator.window_ctl.scene_cur.at(scene.SceneBattle):
            time.sleep(5)
        elif self.simulator.window_ctl.scene_cur.at(scene.SceneCampaign):
            time.sleep(5)

    def from_campaign_info_to_campaign(self):
        self.event_handler.wait("can_run")
        if self.simulator.window_ctl.scene_cur.at(scene.PopupCampaignInfo):
            self.simulator.gateway.scene_manager.goto(Namespace.scene_campaign)

    def save_result(self):
        self.event_handler.wait("can_run")
        if self.simulator.window_ctl.scene_cur.at(scene.PopupCampaignReward):
            x, y, w, h = am.get_image_xywh("CampaignChapter.Label_TotalRewards_without_META")
        elif self.simulator.window_ctl.scene_cur.at(scene.PopupCampaignRewardWithMeta):
            x, y, w, h = am.get_image_xywh("CampaignChapter.Label_TotalRewards_with_META")
        else:
            return

        time.sleep(5)
        file = f"{self.result_dir}/{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        self.cur_farm_time += 1
        self.simulator.window_ctl.screenshot(x, y, w, h, save_path=file)
        self.simulator.gateway.scene_manager.goto(Namespace.scene_campaign, sleep=1)
        self.event_handler.wait("can_run_after_battle")

    def run(self) -> None:
        while self.cur_farm_time < self.max_farm_time:
            try:
                self.from_main_to_anchor_aweigh()
                self.from_anchor_aweigh_to_campaign_chapter(target_chapter_no=13)
                self.from_campaign_chapter_to_stage_info()
                self.from_stage_info_to_campaign()
                self.wait_for_farming()
                self.save_result()
                self.from_campaign_info_to_campaign()

            except Exception as e:
                print(e)
            time.sleep(1)
        print("finished")


if __name__ == '__main__':
    bs = Bluestack("BS_AzurLane")
    task = TaskFarmChapter(bs, refresh_scene=True)
    task.start()
    task.join()
