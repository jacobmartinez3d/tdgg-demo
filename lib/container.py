"""TDGam Container, pseudo-wrapper-Class for td.Container."""
from datetime import datetime
import json
import os

import git
import td

from . import utilities


class TDGamContainer(object):
    """Class to manage local folder tree and Git repo."""
    # TODO: can we inherit from td container class here?
    __logger = utilities.logger

    def __init__(self, name):
        """Init with Name and Parameter dictionary."""
        super(TDGamContainer, self).__init__()

        self.name = name
        self.repo = None
        self.placeholder = None
        # TODO make these objects
        self.dat_stash = None
        self.json_stash = ""

        self.__timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    @classmethod
    def from_timehash(cls):
        """Instantiate a TDGam Component with time stamp: '%Y%m%d%H%M%S'.

        :param project: the td project instance passed fro Touch Designer
        :type project: object
        :return: TDGamContainer instance
        :rtype: TDGam.TDGamContainer
        """
        return cls(datetime.now().strftime('%Y%m%d%H%M%S'))

    @classmethod
    def from_tox(cls, parent_op, tox_filepath, tox_name=""):
        """Instantiate TDGam Component from an imported tox.

        :param parent_op: the parent Touch Designer op to create inside
        :type parent_op: td.Op
        :param tox_filepath: path on the current file system to the tox to load
        :type tox_filepath: str
        :param tox_name: the name to give this TDGamContainer
        :type tox_name: str
        :return: TDGamContainer set to the tox and named after the tox
        :rtype: TDGam.TDGamContainer
        """
        tox = parent_op.loadTox(tox_filepath)

        # set color
        tox.color = (0, 0, 0)
        tox.name = tox_name if tox_name else datetime.now() \
                                                     .strftime('%Y%m%d%H%M%S')

        # activate the op's viewer to active to enable interactivity.
        tox.viewer = 1
        tox.activeViewer = 1

        # instantiate a TDGamContainer using the tox properties
        tdgam_container = cls(tox.name)
        tdgam_container.placeholder = tox

        return tdgam_container

    def create_json_stash(self, path, node_params):
        """Write json with jsonified selection data.

        :param path: Path to the json's save location.
        :type path: str, unicode
        :return: the path to the created json stash
        :rtype: str
        """
        json_file_path = os.path.join(path, self.name + '.json')

        if not os.path.isdir(path):
            os.makedirs(path)

        if os.path.isfile(json_file_path):
            return json_file_path

        with open(json_file_path, 'w+') as json_file:

            json_file.write(json.dumps(node_params, indent=4))

        self.json_stash = json_file_path

        return json_file_path

    def init_repo(self, repo_dir, create_dirs=False):
        """Initialize a Git repo at the target path.

        :param create_dirs: Flag to recursively create dirs.
        :type creat_dirs: bool
        :return: repo instance for this container's folder on the filesystem
        :rtype: git.Repo
        """
        if create_dirs:
            # recursive create non-existent dirs
            if not os.path.isdir(repo_dir):
                os.makedirs(repo_dir)

        self.repo = git.Repo.init(repo_dir)

        return self.repo

    def retrieve_git_log(self):
        """Retreive a list of log entries as strings.

        :return: list of logs from current repo head
        :rtype: list
        """
        result = [str(entry).split("\t")[1]
                  for entry in self.repo.head.log()]

        return result

    def retrieve_tracked_files(self):
        """Return list of tracked files in the Component's dir.

        :return: list of filenames
        :rtype: list
        """
        result = []

        for key in self.repo.index.entries.keys():

            result.append(os.path.join(self.repo.working_dir, key[0]))

        return result

    def retrieve_modified_files(self):
        """Retreive tuple of every tracked file's a_path and b_path.

        :return: list of tuples in (src, dst) format
        :rtype: list
        """
        result = [(diff_obj.a_path, diff_obj.b_path)
                  for diff_obj in self.repo.index.diff(None)]

        return result

    def retrieve_untracked_files(self):
        """Retreive a list of untracked files in the Component's dir.

        :return: lsit of filenames
        :rtype: list
        """
        untracked_files = set(self.retrieve_all_files()) \
            - set(self.retrieve_tracked_files())

        return untracked_files

    def retrieve_all_files(self):
        """Retreive a list of all files on the filesystem in the repo folder.

        :return: list of filenames
        :rtype: list
        """
        result = utilities.rscandir(
            self.folder(), ignore_dirs=[".git"])

        return result

    def git_add(self, filepath):
        """Add target file to the currently tracked files list.

        :param filepath: the path to the fils to track
        :type filepath: string
        :return: the filepath of the file added
        :rtype: str
        """
        filepath = os.path.normpath(filepath)
        self.repo.index.add([filepath])

        return filepath

    def folder(self):
        """Retreieve path to the current repo's directory on the filesystem.

        :return: the path to the repo directory
        :rtype: str
        """
        return os.path.join(
            td.project.folder.replace("/", os.sep),  # incase we're on windows
            "component_repos",
            self.name)

    def timestamp(self):
        """Retreieve timestamp for this container.

        :return: the time created
        :rtype: str
        """
        return self.__timestamp
