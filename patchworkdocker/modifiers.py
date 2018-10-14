import itertools
import os
import shutil
from distutils import dir_util

import re
from tempfile import TemporaryDirectory
from typing import Iterable, Dict

from patch import fromfile, PatchSet

_compiled_patterns: Dict[str, type(re.compile(""))] = {}


def copy_additional_files(files: Iterable[str], destination: str):
    """
    TODO
    
    Will copy directories.
    
    If files with the same name are given, the last in the list will overwrite all of the others.
    :param files: the files (and directories) to copy
    :param destination: 
    :return: 
    """
    for file in files:
        if os.path.isfile(file):
            shutil.copy(file, destination)
        else:
            dir_util.copy_tree(file, destination)


def apply_patch(patch_file: str, target_file: str):
    """
    TOOD

    diff -uNr src_1 src_2

    :param patch_file:
    :param target_file:
    :return:
    """
    patch_set = fromfile(patch_file)
    if not patch_set:
        raise SyntaxError("Could not parse contents of patch file")

    hunks = list(itertools.chain(*[item.hunks for item in patch_set.items]))

    with TemporaryDirectory() as temp_directory:
        temp_file = os.path.join(temp_directory, os.path.basename(target_file))
        patch_set.write_hunks(target_file, os.path.join(temp_file), hunks)
        os.rename(temp_file, target_file)
