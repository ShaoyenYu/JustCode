import time

from techstacks.auto_game.games.azur_lane.controller.simulator import Bluestack
from techstacks.auto_game.games.azur_lane.interface import scene
from techstacks.auto_game.games.azur_lane.interface.scene import Namespace
from util.concurrent import KillableThread, PauseEventHandler


class TaskFarmSubmarineSOS(KillableThread):
    def __init__(self, simulator: Bluestack, refresh_scene=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.refresh = refresh_scene
        self.simulator = simulator
        self.simulator.window_ctl.scene_cur = scene.SceneUnknown(self.simulator.window_ctl)
        self.event_handler = PauseEventHandler(self, "can_run", "can_run_after_battle")
        self.refresh_handler = None

    def start(self) -> None:
        super().start()

        self.simulator.gateway.detect_scene()
        self.refresh_handler = KillableThread(target=self.refresh_scene)
        self.refresh_handler.start()

        self.event_handler.resume("can_run")

    def stop(self):
        if self.refresh and self.refresh_handler.is_alive():
            self.refresh_handler.terminate()
        if self.is_alive():
            self.terminate()

    def refresh_scene(self):
        while True:
            self.simulator.gateway.detect_scene()
            time.sleep(1)

    def from_main_to_anchor_aweigh(self):
        self.event_handler.wait("can_run")
        if self.simulator.window_ctl.scene_cur.at(scene.SceneMain):
            self.simulator.gateway.goto(Namespace.scene_anchor_aweigh)

    def from_anchor_aweigh_to_popup_rescue_sos(self):
        self.event_handler.wait("can_run")
        if self.simulator.window_ctl.scene_cur.at(scene.SceneAnchorAweigh):
            if (rescue_no := self.simulator.window_ctl.scene_cur.recognize_rescue_times(self.simulator.window_ctl)) > 0:
                print(f"remain rescue times: {rescue_no}")
                self.simulator.gateway.goto(Namespace.popup_rescue_sos)
            return rescue_no

    def from_popup_rescue_sos_to_campaign_chapter(self):
        self.event_handler.wait("can_run")
        if self.simulator.window_ctl.scene_cur.at(scene.PopupRescueSOS):
            if self.simulator.window_ctl.scene_cur.is_signal_found(self.simulator.window_ctl):
                print("signal found")
                self.simulator.gateway.goto(Namespace.scene_campaign_chapter)
            else:
                print("signal not found")
                self.simulator.gateway.goto(Namespace.scene_campaign_chapter, sleep=1)
                # self.simulator.gateway.goto(Namespace.scene_campaign_chapter)

    def from_campaign_chapter_to_stage_rescue_sos(self):
        self.event_handler.wait("can_run")
        if self.simulator.window_ctl.scene_cur.at(scene.SceneCampaignChapter):
            has_arrived = self.simulator.gateway.goto(Namespace.popup_stage_info, sleep=1, chapter_no="3-5")
            if not has_arrived:
                print("not arrived")
                # time.sleep(2)
                self.simulator.gateway.goto(Namespace.scene_anchor_aweigh)

    def from_stage_rescue_sos_to_campaign(self):
        self.event_handler.wait("can_run")
        if self.simulator.window_ctl.scene_cur.at(scene.PopupStageInfo):
            self.simulator.gateway.goto(Namespace.popup_fleet_selection_arbitrate)

        if self.simulator.window_ctl.scene_cur.at(scene.PopupFleetSelectionArbitrate):
            self.simulator.window_ctl.scene_cur.choose_team(self.simulator.window_ctl, team_one=1, team_two=3)
            self.simulator.gateway.goto(Namespace.scene_campaign)

    def from_campaign_to_formation(self):
        self.event_handler.wait("can_run")
        if self.simulator.window_ctl.scene_cur.at(scene.SceneCampaign):
            if self.simulator.window_ctl.scene_cur.attack_enemies(self.simulator.window_ctl):
                time.sleep(8)

    def from_formation_to_battle(self):
        self.event_handler.wait("can_run")
        if self.simulator.window_ctl.scene_cur.at(scene.PopupInfoAutoBattle):
            self.simulator.gateway.goto(Namespace.scene_battle_formation)
        if self.simulator.window_ctl.scene_cur.at(scene.SceneBattleFormation):
            self.simulator.gateway.goto(Namespace.scene_battle)

    def from_checkpoint_to_campaign(self):
        self.event_handler.wait("can_run")
        if self.simulator.window_ctl.scene_cur.at(scene.PopupGetShip):
            self.simulator.gateway.goto(Namespace.scene_campaign)
            time.sleep(10)

        if self.simulator.window_ctl.scene_cur.at(scene.SceneBattleCheckpoint00):
            self.simulator.gateway.goto(Namespace.scene_campaign)
            time.sleep(10)

        if self.simulator.window_ctl.scene_cur.at(scene.SceneBattleCheckpoint01):
            self.simulator.gateway.goto(Namespace.scene_get_items)

        if self.simulator.window_ctl.scene_cur.at(scene.SceneGetItems):
            self.simulator.gateway.goto(Namespace.scene_battle_result)

        if self.simulator.window_ctl.scene_cur.at(scene.SceneBattleResult):
            self.simulator.gateway.goto(Namespace.scene_campaign)
            time.sleep(10)

    def from_campaign_info_to_campaign(self):
        self.event_handler.wait("can_run")
        if self.simulator.window_ctl.scene_cur.at(scene.PopupCampaignInfo):
            self.simulator.gateway.goto(Namespace.scene_campaign)

    def run(self) -> None:
        while True:
            try:
                self.from_main_to_anchor_aweigh()

                if (remain_times := self.from_anchor_aweigh_to_popup_rescue_sos()) == 0:
                    print("finished.")
                    self.stop()
                elif remain_times is not None:
                    print(f"remain times: {remain_times}")

                self.from_popup_rescue_sos_to_campaign_chapter()

                self.from_campaign_chapter_to_stage_rescue_sos()

                self.from_stage_rescue_sos_to_campaign()

                self.from_campaign_to_formation()

                self.from_formation_to_battle()

                self.from_checkpoint_to_campaign()

                self.from_campaign_info_to_campaign()

                while self.simulator.window_ctl.scene_cur.at(scene.SceneBattle):
                    print("at battle, wait...")
                    time.sleep(2)

            except Exception as e:
                print(e)
            time.sleep(1)


if __name__ == '__main__':
    bs = Bluestack("BS_AzurLane")
    task = TaskFarmSubmarineSOS(bs, refresh_scene=True)
    task.start()
    task.join()
