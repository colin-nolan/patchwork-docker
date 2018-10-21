import fileinput
import itertools
import os
import shutil
from distutils import dir_util
from tempfile import TemporaryDirectory

from patch import fromfile


def copy_file(file: str, destination: str):
    """
    Copy the given file (which could be a directory) to the given destination.
    :param file: the file (which could be a directory) to copy
    :param destination: where to copy the file to
    """
    if not os.path.exists(file):
        raise FileExistsError(f"Cannot copy file {file} as it does not exist")
    if os.path.isfile(file):
        shutil.copy(file, destination)
    else:
        dir_util.copy_tree(file, destination)


def apply_patch(patch_file: str, target_file: str):
    """
    Applies the given patch file (plain, git, mercurial or svn styles accepted) to the given target file.

    To create a compatible patch between two files, you could use:
    ```
    diff -uNr src_1 src_2
    ```
    :param patch_file: the patch to apply
    :param target_file: the patch target
    """
    patch_set = fromfile(patch_file)
    if not patch_set:
        raise SyntaxError("Could not parse contents of patch file")

    hunks = list(itertools.chain(*[item.hunks for item in patch_set.items]))

    with TemporaryDirectory() as temp_directory:
        temp_file = os.path.join(temp_directory, os.path.basename(target_file))
        patch_set.write_hunks(target_file, os.path.join(temp_file), hunks)
        os.rename(temp_file, target_file)


def change_base_image(dockerfile_location: str, desired_base: str):
    """
    TODO
    :param dockerfile_location:
    :param desired_base:
    :return:
    """
    changed = False
    for line in fileinput.input(dockerfile_location, inplace=True):
        if line.upper().startswith("FROM"):
            assert not changed
            print(f"FROM {desired_base}")
            changed = True
        else:
            print(line, end="")

    if not changed:
        raise ValueError(f"Dockerfile did not contain FROM line: {dockerfile_location}")
