import os
from abc import ABCMeta, abstractmethod
from distutils import dir_util
from tempfile import mkdtemp
from urllib.parse import urldefrag, urlparse

from git import Repo


class Importer(metaclass=ABCMeta):
    """
    Imports a Docker build directory.
    """
    @abstractmethod
    def load(self, origin: str) -> str:
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


class ImporterFactory:
    """
    Importer factory, which can create the correct importer for an origin.
    """
    def create(self, origin: str) -> Importer:
        if os.path.exists(origin):
            return FileSystemImporter()

        parsed_origin = urlparse(origin)
        if parsed_origin.scheme == "git" or parsed_origin.path.endswith(".git"):
            # XXX: it is possible that there's a Git repo at a location that does not have these attributes...
            return GitImporter()

        raise NotImplementedError(f"No importer implemented to work with: {origin}")
