from abc import ABCMeta, abstractmethod
from distutils import dir_util
from pathlib import Path
from tempfile import mkdtemp
from urllib.parse import urldefrag

from git import Repo


class Importer(metaclass=ABCMeta):
    """
    Imports a Docker build directory.
    """
    @abstractmethod
    def load(self, origin: str) -> Path:
        """
        Loads build directory from the given origin into a temporary directory. 
        
        The returned directory is not cleaned up automatically.
        :return: directory containing the loaded content
        """


class GitImporter(Importer):
    """
    Imports content from a git repository.
    
    For a specific commit, branch or tag, set the fragment, e.g. http://example.com/repo.git#branch_tag_or_commit.
    """
    def load(self, origin: str) -> str:
        origin, branch = urldefrag(origin)
        temp_directory = mkdtemp()
        repository = Repo.clone_from(url=origin, to_path=temp_directory)

        if branch != "":
            if branch not in repository.heads:
                branch_reference = None
                for reference in repository.refs:
                    if reference.name == f"origin/{branch}":
                        branch_reference = reference
                        break
                if branch_reference is not None:
                    commit = branch_reference.commit
                else:
                    commit = repository.commit(branch)
                repository.create_head(path=branch, commit=commit)
            repository.heads[branch].checkout()

        return temp_directory


class FileSystemImporter(Importer):
    """
    Imports content from somewhere on the local file system.
    """
    def load(self, origin: str) -> str:
        temp_directory = mkdtemp()
        dir_util.copy_tree(origin, temp_directory)
        return temp_directory
