import os
import shutil
from distutils import dir_util

import re
from typing import Iterable, List, Tuple, Pattern, Set, Dict

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


def replace_in_string(pattern_replacements: Iterable[Tuple[str, str]], string: str) -> str:
    """
    TODO
    :param patterns: 
    :param string: 
    :return: 
    """
    global _compiled_patterns

    for pattern, replacement in pattern_replacements:
        if pattern not in _compiled_patterns:
            _compiled_patterns[pattern] = re.compile(pattern)

        string =_compiled_patterns[pattern].sub(replacement, string)

    return string

    # non_empty_pattern = False
    # for pattern in patterns:
    #     if pattern != "":
    #         non_empty_pattern = True
    #         break
    # if not non_empty_pattern:
    #     return string

    all_patterns = "|".join([f"({pattern})" for pattern in patterns])

    return re.sub(all_patterns, "", string)


# def remove_in_file(patterns: Iterable[str], dockerfile_location: str):
#     """
#     TODO
#     :param patterns:
#     :param dockerfile_location:
#     """
#     with open(dockerfile_location, "rw") as file:
#         content = remove_in_string(patterns, file.read())
#         file.write(content)


# def add_lines_after()

