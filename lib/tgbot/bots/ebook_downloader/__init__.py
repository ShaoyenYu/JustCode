from pathlib import Path

from telegram import Update
from telegram.ext import CallbackContext

from util.io import load_yaml

CONFIG = load_yaml(Path(".").absolute().parent.parent / "config.yaml")


class Command:
    __slots__ = ("value", "cmd")

    def __init__(self, value: int, cmd: str):
        self.value = value
        self.cmd = cmd

    def __lt__(self, other):
        return self.value < other

    def __le__(self, other):
        return self.value <= other

    def __gt__(self, other):
        return self.value > other

    def __ge__(self, other):
        return self.value >= other

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.value == other) or (self.cmd == other.cmd)
        return self.value == other

    def __repr__(self):
        return f"Command({self.value}, {self.cmd})"


class Task:
    __slots__ = ("f", "message", "args", "kwargs", "callback", "cb_args", "cb_kwargs")

    def __init__(self, f, message, *args, **kwargs):
        self.f = f
        self.message = message
        self.args = args
        self.kwargs = kwargs
        self.callback = kwargs.pop("callback") if "callback" in self.kwargs else None
        self.cb_args = kwargs.pop("cb_args") if "cb_args" in self.kwargs else tuple()
        self.cb_kwargs = kwargs.pop("cb_kwargs") if "cb_kwargs" in self.kwargs else dict()

    def __call__(self, *args, **kwargs):
        if self.callback is not None:
            if hasattr(self.message, "data"):
                self.message.data["result"] = self.f(*self.args, **self.kwargs)
            else:
                self.message["data"] = {"result": self.f(*self.args, **self.kwargs)}
            return Task(self.callback, self.message, *self.cb_args, **self.cb_kwargs)
        return self.f(*self.args, **self.kwargs)


class CallbackUpdate:
    __slots__ = ("update", "context", "inline", "data")

    def __init__(self, update: Update, context: CallbackContext, **kwargs):
        self.update = update
        self.context = context
        self.inline = kwargs.get("inline", False)
        self.data = kwargs.get("data", dict())

    @property
    def cmd(self):
        return self.data["cmd"]

    def __lt__(self, other):
        return self.cmd < other

    def __le__(self, other):
        return self.cmd <= other

    def __gt__(self, other):
        return self.cmd > other

    def __ge__(self, other):
        return self.cmd >= other

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.cmd == other) or (self.cmd == other.cmd)
        return self.cmd == other
