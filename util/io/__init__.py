from yaml import load, CLoader

from util.io.ql.mysql import to_sql


def load_yaml(file):
    with open(file, encoding="utf-8") as f:
        return load(f, CLoader)
