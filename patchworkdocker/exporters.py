import shutil

from typing import Callable

Exporter = Callable[[str, str], None]


def export_as_directory(src: str, dest: str):
    """
    TODO
    :param src: 
    :param dest: 
    :return: 
    """
    shutil.copytree(src, dest)
