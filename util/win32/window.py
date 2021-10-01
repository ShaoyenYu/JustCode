import time
from typing import Optional

import cv2 as cv
import numpy as np
import pyautogui as pag
import win32con
import win32gui
import win32ui
from PIL import Image

from util.win32.types.datatypes import Rect

# Get type PyCDC
hwDC = win32gui.CreateDC("DISPLAY", None, None)
DC = win32ui.CreateDCFromHandle(hwDC)
T_PyCDC = type(DC)
DC.DeleteDC()
del hwDC, DC


def create_data_bitmap(x, y, width, height, DC: T_PyCDC, cDC: T_PyCDC = None):
    """

    Args:
        x: int
            left-top coordinate
        y: int
            left-top coordinate
        width: int
            width of rectangle to capture
        height: int
            height to rectangle to capture
        DC: PyCDC
            source device context
        cDC: PyCDC
            compatible device context to copy bit data into;

    Returns:

    """
    if cDC is None:
        cDC = DC.CreateCompatibleDC()

    data_bitmap = win32ui.CreateBitmap()  # create monochrome bitmaps, should call DeleteObject when it's no longer used
    data_bitmap.CreateCompatibleBitmap(DC, width, height)  # create color bitmaps

    # The SelectObject function selects an object into the specified device context (DC).
    # The new object replaces the previous object of the same type.
    cDC.SelectObject(data_bitmap)
    cDC.BitBlt((0, 0), (width, height), DC, (x, y), win32con.SRCCOPY)

    return data_bitmap


def image_from_bitmap(bitmap, form="array"):
    """
    Decode image from bitarray, the result can be formed as PIL Image or an Numpy array.

    Args:
        bitmap:
        form: str, optional {"image", "array"}

    Returns:

    """
    bitmap_w, bitmap_height = ((_ := bitmap.GetInfo())[k] for k in ("bmWidth", "bmHeight"))

    if form == "array":
        # BGRX to RGB
        image_array = cv.cvtColor(
            np.frombuffer(bitmap.GetBitmapBits(True), dtype="uint8").reshape(bitmap_height, bitmap_w, 4),
            cv.COLOR_BGR2RGB,
        )
        return image_array

    elif form == "image":
        image = Image.frombuffer(
            "RGB", (bitmap_w, bitmap_height), bitmap.GetBitmapBits(True), 'raw', *('BGRX', 0, 1)
        )
        return image
    raise NotImplementedError


def screenshot(src_dc, dst_dc, x, y, width, height, form="array", save_path=None) -> Image:
    """

    Args:
        src_dc:
        dst_dc:
        x: int
            left-top x coordinate of source
        y: int
            left-top y coordinate of source
        width: int
            width to capture
        height: int
            height to capture
        form: str, optional {"array", "image"}
        save_path: str

    Returns:

    """

    data_bitmap = create_data_bitmap(x, y, width, height, src_dc, dst_dc)  # create bitmap

    image = image_from_bitmap(data_bitmap, form=form)  # generate image from bitmap

    if save_path:
        data_bitmap.SaveBitmapFile(dst_dc, save_path)

    win32gui.DeleteObject(data_bitmap.GetHandle())  # release bitmap after using
    return image


def screenshot_by_hwnd(hwnd, x, y, width, height, form="array", save_path=None) -> Image:
    """
    To store an image temporarily, your application must call CreateCompatibleDC to create a DC that is compatible with
    the current window DC. After you create a compatible DC, you create a bitmap with the appropriate dimensions by
    calling the CreateCompatibleBitmap function and then select it into this device context by calling the SelectObject
    function.

    After the compatible device context is created and the appropriate bitmap has been selected into it, you can capture
    the image. The BitBlt function captures images. This function performs a bit block transfer that is, it copies data
    from a source bitmap into a destination bitmap. However, the two arguments to this function are not bitmap handles.
    Instead, BitBlt receives handles that identify two device contexts and copies the bitmap data from a bitmap selected
    into the source DC into a bitmap selected into the target DC. In this case, the target DC is the compatible DC, so
    when BitBlt completes the transfer, the image has been stored in memory. To redisplay the image, call BitBlt a
    second time, specifying the compatible DC as the source DC and a window (or printer) DC as the target DC.

    Args:
        hwnd:
        x:
        y:
        width:
        height:
        form:
        save_path:

    Returns:

    """

    hwDC = win32gui.GetWindowDC(hwnd)
    DC = win32ui.CreateDCFromHandle(hwDC)
    cDC = DC.CreateCompatibleDC()

    img = screenshot(DC, cDC, width, height, x, y, form, save_path)

    DC.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwDC)
    return img


class Window:
    def __init__(self, window_name=None, window_pos=None):
        if window_name:
            self.hwnd = win32gui.FindWindow(0, window_name)
        if window_pos:
            self.hwnd = win32gui.WindowFromPoint(window_pos)
        self.rect = self.get_wiondow_rect()

        # for screen-shot usage
        self.hwDC: Optional[int] = None
        self.DC: T_PyCDC = None
        self.cDC: T_PyCDC = None
        self.create_dc()

    def get_window_text(self):
        return win32gui.GetWindowText(self.hwnd)

    def get_wiondow_rect(self):
        return Rect(*win32gui.GetWindowRect(self.hwnd))

    def set_window_pos(self, insert_after, x, y, cx, cy, flags):
        """

        Args:
            insert_after: PyHANDLE
                Window that hWnd will be placed below. Can be a window handle or one of HWND_BOTTOM,
                HWND_NOTOPMOST, HWND_TOP, or HWND_TOPMOST
            x: int
                New X coord
            y: int
                New Y coord
            cx: int
                New width of window
            cy: int
                New height of window
            flags:
                Combination of win32con.SWP_* flags

        Returns:

        """

        win32gui.SetWindowPos(self.hwnd, insert_after, x, y, cx, cy, flags)
        self.rect = self.get_wiondow_rect()

    def screenshot(self, x=0, y=0, width=None, height=None, form="array", save_path=None):
        return screenshot(
            self.DC, self.cDC,
            x, y, width or self.rect.width, height or self.rect.height,
            form,
            save_path
        )

    def create_dc(self):
        self.hwDC = win32gui.GetWindowDC(self.hwnd)  # use ReleaseDC after calling
        self.DC = win32ui.CreateDCFromHandle(self.hwDC)  # use DeleteDC after calling
        self.cDC = self.DC.CreateCompatibleDC()  # use DeleteDC after calling

    def release_dc(self):
        self.DC.DeleteDC()
        self.cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, self.hwDC)

    # mouse action
    def abs_move(self, x_y: tuple):
        x, y = win32gui.ClientToScreen(self.hwnd, x_y)
        pag.moveTo(x, y)

    def abs_click(self, x_y: tuple, pause=None):
        x, y = win32gui.ClientToScreen(self.hwnd, x_y)
        pag.click(x, y, pause=pause)

    def abs_scroll(self, clicks, x_y=None, pause=.01, _pause=True):
        if x_y is not None:
            self.abs_click(x_y)
        unit = 1 if clicks > 0 else -1
        for _ in range(abs(clicks)):
            pag.scroll(unit, pause=pause, _pause=_pause)

    def drag_to(self, from_, to, duration, sleep_down=0, sleep_up=0):
        pag.moveTo(self.rect.left + from_[0], self.rect.top + from_[1])
        pag.mouseDown()
        if sleep_down:
            time.sleep(sleep_down)

        pag.moveTo(self.rect.left + to[0], self.rect.top + to[1], duration)

        if sleep_up:
            time.sleep(sleep_up)
        pag.mouseUp()

    def __repr__(self):
        return f"{self.get_window_text()}[{self.hwnd}]"
