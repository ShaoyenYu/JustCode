from hashlib import md5
from pickle import dumps

from techstacks.auto_game.util.logging import *


def gen_key(*args, **kwargs):
    return md5(dumps((args, kwargs))).hexdigest()
