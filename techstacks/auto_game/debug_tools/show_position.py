import time
from threading import Thread

import pyautogui as pag
import win32gui
from pynput import keyboard

from util.win32 import monitor, common

monitor.set_process_dpi_awareness(1, silent=True)


class Pixel:
    pos_client = None
    rgb_tuple = None
    rgb_int = None


class Config:
    sleep_time = 1
    paused = False


def transform_rbg_int2tuple(rgb_int: int):
    return rgb_int & 0xff, (rgb_int >> 8) & 0xff, (rgb_int >> 16) & 0xff


def transform_rbg_tuple2int(rgb_tuple: tuple):
    return rgb_tuple[0] << 16 | rgb_tuple[1] << 8 | rgb_tuple[2]


def show_position_and_client():
    while True:
        if not Config.paused:
            p = pag.position()
            pos_global = (p.x, p.y)
            hwnd = win32gui.WindowFromPoint(pos_global)
            Pixel.pos_client = win32gui.ScreenToClient(hwnd, pos_global)
            hdc = win32gui.GetWindowDC(hwnd)
            try:
                Pixel.rgb_int = win32gui.GetPixel(hdc, *Pixel.pos_client)
                Pixel.rgb_tuple = transform_rbg_int2tuple(Pixel.rgb_int)
            except:
                Pixel.rgb_int = ""
                Pixel.rgb_tuple = ("", "", "")
            finally:
                win32gui.ReleaseDC(hwnd, hdc)

            pos_global_str = f", ".join((f"{s:>4}" for s in pos_global))
            pos_client_str = f", ".join((f"{s:>4}" for s in Pixel.pos_client))
            rgb_client_str = f", ".join((f"{s:>3}" for s in Pixel.rgb_tuple))

            print("=" * 128)
            print(f"【{win32gui.GetWindowText(hwnd)}】@{hwnd}")
            print(f"Global: ({pos_global_str})  Client: ({pos_client_str})  RGB: ({rgb_client_str}) {Pixel.rgb_int}")

            time.sleep(Config.sleep_time)
        else:
            time.sleep(1)


class EventHandler:
    def __init__(self):
        self._listener_keyboard = None

    def start(self):
        self._listener_keyboard = keyboard.Listener(on_release=self.on_keyboard_release)
        self._listener_keyboard.start()

    def on_keyboard_release(self, key):
        if key is keyboard.Key.f4:
            print("f4 is pressed, copy...")
            common.set_text(f"{[*Pixel.pos_client, Pixel.rgb_int]},")

        elif key is keyboard.Key.f8:
            Config.paused = True
            Config.sleep_time = float(input("Input a new sleep time:\n"))
            Config.paused = False

        elif key is keyboard.Key.f10:
            Config.paused = not Config.paused
            if Config.paused:
                print("Paused")
            else:
                print("Continued")

        elif key is keyboard.Key.f12:
            return False


def main():
    eh = EventHandler()
    eh.start()

    w1 = Thread(target=show_position_and_client())
    w1.start()


if __name__ == '__main__':
    main()
