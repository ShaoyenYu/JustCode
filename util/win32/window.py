import time

import pyautogui as pag
import win32con
import win32gui
import win32ui
from PIL import Image

from util.win32.types.datatypes import Rect


def _create_data_bitmap(x, y, width_to_cap, height_to_cap, DC, cDC=None):
    if cDC is None:
        cDC = DC.CreateCompatibleDC()

    data_bitmap = win32ui.CreateBitmap()  # create monochrome bitmaps
    data_bitmap.CreateCompatibleBitmap(DC, width_to_cap, height_to_cap)  # create color bitmaps

    # The SelectObject function selects an object into the specified device context (DC).
    # The new object replaces the previous object of the same type.
    cDC.SelectObject(data_bitmap)
    cDC.BitBlt((0, 0), (width_to_cap, height_to_cap), DC, (x, y), win32con.SRCCOPY)

    return data_bitmap


def take_screenshot(src_dc, dst_dc, width, height, x=0, y=0, save_path=None, release=True) -> Image:
    """

    Args:
        src_dc:
        dst_dc:
        width: int
            width to capture
        height: int
            height to capture
        x:
            left-top x coordinate of source
        y:
            left-top y coordinate of source
        save_path: str
        release: bool, default True
            whether to release `src_dc`, `dst_dc`

    Returns:

    """

    data_bitmap = _create_data_bitmap(x, y, width, height, src_dc, dst_dc)
    bmpinfo = data_bitmap.GetInfo()

    image = Image.frombuffer(
        "RGB", (bmpinfo['bmWidth'], bmpinfo['bmHeight']), data_bitmap.GetBitmapBits(True),
        'raw', *('BGRX', 0, 1)
    )

    if save_path:
        data_bitmap.SaveBitmapFile(dst_dc, save_path)

    if release:
        src_dc.DeleteDC()
        dst_dc.DeleteDC()
    win32gui.DeleteObject(data_bitmap.GetHandle())
    return image


def take_screenshot_by_hwnd(hwnd, width_to_cap, height_to_cap, x=0, y=0, save_path=None) -> Image:
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
        width_to_cap:
        height_to_cap:
        x:
        y:
        dc_src:
        dc_dest:
        save_path:

    Returns:

    """

    wDC = win32gui.GetWindowDC(hwnd)
    DC = win32ui.CreateDCFromHandle(wDC)
    cDC = DC.CreateCompatibleDC()

    img = take_screenshot(DC, cDC, width_to_cap, height_to_cap, x, y, save_path, release=True)

    win32gui.ReleaseDC(hwnd, wDC)
    return img


class Window:
    def __init__(self, window_name=None, window_pos=None):
        if window_name:
            self.hwnd = win32gui.FindWindow(0, window_name)
        if window_pos:
            self.hwnd = win32gui.WindowFromPoint(window_pos)
        self.rect = self.get_wiondow_rect()

        # for screen-shot usage
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

    def screenshot(self, width=None, height=None, x=None, y=None, save_path=None, shift_x=0, shift_y=0):
        return take_screenshot(
            self.DC, self.cDC, width or self.rect.width, height or self.rect.height, (x or 0) + shift_x, (y or 0) + shift_y,
            save_path, release=False
        )

    def create_dc(self):
        self.wDC = win32gui.GetWindowDC(self.hwnd)
        self.DC = win32ui.CreateDCFromHandle(self.wDC)
        self.cDC = self.DC.CreateCompatibleDC()

    def release_dc(self):
        self.DC.DeleteDC()
        self.cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, self.wDC)

    # mouse action
    def drag_to(self, from_, to, duration, sleep_down=0, sleep_up=0):
        pag.moveTo(self.rect.left + from_[0], self.rect.top + from_[1])
        pag.mouseDown()
        if sleep_down:
            time.sleep(sleep_down)

        pag.moveTo(self.rect.left + to[0], self.rect.top + to[1], duration)

        if sleep_up:
            time.sleep(sleep_up)
        pag.mouseUp()
        # pag.dragTo(self.rect.left + to[0], self.rect.top + to[1], duration, mouseDownUp=True)

    def __repr__(self):
        return f"{self.get_window_text()}[{self.hwnd}]"
