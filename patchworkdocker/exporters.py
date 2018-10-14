import shutil
from abc import ABCMeta, abstractmethod


class Exporter(metaclass=ABCMeta):
    """
    TODO
    """
    @abstractmethod
    def export(self, src: str, dest: str):
        """
        TODO
        :param src:
        :param dest:
        :return:
        """


class DirectoryExporter(Exporter):
    """
    TODO
    """
    def export(self, src: str, dest: str):
        shutil.copytree(src, dest)
