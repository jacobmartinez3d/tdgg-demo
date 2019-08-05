"""Main Project interface to manage git repos and TDGam components."""
# TODO: selections need to be a class
import json
import os.path as osp
from random import choice
import string

import git

import td

from .component import TDGamComponent
from .utilities import rscandir, tdgamlog


class TDGamProject(object):
    """This class is the root access for all TDGam related functionality.

    Example Project hierarchy which would be managed by this class:

        Project-directory
            |_(project .git repo)
            |
            |_Components-directory
                |_component-repo-folder
                    |_(component .git submodule)
                |_component-repo-folder
                    |_(component .git submodule)

    Project-directory:
        This is automatically set where your .toe is saved.
        Everything you do in TDGam for this project instance is set and
        retrieved out of this directory. It's also where the project's main
        .git repo is located.

    Components-directory:
        Nested directly inside the project-folder and
        houses all the individual component submodule repo folders.

    Component-repo-folder:
        The .git repo for that component. Any external
        assets used by the component in Touch Designer are also stored here.
    """

    def __init__(self, project_name, path_to_project_folder):
        """Initialize Project with path to the folder, and a name.

        :param project_name: name of the project.
        :type  project_name: str
        :param path_to_project_folder: A path string to the project folder.
        :type  path_to_project: str
        """
        super(TDGamProject, self).__init__()

        self.preferences = {
            "project_folder": path_to_project_folder,
            "project_remote_repo_url": "https://"
        }

        self.components = []
        self.repo = None
        self.master_branch = None
        self.remote = None

        self.set_project_root(path_to_project_folder)

        self.log("Project '{}' Created!".format(project_name), "warning")
        self.log(path_to_project_folder, "path")

    @classmethod
    def get_current(cls):
        """Instantiate a TDGamProject instance for the currentlt open .toe.

        :return: a TDGamProject instance for the currently open .toe.
        :rtype:  TDGam.TDGamProject
        """
        return True

    def folder(self):
        """Retreive the current project directory-path on the filesystem.

        :return: the directory-path to the current project folder.
        :rtype:  str
        """
        return self.preferences["project_folder"]

    def components_folder(self):
        """Retreive the project's component directory-path on the filesystem.

        :return: the path to the current project folder's components directory.
        :rtype:  str
        """
        return osp.join(self.preferences["project_folder"], "TDGam_Components")

    @staticmethod
    def log(msg, type_, length=72):
        """Log a formatted message to terminal.

        :param msg: the msg to log.
        :type  msg: str
        :param type_: the type of msg (see utilities.tdgamlog for list).
        :type  type_: str
        :param length: the amount of characters in the terminal to limit to.
        :type  length: int
        """
        tdgamlog(msg, type_, length)

    def set_project_root(self, path_to_project_folder):
        """Initialize .git repo at given path and set as new project-directory.

        :param path_to_project_folder: valid path to folder.
        :type  path_to_project_folder: str
        """
        if not osp.exists(path_to_project_folder):
            self.log("Path: {}, does not exist. Aborting.".format(
                path_to_project_folder), "warning")
            return

        elif osp.isdir(path_to_project_folder):
            self.preferences["project_folder"] = path_to_project_folder

        elif osp.isfile(path_to_project_folder):
            self.preferences["project_folder"] = osp.dirname(
                path_to_project_folder)

        # attempt to retrieve git.Repo object
        try:
            self.repo = git.Repo(self.folder())
            self.log("Project set to previous repo located at:", "info")
            self.log(self.folder(), "path")

        except git.exc.InvalidGitRepositoryError:
            self.log("Project Created with no repo at:", "info")
            self.log(self.folder(), "path")
            self.repo = None

    def git_init(self):
        """Init a repo in the app's project folder.

        :return: True if repo already existed, False if newly initialized.
        :rtype:  bool
        """
        exists = False
        try:
            self.repo = git.Repo.init(self.folder())
            self.git_add_dir(self.folder())
            self.master_branch = self.repo.head.ref

            self.log("Initialized git repo @:", "info")
            self.log(self.folder(), "path")

        except git.exc.InvalidGitRepositoryError:
            self.log("Repo already initialized!", "info")
            exists = True

        return exists

    def git_initial_commit(self):
        """Perform an "initial commit"."""
        try:
            self.repo.git.add(".")
            self.repo.git.commit("-m", "Initial Commit.")

        except git.exc.GitCommandError as e:
            self.log(e, "warning")

    def git_create_branch(self, branch_name):
        """Create a new project git branch.

        :param branch_name: the name of the new branch to create.
        :type  branch_name: str
        """
        self.repo.create_head(branch_name, self.repo.head.ref)

    def git_add(self, filepath):
        """Add target file to the currently tracked files list.

        :param filepath: the path on the filesystem to the file to add.
        :type  filepath: str
        :return: the filepath of the file added
        :rtype:  str
        """
        filepath = osp.normpath(filepath)
        self.repo.index.add([filepath])

        self.log("Now tracking:", "info")
        self.log(filepath, "path")

        return filepath

    def git_add_dir(self, folder):
        """Add files recursively from target directory.

        :param folder: the path to the folder on the filesystem to add.
        :type  folder: str
        :return: a generator of results from the git api for each added file.
        :rtype:  generator
        """
        return (self.git_add(file_) for file_ in rscandir(folder, [".git"]))

    def append_component(self, selection, name=None):
        """Append a new TDGam.Component instance to the project.

        :param selection: selected td operators to add.
        :type  selection: str
        :param name: the name of the new component to add.
        :return: the newly created component
        :rtype:  TDGam.TDGamComponent
        """
        if name:
            component = TDGamComponent(selection, name)

        else:
            component = TDGamComponent(selection, self._name_hash(7))

        self.components.append(component)
        self.log("Component: {} added to project repo.".format(
            component.name), "info")
        self.log(selection, "results")

        return component

    def retrieve_component(self, name):
        """Retrieve a TDGamComponent associated with this project by name.

        :param name: Name of Component to search for.
        :type  name: str
        :return: the found component, or None
        :rtype:  TDGam.Component|None
        """
        def __from_self():
            """Search in self.components."""
            result = None

            for component in self.components:

                if component.name == name:
                    result = component
                    break

            return result

        def __from_dir():
            """Search the Component's JSON saved in Project-directory."""
            result = None

            json_filepath = osp.join(
                self.components_folder, name + ".json")
            json_filepath = osp.normpath(json_filepath)

            with open(json_filepath, "r") as json_file:

                json_data = json.loads(json_file.read())[0]
                result = TDGamComponent(data=json_data)

            return result

        return __from_self() or __from_dir()

    def save(self, save_external_toxs=False, commit_repos=False):
        """Save TDGam Project with default TD save.

        :param saveExternalToxs: (Keyword, Optional) If set to True, will save
            out the contents of any COMP that references an external .tox into
            the referenced .tox file.
        :type  saveExternalToxs: bool
        :param commit_repos: Flag to commit changes to all component repos.
        :type  commit_repos: bool
        """
        td.Project.save(self.repo.path, save_external_toxs)
        if commit_repos:
            # TODO: commit all component submodule-repos in project folder.
            pass

    def update_preferences(self, preferences):
        """Update the project prefernces with a new dictionary.

        :param preferences: dictionary of changed preferences to update.
        :type  preferences: dict
        """
        self.preferences.update(preferences)
        self.__init_project()

    @staticmethod
    def _name_hash(length):
        """Generate a random name-hash.

        :param length: the amount of characters in the desired name.
        :type  length: int
        :return: a string of randomly-generated characters.
        :rtype:  str
        """
        allchar = string.ascii_letters
        random_chars = ('').join((choice(allchar) for x in range(length)))

        return random_chars

    def __init_project(self):
        """Force a reload and set the project use latest preferences."""
        self.set_project_root(self.folder())
