import time
from threading import Thread

from pynput import keyboard
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Controller as MouseController, Button


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
        self.kb_controller = KeyboardController()
        self.mouse_thread = Thread(target=click_left_button)
        self.mouse_thread.start()

    def start(self):
        self._listener_keyboard = keyboard.Listener(on_release=self.on_keyboard_release)
        self._listener_keyboard.start()

    def on_keyboard_release(self, key):
        if key is keyboard.Key.f2:
            if not Shared.is_pressed_f2:
                Shared.is_pressed_f2 = True
                self.kb_controller.press(Key.space)
            else:
                Shared.is_pressed_f2 = False
                self.kb_controller.release(Key.space)

        if key is keyboard.Key.f3:
            Shared.is_pressed_f3 = not Shared.is_pressed_f3

        if key is keyboard.Key.f4:
            if not Shared.is_pressed_f4:
                Shared.is_pressed_f4 = True
                self.kb_controller.press("f")
            else:
                Shared.is_pressed_f4 = False
                self.kb_controller.release("f")


def main():
    eh = EventHandler()
    eh.start()

    while True:
        x = input("input 'exit' to quit.\n")
        if x == "exit":
            return


if __name__ == '__main__':
    main()
