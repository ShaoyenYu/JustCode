import time
from threading import Thread

from pynput import keyboard
from pynput.keyboard import Key, Controller as KeyboardController, Listener as KeyboardListener
from pynput.mouse import Controller as MouseController, Listener as MouseListener, Button


class Shared:
    is_pressed_f2 = False
    is_pressed_f3 = False
    is_pressed_f4 = False


def click_left_button():
    mouse_controller = MouseController()
    while True:
        if Shared.is_pressed_f3:
            mouse_controller.press(Button.left)
            mouse_controller.release(Button.left)
        time.sleep(0.1)


class EventHandler:
    def __init__(self):
        self._listener_keyboard = None
        self._listener_mouse = None

        self.ctl_keyboard = KeyboardController()
        self.ctl_mouse = None

        self.control_thread_mouse = Thread(target=click_left_button)
        self.control_thread_mouse.start()

    def start(self):
        self._listener_keyboard = KeyboardListener(on_release=self.on_keyboard_release)
        self._listener_keyboard.start()
        if input("please input \"MOUSE\" to start mouse function:\n") == "MOUSE":
            self._listener_mouse = MouseListener(on_click=self.on_click)
            self._listener_mouse.start()
            self.ctl_mouse = MouseController()

    def on_click(self, x, y, button, pressed):
        if (button == Button.x2) and (not pressed):
            self.ctl_keyboard.press(Key.space)
            self.ctl_keyboard.release(Key.space)

    def on_keyboard_release(self, key):
        if key is keyboard.Key.f2:
            if not Shared.is_pressed_f2:
                Shared.is_pressed_f2 = True
                self.ctl_keyboard.press(Key.space)
            else:
                Shared.is_pressed_f2 = False
                self.ctl_keyboard.release(Key.space)

        if key is keyboard.Key.f3:
            Shared.is_pressed_f3 = not Shared.is_pressed_f3

        if key is keyboard.Key.f4:
            if not Shared.is_pressed_f4:
                Shared.is_pressed_f4 = True
                self.ctl_keyboard.press("f")
            else:
                Shared.is_pressed_f4 = False
                self.ctl_keyboard.release("f")


def main():
    eh = EventHandler()
    eh.start()

    while True:
        x = input("input 'exit' to quit.\n")
        if x == "exit":
            return


if __name__ == '__main__':
    main()
