from pathlib import Path


def combine_path(p1, p2):
    s = Path(p1) / p2
    return str(s)
