import itertools
import re
import time
from abc import abstractmethod
from hashlib import md5
from pickle import dumps
from typing import Tuple, Union, Any, Optional

import cv2
import numpy as np
import pytesseract
from cv2 import (
    TM_CCOEFF_NORMED, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED,
)
from matplotlib import pyplot as plt
from scipy.spatial import distance_matrix

from techstacks.auto_game.games.azur_lane.config import CONFIG_SCENE, DIR_BASE
from techstacks.auto_game.games.azur_lane.controller.simulator import AzurLaneWindow
from util.io import load_yaml

ASSETS = load_yaml(CONFIG_SCENE)


def gen_key(*args, **kwargs):
    return md5(dumps((args, kwargs))).hexdigest()


def cache(max_cache=10):
    CACHE = {}

    def decorator(fn):

        def wrapper(*args, **kwargs):
            if not (md5_key := gen_key(*args, **kwargs)) in CACHE:
                if len(CACHE) >= max_cache:
                    CACHE.pop(list(CACHE.keys())[0])
                CACHE[md5_key] = fn(*args, **kwargs)
            return CACHE[md5_key]

        return wrapper

    return decorator


@cache(max_cache=10)
def read_template(file):
    try:
        return cv2.imread(f"{DIR_BASE}{file}")[:, :, ::-1]
    except:
        print(file)


def match_single_template(origin: np.ndarray, template: np.ndarray, method=TM_CCORR_NORMED, debug=True) -> Tuple[
    Any, Any, Any, Any]:
    result = cv2.matchTemplate(origin, template, method)

    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if debug:
        origin_copy = origin.copy()
        width, height = template.shape[:2][::-1]
        top_left = max_loc
        bottom_right = (top_left[0] + width, top_left[1] + height)
        cv2.rectangle(origin_copy, top_left, bottom_right, (255, 255, 255), 2)
        plt.imshow(origin_copy)
        plt.show()
    return min_val, max_val, min_loc, max_loc


def match_multi_template(img_ori: np.ndarray, img_tem: np.ndarray, method=TM_CCOEFF_NORMED, threshold=.8, debug=True):
    res = cv2.matchTemplate(img_ori, img_tem, method)
    if method in (TM_SQDIFF, TM_SQDIFF_NORMED):
        loc = np.where(res <= threshold)
    else:
        loc = np.where(res >= threshold)
    print(cv2.minMaxLoc(res))

    if debug:
        img_cp = img_ori.copy()
        w, h = img_tem.shape[:2][::-1]
        locs = np.array([loc[1], loc[0]]).T
        if len(locs) > 0:
            locs = combine_similar_points(locs)
        for pt in locs:
            print(pt)
            cv2.rectangle(img_cp, pt, (pt[0] + w, pt[1] + h), (255, 0, 0), 2)
        plt.imshow(img_cp)
        plt.show()

    return list(np.array([loc[1], loc[0]]).T)


def get_eigen(*objects):
    return itertools.chain.from_iterable(xy_rgb["__Eigen"] for xy_rgb in objects)


def get_image_xywh(obj):
    lt, rb = (point[:2] for point in obj["__Img"])
    return lt[0], lt[1], rb[0] - lt[0], rb[1] - lt[1]


def goto_scene_main(window: AzurLaneWindow):
    window.left_click(ASSETS["AnchorAweigh"]["Button_BackToMain"], sleep=1)


def ocr_preprocess(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Morph open to remove noise
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    final = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)

    return final


def ocr_int(img, config):
    final_img = ocr_preprocess(img)
    data = pytesseract.image_to_string(final_img, lang='eng', config=config)
    return data


def ocr_eng(img, config):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Morph open to remove noise
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    final_img = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    cv2.imshow("fi", final_img)

    data = pytesseract.image_to_string(final_img, lang='eng', config=config)
    return data


def ocr_zhtw(img, config):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    data = pytesseract.image_to_string(thresh, lang='chi_tra', config=config)

    return data


def combine_similar_points(points, threshold=50):
    points = np.array(points)
    points_sorted = points[np.lexsort((points[:, 1], points[:, 0]))]
    dm = distance_matrix(points_sorted, points_sorted)
    return points_sorted[np.unique((dm < threshold).argmax(axis=0))]


class Namespace:
    scene_main = "Scene.Main"
    scene_anchor_aweigh = "Scene.AnchorAweigh"
    popup_rescue_sos = "Popup.AnchorAweigh.RescueSOS"
    scene_campaign = "Scene.Campaign"
    popup_campaign_info = "Popup.Campaign.Info"
    scene_battle_formation = "Scene.Battle.Formation"
    scene_battle = "Scene.Battle"
    popup_get_ship = "Popup.GetShip"
    scene_battle_checkpoint = "Scene.Battle.Checkpoint"
    scene_battle_get_items = "Scene.Battle.GetItems"
    scene_battle_result = "Scene.Battle.Result"

    popup_stage_info = "Popup.StageInfo"
    popup_fleet_selection = "Popup.FleetSelection"
    popup_fleet_selection_arbitrate = "Popup.FleetSelectionArbitrate"
    popup_fleet_selection_fixed = "Popup.FleetSelectionFixed"
    popup_fleet_selection_duty = "Popup.FleetSelection.Duty"

    popup_campaign_reward = "Popup.Campaign.Reward"

    scene_campaign_chapter = "Scene.Campaign.Chapter"


class Scene:
    window = None

    def __init__(self, window: AzurLaneWindow, scene_from=None):
        self.window = window
        self.scene_from = scene_from
        self._bounds = None

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def bounds(self) -> dict:
        pass

    def at(self, scene):
        return isinstance(self, scene)

    def get_bound_methods(self):
        if self._bounds is None:
            self._bounds = self.bounds
        return self._bounds

    def update_scenes(self, scene_cur, scene_prev=None):
        self.window.scene_prev, self.window.scene_cur = scene_prev or self.window.scene_cur, scene_cur

    def is_at_this_scene(self, window: AzurLaneWindow = None):
        window = window if window is not None else self.window
        return self._is_at_this_scene(window)

    @classmethod
    @abstractmethod
    def _is_at_this_scene(cls, window: AzurLaneWindow) -> bool:
        """Custom method to implement"""
        pass

    def goto(self, next_scene, sleep=0, *args, **kwargs):
        if (next_scene := scene_map.get(next_scene)) is None:
            has_arrived = False
            print(f"Has arrived: {has_arrived}")
            return has_arrived

        if not self.is_at_this_scene():
            print(f"Not here: {self}")
            return False

        self.bounds[next_scene.name](self.window, *args, **kwargs)
        if has_arrived := next_scene._is_at_this_scene(self.window):
            self.update_scenes(next_scene(self.window))
        else:
            self.window.scene_cur.detect_scene()

        if sleep > 0:
            time.sleep(sleep)
        return has_arrived

    def goto_(self, window: AzurLaneWindow, next_scene: str):
        return self.bounds[next_scene](window)

    def detect_scene(self):
        if (cur_scene := self._detect_scene(self.window)) is None:
            return cur_scene(self.window)

        self.update_scenes(cur_scene(self.window))
        return self.window.scene_cur

    @classmethod
    def _detect_scene(cls, window):
        for scene in scenes_maybe:
            # print("*" * 36 + f"{scene.name}" + "*" * 36)
            if scene._is_at_this_scene(window):
                return scene
        return SceneUnknown

    def __repr__(self):
        return f"{self.window} @ {self.name}"


class SceneUnknown(Scene):
    name = "Scene.Unknown"
    bounds = dict()

    @classmethod
    def _is_at_this_scene(cls, window: AzurLaneWindow) -> bool:
        if Scene._detect_scene(window).name == "Scene.Unknown":
            return True
        return False


class SceneMain(Scene):
    name = Namespace.scene_main

    @property
    def bounds(self) -> dict:
        bounds = {
            Namespace.scene_anchor_aweigh: self.goto_scene_anchor_aweigh
        }
        return bounds

    @classmethod
    def _is_at_this_scene(cls, window: AzurLaneWindow) -> bool:
        points_to_check = get_eigen(
            ASSETS["Main"]["Icon_Resources"]["Icon_Oil"],
            ASSETS["Main"]["Icon_Resources"]["Icon_Money"],
            ASSETS["Main"]["Icon_Resources"]["Icon_Diamond"],
            ASSETS["Main"]["Button_Shop"],
            ASSETS["Main"]["Button_AnchorAweigh"],
        )
        return window.compare_with_pixel(points_to_check, threshold=1)

    @staticmethod
    def goto_scene_anchor_aweigh(window: AzurLaneWindow):
        window.left_click(ASSETS["Main"]["Button_AnchorAweigh"], sleep=1.5)

    @staticmethod
    def open_popup_living_area(window: AzurLaneWindow):
        window.left_click(ASSETS["Main"]["Button_LivingArea"])

    def has_new_notice(self):
        asset = ASSETS["Main"]["Button_LivingArea"]["State_HasNewNotice"]
        return self.window.compare_with_template(asset["__ImageRect"], read_template(asset["__Image"]), .8)


class SceneAnchorAweigh(Scene):
    name = Namespace.scene_anchor_aweigh

    @property
    def bounds(self) -> dict:
        destinations = {
            Namespace.scene_main: goto_scene_main,
            Namespace.popup_rescue_sos: self.open_popup_rescue_sos
        }
        return destinations

    @classmethod
    def _is_at_this_scene(cls, window: AzurLaneWindow) -> bool:
        points_to_check = get_eigen(
            ASSETS["AnchorAweigh"]["Icon_Resources"]["Icon_Oil"],
            ASSETS["AnchorAweigh"]["Icon_Resources"]["Icon_Money"],
            ASSETS["AnchorAweigh"]["Icon_Resources"]["Icon_Diamond"],
            ASSETS["AnchorAweigh"]["Button_MainBattleLine"],
            ASSETS["AnchorAweigh"]["Label_WeighAnchor"],
        )
        return window.compare_with_pixel(points_to_check, threshold=1)

    @staticmethod
    def open_popup_rescue_sos(window: AzurLaneWindow):
        window.left_click(ASSETS["AnchorAweigh"]["Button_RescueSOS"], sleep=1)

    def recognize_rescue_times(self, max_retry=20):
        x, y, w, h = get_image_xywh(ASSETS["AnchorAweigh"]["Button_RescueSOS"])
        image = self.window.screenshot(x, y, w, h)
        try:
            res = int(ocr_int(image, config="--psm 8 --oem 3 -c tessedit_char_whitelist=012345678")[0])
        except:
            res = None
            for _ in range(max_retry):
                if res := self.recognize_rescue_times(max_retry=0) is not None: break
        finally:
            return res


class PopupRescueSOS(Scene):
    name = Namespace.popup_rescue_sos

    @property
    def bounds(self) -> dict:
        destinations = {
            Namespace.scene_main: goto_scene_main,
            Namespace.scene_anchor_aweigh: self.goto_scene_anchor_aweigh,
            Namespace.scene_campaign_chapter: self.goto_scene_chapter03,
        }
        return destinations

    @classmethod
    def _is_at_this_scene(cls, window: AzurLaneWindow) -> bool:
        points_to_check = get_eigen(
            ASSETS["AnchorAweigh"]["Button_RescueSOS"]["Popup_RescueSOS"],
        )
        return window.compare_with_pixel(points_to_check, threshold=1)

    @staticmethod
    def goto_scene_anchor_aweigh(window: AzurLaneWindow):
        window.left_click(ASSETS["AnchorAweigh"]["Button_RescueSOS"]["Popup_RescueSOS"]["Button_GoBack"], sleep=1)

    def is_signal_found(self):
        points_to_check = get_eigen(
            ASSETS["AnchorAweigh"]["Button_RescueSOS"]["Popup_RescueSOS"]["Button_Chapter03"]["State_SignalFound"],
        )
        return self.window.compare_with_pixel(points_to_check, threshold=1)

    @staticmethod
    def goto_scene_chapter03(window: AzurLaneWindow):
        window.left_click(ASSETS["AnchorAweigh"]["Button_RescueSOS"]["Popup_RescueSOS"]["Button_Chapter03"], sleep=1.5)


class SceneCampaignChapter(Scene):
    name = Namespace.scene_campaign_chapter
    map_chapter_names = {
        "虎!虎!虎!": 1,
        "玻瑚海首秀": 2,
        "決戰中途島": 3,
        "所羅門的噩夢上": 4,
        "所羅門的噩夢中": 5,
        "所羅門的噩夢下": 6,
        "混沐之夜": 7,
        "科曼多爾海戰": 8,
        "庫拉灣海戰": 9,
        "科隆班加拉島夜戰": 10,
        "奧古斯塔皇后灣海戰": 11,
        "馬里亞納風雲上": 12,
        "馬里亞納風雲下": 13,
    }

    def __init__(self, window: AzurLaneWindow, scene_from=None):
        super().__init__(window, scene_from)
        self.chapter_no = None

    @property
    def bounds(self) -> dict:
        destinations = {
            Namespace.scene_main: goto_scene_main,
            Namespace.scene_anchor_aweigh: goto_scene_main,
            Namespace.popup_stage_info: self.open_stage_popup
        }
        return destinations

    @classmethod
    def _is_at_this_scene(cls, window: AzurLaneWindow) -> bool:
        points_to_check = get_eigen(
            ASSETS["CampaignChapter"]["Button_BackToMain"],
            ASSETS["CampaignChapter"]["Label_WeighAnchor"],
            ASSETS["Main"]["Icon_Resources"]["Icon_Oil"],
            ASSETS["Main"]["Icon_Resources"]["Icon_Money"],
            ASSETS["Main"]["Icon_Resources"]["Icon_Diamond"],
        )
        return window.compare_with_pixel(points_to_check, threshold=1)

    def recognize_chapter_title(self, max_retry=20) -> Union[int, None]:
        chapter_title = self._recognize_chapter_title(self.window, max_retry)
        print(chapter_title)
        self.chapter_no = None or self.map_chapter_names.get(chapter_title)
        return self.chapter_no

    @classmethod
    def _recognize_chapter_title(cls, window: AzurLaneWindow, max_retry=20) -> Union[int, None]:
        x, y, w, h = get_image_xywh(ASSETS["CampaignChapter"]["Chapters"]["ChapterNo"])
        image = window.screenshot(x, y, w, h)
        try:
            res = ocr_zhtw(image, config="--psm 7 --oem 2")
            res = re.sub("\s", "", res)
        except:
            res = None
            for _ in range(max_retry):
                if res := cls._recognize_chapter_title(window, max_retry=0) is not None:
                    break
        finally:
            return res

    @staticmethod
    def open_stage_popup(window, chapter_no=None) -> bool:
        if chapter_no == "3-5":
            window.left_click(ASSETS["CampaignChapter"]["Chapters"]["Chapter_03"]["3-5"])
        return False

    @staticmethod
    def go_back_to_anchor_aweigh(window) -> bool:
        window.left_click(ASSETS["CampaignChapter"]["Chapters"]["Button_BackToAnchorAweigh"])
        return False


class PopupStageInfo(Scene):
    name = Namespace.popup_stage_info

    @property
    def bounds(self) -> dict:
        destinations = {
            Namespace.scene_campaign: self.close_popup,
            Namespace.popup_fleet_selection: self.goto_immediate_start,
            Namespace.popup_fleet_selection_arbitrate: self.goto_immediate_start,
            Namespace.popup_fleet_selection_fixed: self.goto_immediate_start,
        }
        return destinations

    @classmethod
    def _is_at_this_scene(cls, window: AzurLaneWindow) -> bool:
        points_to_check = get_eigen(
            ASSETS["PopupStageInfo"]["Label_WeighAnchor"],
            ASSETS["PopupStageInfo"]["Button_ImmediateStart"],
        )
        return window.compare_with_pixel(points_to_check, threshold=1)

    @staticmethod
    def goto_immediate_start(window: AzurLaneWindow):
        window.left_click(ASSETS["PopupStageInfo"]["Button_ImmediateStart"], sleep=1)

    @staticmethod
    def close_popup(window: AzurLaneWindow):
        window.left_click(ASSETS["PopupStageInfo"]["Button_Close"], sleep=1)

    def is_automation(self) -> bool:
        lt, rb = ASSETS["PopupStageInfo"]["Button_Automation"]["__Rect"]
        mid = tuple(int((lt[i] + rb[i]) / 2) for i in range(2))
        rgb_tuple = self.window.get_pixel(*mid, as_int=False)

        return rgb_tuple[0] > 100

    def set_automation(self, turn_on=True, sleep=1):
        if turn_on is not self.is_automation():
            self.window.left_click(ASSETS["PopupStageInfo"]["Button_Automation"], sleep=1)
        time.sleep(sleep)


class PopupFleetSelection(Scene):
    name = Namespace.popup_fleet_selection

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_fleet_fixed = None

    @property
    def bounds(self) -> dict:
        destinations = {
            Namespace.scene_campaign_chapter: self.close,
            Namespace.scene_campaign: self.goto_immediate_start,
            Namespace.popup_fleet_selection_duty: self.goto_fleet_duty,
        }
        return destinations

    @classmethod
    def _is_at_this_scene(cls, window: AzurLaneWindow) -> bool:
        points_to_check = get_eigen(
            ASSETS["PopupFleetSelect"]["Label_FleetSelect"],
            ASSETS["PopupFleetSelect"]["Button_ImmediateStart"],
        )
        return window.compare_with_pixel(points_to_check, threshold=1)

    @staticmethod
    def goto_immediate_start(window: AzurLaneWindow):
        window.left_click(ASSETS["PopupFleetSelect"]["Button_ImmediateStart"], sleep=1)

    @staticmethod
    def goto_fleet_duty(window: AzurLaneWindow):
        window.left_click(ASSETS["PopupFleetSelect"]["Button_ChangeDuty"], sleep=1)

    @staticmethod
    def close(window: AzurLaneWindow):
        window.left_click(ASSETS["PopupFleetSelect"]["Button_Close"], sleep=1)

    @classmethod
    def _is_fixed_fleet(cls, window: AzurLaneWindow):
        points_to_check = get_eigen(
            ASSETS["PopupFleetSelect"]["Button_ChangeFormation"],
        )
        return window.compare_with_pixel(points_to_check, threshold=1)


class PopupFleetSelectionArbitrate(PopupFleetSelection):
    name = Namespace.popup_fleet_selection_arbitrate

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_fleet_fixed = False

    @classmethod
    def _is_at_this_scene(cls, window: AzurLaneWindow) -> bool:
        return (not cls._is_fixed_fleet(window)) and super()._is_at_this_scene(window)

    def choose_team(self, team_one=None, team_two=None):
        btns = ASSETS["PopupFleetSelect"]["Formation"]
        map_fleet_no = dict(
            enumerate([f"Button_Fleet{x}" for x in ("One", "Two", "Three", "Four", "Five", "Six")], start=1))

        if (key := map_fleet_no.get(team_one)) is not None:
            btn = btns["Button_ChooseTeamOne"]
            self.window.left_click(btn, sleep=.5)
            self.window.left_click(btn[key], sleep=.5)

        if (key := map_fleet_no.get(team_two)) is not None:
            btn = btns["Button_ChooseTeamTwo"]
            self.window.left_click(btn, sleep=.5)
            self.window.left_click(btn[key], sleep=1)


class PopupFleetSelectionFixed(PopupFleetSelection):
    name = Namespace.popup_fleet_selection_fixed

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_fleet_fixed = True

    @classmethod
    def _is_at_this_scene(cls, window: AzurLaneWindow) -> bool:
        return cls._is_fixed_fleet(window) and super()._is_at_this_scene(window)


class PopupFleetSelectionDuty(PopupFleetSelection):
    name = Namespace.popup_fleet_selection_duty

    def bounds(self) -> dict:
        destinations = {
            Namespace.scene_campaign_chapter: self.close,
            Namespace.scene_campaign: self.goto_immediate_start,
            Namespace.popup_fleet_selection_duty: self.goto_fleet_duty,
        }
        return destinations

    @classmethod
    def _is_at_this_scene(cls, window: AzurLaneWindow) -> bool:
        duties = cls.show_duty(window)

        return duties != 0b0 and super()._is_at_this_scene(window)

    @staticmethod
    def show_duty(window):
        btn = ASSETS["PopupFleetSelect"]["Button_ChangeDuty"]
        cmp = lambda x: window.compare_with_pixel(get_eigen(x), threshold=1)
        res = 0b0

        s0, s1 = (cmp(btn["Submarine"][state]) for state in ["Button_AutoEngage", "Button_StandBy"])
        if s0 and (not s1):
            res |= 0b1
        elif (not s0) and s1:
            res |= (0b1 << 1)

        for idx, state in enumerate(("Button_StandBy", "Button_AllBattle", "Button_Flagship", "Button_NormalBattle"),
                                    start=2):
            if cmp(btn["NormalFleet"][state]) is True:
                res |= (0b1 << idx)

        return res

    def set_duty_marine(self, team_one) -> bool:
        btn_marine = ASSETS["PopupFleetSelect"]["Button_ChangeDuty"]["NormalFleet"]
        duty_marines = {
            0b1000: btn_marine["Button_NormalBattle"],
            0b0100: btn_marine["Button_Flagship"],
            0b0010: btn_marine["Button_AllBattle"],
            0b0001: btn_marine["Button_StandBy"],
        }
        if (duty_marine := duty_marines.get(team_one)) is None:
            return False
        self.window.left_click(duty_marine, sleep=.75)
        return (self.show_duty(self.window) >> 2) == team_one

    def set_duty_submarine(self, team_submarine=0b01) -> bool:
        btn_submarine = ASSETS["PopupFleetSelect"]["Button_ChangeDuty"]["Submarine"]
        duty_submarines = {
            0b10: btn_submarine["Button_AutoEngage"],
            0b01: btn_submarine["Button_StandBy"],
        }
        if (duty_submarine := duty_submarines.get(team_submarine)) is None:
            return False
        self.window.left_click(duty_submarine, sleep=.75)
        return (self.show_duty(self.window) & 0b000011) == duty_submarine


class SceneCampaignChapter03(SceneCampaignChapter):
    @classmethod
    def _is_at_this_scene(cls, window: AzurLaneWindow) -> bool:
        return super()._is_at_this_scene(window) and cls._recognize_chapter_title(window) == 3

    def goto_sos_rescue(self, chapter_no=None) -> bool:
        pass


class SceneCampaign(Scene):
    name = Namespace.scene_campaign

    @property
    def bounds(self) -> dict:
        destinations = {
            Namespace.scene_main: goto_scene_main
        }
        return destinations

    @classmethod
    def _is_at_this_scene(cls, window: AzurLaneWindow) -> bool:
        points_to_check = get_eigen(
            ASSETS["Campaign"]["Label_LimitTime"],
            ASSETS["Campaign"]["Button_BackToMain"],
            ASSETS["Main"]["Icon_Resources"]["Icon_Oil"],
            ASSETS["Main"]["Icon_Resources"]["Icon_Money"],
            ASSETS["Main"]["Icon_Resources"]["Icon_Diamond"],
        )
        return window.compare_with_pixel(points_to_check, threshold=1)

    def is_commission_popup(self):
        points_to_check = get_eigen(
            ASSETS["Main"]["Button_Commission"]["Popup_Commission"]["Label_Commission"],
        )
        return self.window.compare_with_pixel(points_to_check, threshold=1)

    def is_commissions_all_folded(self):
        points_to_check = get_eigen(
            ASSETS["Main"]["Button_Commission"]["Popup_Commission"]["State_AllFolded"],
        )
        return self.window.compare_with_pixel(points_to_check, threshold=1)

    def is_automation_on(self) -> bool:
        button = ASSETS["Campaign"]["Button_Automation"]
        return self.window.compare_with_template(button["__Rect"], read_template(button["State_On"]["__Image"]),
                                                 threshold=.999)

    def is_automation_off(self) -> bool:
        button = ASSETS["Campaign"]["Button_Automation"]
        return self.window.compare_with_template(button["__Rect"], read_template(button["State_Off"]["__Image"]),
                                                 threshold=.999)

    def is_formation_locked(self):
        points_to_check = get_eigen(ASSETS["Campaign"]["Button_FormationLock"]["State_On"])
        return self.window.compare_with_pixel(points_to_check, threshold=1)

    def is_strategy_popup(self):
        points_to_check = get_eigen(
            ASSETS["Campaign"]["Button_Strategy"]["State_Expanded"]
        )
        return self.window.compare_with_pixel(points_to_check, threshold=1)

    def recognize_fleet_no(self, max_retry=20) -> int:
        x, y, w, h = get_image_xywh(ASSETS["Campaign"]["Label_FleetNo"])
        image = self.window.screenshot(x, y, w, h)
        try:
            return int(ocr_int(image).strip())
        except:
            for _ in range(max_retry):
                res = self.recognize_fleet_no(max_retry=0)
        return res

    def get_fleet_formation(self) -> Optional[str]:
        if self.is_strategy_popup():
            for state in ("State_SingleLineAssault", "State_DoubleLineAdvance", "State_CircularDefense"):
                points_to_check = self.get_points(
                    ASSETS["Campaign"]["Button_Strategy"]["State_Expanded"]["Button_SwitchFormation"][state]
                )
                if self.compare_with_pixel(points_to_check, threshold=1):
                    return state
        return None

    @staticmethod
    def _detect_enemy(img_screen, templates, threshold=.1, method=TM_SQDIFF_NORMED):
        res = []
        for img_template in templates:
            res.extend(match_multi_template(
                img_screen, img_template, threshold=threshold, method=method, debug=False
            ))

        if len(res) > 0:
            res = combine_similar_points(np.array(res))

        return res

    def detect_enemy(self, scale, img_screen=None, threshold=.1, method=TM_SQDIFF_NORMED):
        print(scale)
        if img_screen is None:
            img_screen = self.window.screenshot()

        templates = [read_template(x) for x in ASSETS["Campaign"]["Enemy"]["Scale"][scale]["__Images"].values()]
        res = self._detect_enemy(img_screen, templates, threshold, method)
        if len(res) > 0 and scale != "Boss":
            res += np.array([50, 80])
        return list(res)

    def attack_enemies(self):
        img_screen_1 = self.window.screenshot()
        time.sleep(1.5)
        img_screen_2 = self.window.screenshot()
        enemy_type = {4: "Boss", 3: "Large", 2: "Medium", 1: "Small"}
        enemies = {
            k: self.detect_enemy(v, img_screen_1)
            for k, v in enemy_type.items()
        }
        for k, v in enemy_type.items():
            enemies[k].extend(self.detect_enemy(v, img_screen_2))
            if len(enemies[k]) > 0:
                enemies[k] = combine_similar_points(np.array(enemies[k]))
        print(enemies)
        for k in (4, 3, 2, 1):
            if len(enemies_found := enemies[k]) > 0:
                self.window.left_click(tuple(enemies_found[0]), sleep=1)
                return True
        return False


class PopupGetShip(Scene):
    name = Namespace.popup_get_ship

    @property
    def bounds(self) -> dict:
        destinations = {
            Namespace.scene_campaign: self.goto_campaign
        }
        return destinations

    @classmethod
    def _is_at_this_scene(cls, window: AzurLaneWindow) -> bool:
        points_to_check = get_eigen(
            ASSETS["Campaign"]["Popup_GetShip"],
        )
        return window.compare_with_pixel(points_to_check, threshold=1)

    @staticmethod
    def goto_campaign(window):
        window.left_click(ASSETS["Campaign"]["Popup_GetShip"]["Button_Exit"], sleep=2)


class PopupCampaignInfo(Scene):
    name = Namespace.popup_campaign_info

    @property
    def bounds(self) -> dict:
        destinations = {
            Namespace.scene_campaign: self.goto_campaign
        }
        return destinations

    @classmethod
    def _is_at_this_scene(cls, window: AzurLaneWindow) -> bool:
        points_to_check = get_eigen(
            ASSETS["Campaign"]["Popup_Information"],
            ASSETS["Campaign"]["Popup_Information"]["Button_Ensure"],
        )
        return window.compare_with_pixel(points_to_check, threshold=1)

    @staticmethod
    def goto_campaign(window):
        window.left_click(ASSETS["Campaign"]["Popup_Information"]["Button_Ensure"], sleep=.75)


class SceneBattleFormation(Scene):
    name = Namespace.scene_battle_formation

    @property
    def bounds(self) -> dict:
        destinations = {
            Namespace.scene_main: goto_scene_main,
            Namespace.scene_battle: self.goto_battle,
        }
        return destinations

    @classmethod
    def _is_at_this_scene(cls, window: AzurLaneWindow) -> bool:
        points_to_check = get_eigen(
            ASSETS["BeforeBattle"]["Formation"]["Button_WeighAnchor"],
            ASSETS["BeforeBattle"]["Formation"]["Label_MainFleet"],
            ASSETS["BeforeBattle"]["Formation"]["Label_VanguardFleet"],
        )
        return window.compare_with_pixel(points_to_check, threshold=1)

    @staticmethod
    def goto_battle(window: AzurLaneWindow):
        window.left_click(ASSETS["BeforeBattle"]["Formation"]["Button_WeighAnchor"], sleep=2.5)

    def is_automation(self) -> bool:
        points_to_check = get_eigen(
            ASSETS["BeforeBattle"]["Formation"]["Automation"]["Button_Automation"]["State_On"]
        )
        return self.window.compare_with_pixel(points_to_check, threshold=1)

    def set_automation(self, turn_on=True):
        if self.is_automation() is not turn_on:
            self.window.left_click(ASSETS["BeforeBattle"]["Formation"]["Automation"]["Button_Automation"], sleep=1)
        return self.is_automation() is turn_on

    def is_auto_submarine_off(self) -> bool:
        points_to_check = get_eigen(
            ASSETS["BeforeBattle"]["Formation"]["Automation"]["Button_AutoSubmarine"]["State_Off"]
        )
        return self.window.compare_with_pixel(points_to_check, threshold=1)

    def set_auto_submarine(self, turn_on=False):
        if not self.is_automation():
            return turn_on is False

        if self.is_auto_submarine_off() is turn_on:
            self.window.left_click(ASSETS["BeforeBattle"]["Formation"]["Automation"]["Button_AutoSubmarine"], sleep=1)
        return self.is_auto_submarine_off() is turn_on


class SceneBattle(Scene):
    name = Namespace.scene_battle

    @property
    def bounds(self) -> dict:
        destinations = {
        }
        return destinations

    @classmethod
    def _is_at_this_scene(cls, window: AzurLaneWindow) -> bool:
        points_to_check = get_eigen(
            ASSETS["Battle"]["Button_Pause"],
        )
        return window.compare_with_pixel(points_to_check, threshold=1)


class SceneBattleCheckpoint(Scene):
    name = Namespace.scene_battle_checkpoint

    @property
    def bounds(self) -> dict:
        destinations = {
            Namespace.scene_battle_get_items: self.goto_get_items
        }
        return destinations

    @classmethod
    def _is_at_this_scene(cls, window: AzurLaneWindow) -> bool:
        points_to_check = get_eigen(
            ASSETS["AfterBattle"]["Checkpoint"]["Label_Checkpoint"],
        )

        return window.compare_with_pixel(points_to_check)

    @staticmethod
    def goto_get_items(window: AzurLaneWindow):
        window.left_click((1850, 200), sleep=.5)


class SceneBattleGetItems(Scene):
    name = Namespace.scene_battle_get_items

    @property
    def bounds(self) -> dict:
        destinations = {
            Namespace.scene_battle_result: self.goto_battle_results
        }
        return destinations

    @classmethod
    def _is_at_this_scene(cls, window: AzurLaneWindow) -> bool:
        points_to_check = get_eigen(
            ASSETS["AfterBattle"]["GetItems"]["Label_GetItems"],
        )

        return window.compare_with_pixel(points_to_check)

    @staticmethod
    def goto_battle_results(window: AzurLaneWindow):
        window.left_click((1850, 200), sleep=.5)


class SceneBattleResult(Scene):
    name = Namespace.scene_battle_result

    @property
    def bounds(self) -> dict:
        destinations = {
            Namespace.scene_campaign: self.goto_campaign,
        }
        return destinations

    @classmethod
    def _is_at_this_scene(cls, window: AzurLaneWindow) -> bool:
        points_to_check = get_eigen(
            ASSETS["AfterBattle"]["BattleResult"]["Button_DamageReport"],
            ASSETS["AfterBattle"]["BattleResult"]["Button_Ensure"],
        )

        return window.compare_with_pixel(points_to_check)

    @staticmethod
    def goto_campaign(window: AzurLaneWindow):
        window.left_click(ASSETS["AfterBattle"]["BattleResult"]["Button_Ensure"])


class PopupCampaignReward(Scene):
    name = Namespace.popup_campaign_reward

    @property
    def bounds(self) -> dict:
        destinations = {
            Namespace.scene_campaign: self.goto_campaign
        }
        return destinations

    @classmethod
    def _is_at_this_scene(cls, window: AzurLaneWindow) -> bool:
        points_to_check_1 = get_eigen(
            ASSETS["CampaignChapter"]["Label_TotalRewards_without_META"],
            ASSETS["CampaignChapter"]["Label_TotalRewards_without_META"]["Button_GoAgain"],
        )
        points_to_check_2 = get_eigen(
            ASSETS["CampaignChapter"]["Label_TotalRewards_with_META"],
            ASSETS["CampaignChapter"]["Label_TotalRewards_with_META"]["Button_GoAgain"],
        )

        return window.compare_with_pixel(points_to_check_1) or window.compare_with_pixel(points_to_check_2)

    @staticmethod
    def goto_campaign(window: AzurLaneWindow):
        window.left_click((1460, 115), sleep=1.5)  # just a random empty space


scene_map = {
    Namespace.scene_main: SceneMain,

    Namespace.scene_anchor_aweigh: SceneAnchorAweigh,
    Namespace.popup_rescue_sos: PopupRescueSOS,

    Namespace.scene_campaign: SceneCampaign,
    Namespace.scene_campaign_chapter: SceneCampaignChapter,
    Namespace.popup_stage_info: PopupStageInfo,
    Namespace.popup_fleet_selection: PopupFleetSelection,
    Namespace.popup_fleet_selection_arbitrate: PopupFleetSelectionArbitrate,
    Namespace.popup_fleet_selection_fixed: PopupFleetSelectionFixed,
    Namespace.popup_fleet_selection_duty: PopupFleetSelectionDuty,
    Namespace.popup_campaign_reward: PopupCampaignReward,

    Namespace.scene_battle: SceneBattle,
    Namespace.popup_get_ship: PopupGetShip,
    Namespace.scene_battle_checkpoint: SceneBattleCheckpoint,
    Namespace.scene_battle_get_items: SceneBattleGetItems,
    Namespace.scene_battle_result: SceneBattleResult,
}
scenes_maybe = [
    SceneMain, SceneAnchorAweigh,

    SceneCampaign,
    PopupGetShip,
    PopupCampaignInfo,
    SceneCampaignChapter,

    PopupStageInfo,
    PopupFleetSelectionDuty, PopupFleetSelectionFixed, PopupFleetSelectionArbitrate, PopupFleetSelection,

    PopupCampaignReward,

    SceneBattle,
    SceneBattleFormation,
    SceneBattleCheckpoint,
    SceneBattleGetItems,
    SceneBattleResult,

    PopupRescueSOS,
]
