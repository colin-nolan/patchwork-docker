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
    def _load(self, origin: str, load_directory: str) -> str:
        """
        Loads the build directory from the given origin into the given directory.
        :param origin: where to import materials from
        :param load_directory: the directory in which imported materials should be saved
        :return: directory containing the loaded content
        """

    def load(self, origin: str, load_directory: str=None) -> str:
        """
        Loads build directory from the given origin into a load directory, which can be specified or is a generated
        temp directory if `None`.

        The returned directory is not cleaned up automatically.
        :param origin: where to import materials from
        :param load_directory: the directory in which imported materials should be saved
        :return: directory containing the loaded content
        """
        if load_directory is None:
            load_directory = mkdtemp()
        return self._load(origin, load_directory)


class GitImporter(Importer):
    """
    Imports content from a git repository.
    
    For a specific commit, branch or tag, set the fragment, e.g. http://example.com/repo.git#branch_tag_or_commit.
    """
    def _load(self, origin: str, load_directory: str) -> str:
        origin, branch = urldefrag(origin)
        repository = Repo.clone_from(url=origin, to_path=load_directory)

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

        return load_directory


class FileSystemImporter(Importer):
    """
    Imports content from the local file system.
    """
    def _load(self, origin: str, load_directory: str) -> str:
        dir_util.copy_tree(origin, load_directory)
        return load_directory


class ImporterFactory:
    """
    Importer factory, which can create the correct importer for an origin.
    """
    def create(self, origin: str) -> Importer:
        """
        Create an importer determined by analysis of the given origin.
        :param origin: where to import materials from
        :return: importer for the given origin
        """
        if os.path.exists(origin):
            return FileSystemImporter()

        parsed_origin = urlparse(origin)
        if parsed_origin.scheme == "git" or parsed_origin.path.endswith(".git"):
            # XXX: it is possible that there's a Git repo at a location that does not have these attributes...
            return GitImporter()

        raise NotImplementedError(f"No importer implemented to work with: {origin}")
