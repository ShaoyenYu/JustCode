import ctypes
from ctypes import windll
from typing import List, Tuple, Dict

import win32api
import win32con
import win32gui
import win32ui

from util.win32.types.datatypes import Rect

__ProcessDpiAwareness = 0
__HAS_INITIALIZED = False


class Monitor:
    def __init__(self, **kwargs):
        self.handle = kwargs.get("handle")
        self.index = kwargs.get("index")
        self.name = kwargs.get("name")
        self.rect = kwargs.get("rect")
        self.width, self.height = (kwargs.get(k) for k in ("width", "height"))
        self.scale_factor = kwargs.get("scale_factor")
        self.is_primary = kwargs.get("is_primary")

    def __repr__(self):
        s_info = f"Monitor-{self.index}[Hnd:{self.handle}, Res:{self.width, self.height}, Rect:{self.rect}, Scale:{self.scale_factor}]"
        s_is_main = "*" if self.is_primary else ""
        return f"{s_is_main}{s_info}"


def get_monitor_scale_factor(monitor_handle: int) -> float:
    res = ctypes.c_int()
    windll.shcore.GetScaleFactorForMonitor(monitor_handle, ctypes.byref(res))
    return res.value


def get_monitor_resolution(monitor_name: str):
    device_context = win32gui.CreateDC("DISPLAY", monitor_name, None)
    width, height = (win32ui.GetDeviceCaps(device_context, w32con) for w32con in (win32con.HORZRES, win32con.VERTRES))
    win32gui.DeleteDC(device_context)
    return width, height


def get_monitor_by_handle(monitor_handle, monitor_index=None) -> Monitor:
    monitor_info = win32api.GetMonitorInfo(monitor_handle)  # type: Dict
    monitor_scale_factor = get_monitor_scale_factor(monitor_handle)
    monitor_resolution = get_monitor_resolution(monitor_info["Device"])

    mon = Monitor(**{
        "handle": monitor_handle,
        "name": monitor_info["Device"],
        "index": monitor_index,
        "rect": Rect(*monitor_info["Monitor"]),
        "width": monitor_resolution[0],
        "height": monitor_resolution[1],
        "scale_factor": monitor_scale_factor,
        "is_primary": monitor_info["Monitor"][0] == monitor_info["Monitor"][1] == 0,  # left == height == 0
    })
    return mon


def get_monitors():
    monitors = win32api.EnumDisplayMonitors()  # type: List[Tuple]
    return [get_monitor_by_handle(mon_tuple[0].handle, mon_index) for mon_index, mon_tuple in enumerate(monitors)]


def set_process_dpi_awareness(process_dpi_awareness: int, silent=False):
    from warnings import warn
    global __HAS_INITIALIZED, __ProcessDpiAwareness

    if __HAS_INITIALIZED:
        if silent:
            return
        raise RuntimeError(f"ProcessDpiAwareness can only be set once, current value: {__ProcessDpiAwareness}")
    __HAS_INITIALIZED = True
    __ProcessDpiAwareness = process_dpi_awareness
    msg = (
        "Once API awareness is set for an app, any future calls to this API will fail."
        "This is true regardless of whether you set the DPI awareness in the manifest or by using this API"
        "For more information, check https://docs.microsoft.com/en-us/windows/win32/api/shellscalingapi"
        "/nf-shellscalingapi-setprocessdpiawareness\n"
        "This setting will impact on process level, instead of module level"
        f"CURRENT `ProcessDpiAwareness`: {__ProcessDpiAwareness}"
    )
    warn(msg)
    windll.shcore.SetProcessDpiAwareness(__ProcessDpiAwareness)  # this will change api to raw api
