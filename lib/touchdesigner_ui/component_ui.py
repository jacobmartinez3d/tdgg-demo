"""Touch Designer UI Wrapper for TDGam Components."""
import json
import logging
from os import path as osp

import git
import td

from ..maglapath import Path
from ..plugins import TouchDesigner


class TDGamComponentUI(object):
    """Provide interface between TDGamComponent and UI components."""

    def __init__(self, c, parent_op):
        """Initialize with TDGam.TDGamComponent instance.

        :param c: the component model this UI is controlling.
        :type  c: tdgam.TDGamComponent
        :param parent_op: the parent op this instance will be created in.
        :type  parent_op: td.Op
        """
        self.c = c
        self.parent_op = parent_op
        # the containerCOMP parent of the original selection.
        self.placeholder = None
        # td.tableDAT's used by the UI
        self.controllers = {}
        self.td_utils = TouchDesigner()
        self.__setup()

    def __repr__(self):
        return "<TDGamConponent: {name}, {repo_dir}>".format(
            name=self.c.name,
            repo_dir=self.c.folder())

    def refresh(self):
        """Edit controllers any td.tableDAT's being used by the UI."""
        execute_list = [
            # git_log
            {
                "table": self.controllers["git_log"],
                "rows": self.retrieve_git_log()
            },
            # tracked_files
            {
                "table": self.controllers["tracked_files"],
                "rows": self.retrieve_tracked_files(),
                "is_path": True
            },
            # untracked_files
            {
                "table": self.controllers["untracked_files"],
                "rows": self.retrieve_untracked_files(),
                "is_path": True
            },
            # modified_files
            {
                "table": self.controllers["modified_files"],
                "rows": [t[1] for t in self.retrieve_modified_files()],
                "is_path": True
            },
            # ops
            {
                "table": self.controllers["ops"],
                "rows": [o["name"] for o in self.c.selection]
            },
            # git_branches
            {
                "table": self.controllers["git_branches"],
                "rows": [h.name for h in self.c.repo.heads]
            },
            # remotes
            {
                "table": self.controllers["remotes"],
                "rows": [h.name for h in self.c.repo.heads]
            }
        ]

        return [self._setTable(**args_) for args_ in execute_list]

    # -- TDGam methods -- #

    def rebuild(self, target_op=None, custom_json_path=None):
        """Rebuild original selection from Component's json data.

        :param target_op: Target op to create inside.
        :type  target_op: td.OP
        :param custom_json_path: Valid path to a ParSet json.
        :type  custom_json_path: str
        :return: list of recreated td.OP instances.
        :rtype:  list
        """
        json_path = self.c.json_file_path

        if not target_op:
            target_op = self.c.parent_op

        if custom_json_path:
            json_path = custom_json_path

        try:
            with open(json_path) as jf:
                # selection = []
                # for string_dict in :
                #     selection.append(ast.literal_eval(string_dict))
                self.c.selection = json.loads(jf.read())

        # TODO: needs more specific exception types here
        except Exception as e:
            with open(json_path) as jf:
                print(jf.read())
            return False

        rebuilt = self.td_utils.recreate(
            target_op,
            self.c.selection,
            recurse=True)

        for i, recreated_op in enumerate(rebuilt):

            op_data = self.c.selection[i]
            self._set_pars_from_data_recursive(recreated_op, op_data)

        return rebuilt

    def stash(self):
        """Save all contained ops' pars, then destroy all ops."""
        for op_data in self.c.selection:

            self._destroy_op(op_data)

    def dock(self):
        """Dock ops to the placeholder."""
        for op_data in self.c.selection:
            self._dock_op(op_data)
        # x, y = self.calculate_placeholder_position()
        # self.select_placeholder.nodeCenterX = x
        # self.select_placeholder.nodeCenterY = y + 50

    def export_json(self):
        """TODO: Export selection-data as json."""
        print("export_json")

    def export_table_dat(self):
        """TODO: Export Table-dat containing selection-data."""
        print("export_table_dat")

    def import_from_json(self, json_file_path):
        """TODO: Create component from a json.

        :param json_file_path: the path to the json file.
        :type  json_file_path: str
        """
        print("import_from_json")

    def import_from_table_dat(self, table_dat_path):
        """TODO: Create component from a tableDAT.

        :param table_dat_path: the td pat to the tableDAT.
        :type  table_dat_path: str
        """
        print("import_from_table_dat")

    def import_from_remote_repo(self, remote_repo_url):
        """TODO: Create component from a remote repo.

        :param remote_repo_url: the remote repo url to pull from.
        :type  remote_repo_url: str
        """
        print("import_from_remote_repo")

    def expand(self):
        """Rebuild the original selection, then delete the placeholder object."""
        print("expand")

    # -- GIT methods -- #

    def git_commit(self):
        """TODO: Commit current staging area."""
        print("commit")

    def git_reset(self):
        """TODO: Reset the current staging area."""
        print("reset")

    def git_push(self, remote_branch=None):
        """Push current staging area to remote repo.

        :param remote_branch: remote branch to push to.
        :type  remote_branch: git Branch
        :return: push info object.
        :rtype:  git push info object
        """
        remote = self.c.repo.remotes[0]
        remote_branch = "master"  # temporary
        push_info = remote.push(
            refspec='{}:{}'.format(
                self.c.repo.active_branch.name, remote_branch))

        self.refresh()
        return push_info

    def git_pull(self):
        """TODO: Pull changes from remote repo to current branch."""
        print("pull")

    def git_checkout_branch(self):
        """TODO: Checkout target branch.

        :param branch_name: name of the branch to checkout.
        :type  branch_name: str
        """
        print("change_branch")

    def git_new_branch(self):
        """TODO: Create new branch from current staging area."""
        print("git_new_branch")

    def set_component_remote(self, remote_name, remote_url):
        """Open a confirm dialogue to add a new git repo URL to this component.

        :param remote_name: the name of the remote repo.
        :type  remote_name: str
        :param remote_url: the url to the remote repo.
        :type  remote_url: str
        :return: tuple which is passed to confirmation dialog.
        :rtype:  tuple
        """
        title = "Confirm Remote Repo URL:"
        message = """Enter a name and URL for remote Git repo below, then press
            "Add Remote".""".strip()

        ui_components = {
            "ok": {
                "label": "Add Remote",
                "callback": self.git_add_remote,
                "args": (remote_name, remote_url)},
            "message": {"label": None, "val": message},
            "stringfield_url": {"label": "URL", "val": "https://"},
            "stringfield_name": {"label": "Name", "val": "Origin"},
            "list": [
                {"label": remote.name, "cancel": None}
                for remote in self.c.repo.remotes
            ]
        }
        return title, ui_components

    def retrieve_git_log(self):
        """retrieve the git log for current branch."""
        return self.c.retrieve_git_log()

    def retrieve_tracked_files(self):
        """retrieve s list of currently tracked files in the repo."""
        return self.c.retrieve_tracked_files()

    def retrieve_untracked_files(self):
        """retrieve s list of currently un-tracked files in the repo."""
        return self.c.retrieve_untracked_files()

    def retrieve_modified_files(self):
        """retrieve s list of currently modified files in the repo."""
        return self.c.retrieve_modified_files()

    def git_add_remote(self, remote_name, remote_url):
        """Add a remote origin to for the current component repo.

        :param remote_name: the name to give the the remote repo.
        :type  remote_name: str
        :param remote_url: the url of the remote repo to add.
        :type  remote_url: str
        :return: the path to the remote url just added.
        :rtype:  str
        """
        print("repo at: {}".format(remote_url))
        try:
            remote_url = self.c.repo.create_remote(remote_name, url=remote_url)

        except git.exc.GitCommandError as e:
            if e.status == 128:
                print("using existing repo at: {0}".format(remote_url))

        self.refresh()

        return remote_url

    def _dock_op(self, op_data):
        """Dock an op to it's placeholder.

        :param op_data: the op data dict for the op to dock.
        :type  op_data: ParDict
        """
        op_ = td.op(op_data["path"])
        op_.dock = self.select_placeholder

    def create_stash_dat(self, target_op):
        """Create a stash tableDAT containging selection data for component.

        :param target_op: the target op to create the tableDAT inside.
        :type  target_op: td.Op
        :return: the stash tableDAT just created.
        :rtype: td.tableDAT
        """
        titles = list(self.c.selection[0].keys())
        stash_dat = target_op.create(
            td.tableDAT, "stash_{}".format(self.c.name))

        stash_dat.deleteRow(0)
        stash_dat.appendRow(titles)

        for data_dict in self.c.selection:
            stash_dat.appendRow(list(data_dict.values()))

        return stash_dat

    def calculate_placeholder_position(self):
        """Calculate a position for the placeholder by averaging selected ops.

        :return: x, y positions
        :rtype:  tuple
        """
        x_sum = 0
        y_sum = 0
        leftmost = 0
        topmost = 0

        for op_data in self.c.selection:

            op_ = td.op(op_data["path"])
            x_sum += op_.nodeCenterX
            y_sum += op_.nodeCenterY

            leftmost = leftmost if leftmost > op_.nodeX else op_.nodeX
            topmost = topmost if topmost > op_.nodeY else op_.nodeY

        mean_x = x_sum / len(self.c.selection)
        mean_y = y_sum / len(self.c.selection)

        return int(mean_x), int(mean_y)

    def __setup(self):
        """Creates all necessary td-related ops."""

        self.placeholder = td.op(str(Path("<user_components>"))).create(
            td.containerCOMP, self.c.name)
        self.placeholder.par.clone = str(Path("<placeholder_template>"))
        self.placeholder.par.align = "verttb"

        # create a td.tableDAT from selection inside placeholder
        self.stash_dat = \
            self.create_stash_dat(td.op(str(Path("<user_components>"))))
        self.stash_dat.outputConnectors[
            0].connect(self.placeholder.inputConnectors[0])

        # set dat comment
        self.stash_dat.comment = 'Created on {0}'.format(self.c.timestamp)

        # create a selectCOMP where the user made the selection
        self.select_placeholder = self.parent_op.create(
            td.selectCOMP, self.c.name)
        self.select_placeholder.par.selectpanel = \
            str(Path("<user_components>")) \
            + "/" \
            + self.c.name
        self.select_placeholder.par.selectpanel.readOnly = True
        self.select_placeholder.viewer = 1

        # set the select_placeholder position
        x, y = self.calculate_placeholder_position()
        self.select_placeholder.nodeCenterX = x
        self.select_placeholder.nodeCenterY = y

        # destroy originally selected ops
        for data_pack in self.c.selection:
            self._destroy_op(data_pack["path"])

        # assign all controller tableDAT's
        self.controllers = {
            "tracked_files": self.placeholder.findChildren(
                name="tbl_tracked_files")[0],
            "untracked_files": self.placeholder.findChildren(
                name="tbl_untracked_files")[0],
            "modified_files": self.placeholder.findChildren(
                name="tbl_modified_files")[0],
            "ops": self.placeholder.findChildren(
                name="tbl_ops")[0],
            "git_log": self.placeholder.findChildren(
                name="tbl_git_log")[0],
            "git_branches": self.placeholder.findChildren(
                name="tbl_git_branches")[0],
            "remotes": self.placeholder.findChildren(
                name="tbl_remotes")[0]
        }

    @staticmethod
    def decorate_button(target_op, **kwargs):
        """Change the properties of a button.

        :param target_op: the button to decorate.
        :type  target_op: td.Op
        """
        if "label" in kwargs:
            bg_top = target_op.findChildren(name="bg")[0]
            bg_top.par.text = kwargs["label"]

    @staticmethod
    def _destroy_op(op_tdpath):
        """Destroy a single op.

        :param op_tdpath: path to the op to destroy.
        :type  op_tdpath: str
        """
        try:
            td.op(op_tdpath).destroy()

        except AttributeError:
            logging.exception(
                "{} was missing, skipping delete!".format(op_tdpath))

    @staticmethod
    def _set_pars_from_data(op_path, op_data):
        """Set target op's parameters from json data.

        :param op_path: TD path to the target op.
        :type: str
        :param op_data: Op data from json.
        :type: dict
        :returns: recreation of the original td.OP from current json.
        """
        if isinstance(op_path, td.OP):
            op_ = op_path
        else:
            op_ = td.op(op_path)

        for par in op_.pars():
            # set pars
            if par.name in op_data["pars"]:
                par.val = op_data["pars"][par.name]

        # set nodeCenter
        op_.nodeCenterX = op_data["nodeCenter"][0]
        op_.nodeCenterY = op_data["nodeCenter"][1]

        # set connections
        for i, output_dict in enumerate(op_data["outputs"]):

            op_.outputConnectors[i].connect(td.op(output_dict["path"]))

        for i, input_dict in enumerate(op_data["inputs"]):

            op_.inputConnectors[i].connect(td.op(input_dict["path"]))

        return op_

    def _set_pars_from_data_recursive(self, op_path, op_data):
        """Set the parameters of a newly created op from its ParDict.

        :param op_path: path to the op whose pars to set.
        :type  op_path: str
        :param op_data: the ParDict to use.
        :type  op_data: ParDict
        :return: the op that was set.
        :rtype:  td.Op
        """
        op_ = None
        if "children" in op_data:
            for child_data in op_data["children"]:

                self._set_pars_from_data_recursive(
                    child_data["path"], child_data)
        else:
            op_ = self._set_pars_from_data(op_path, op_data)

        return op_

    @staticmethod
    def _setTable(**args):
        """Set a tab;eDAT's rows and columns.

        :return: the table that was set.
        :rtype:  td.tableDAT
        """
        table = args.get("table", None)
        rows = args.get("rows", None)
        is_path = args.get("is_path", None)

        table.setSize(0, 1)

        if is_path:
            for path in rows:
                table.appendRow([osp.basename(path), path])
        else:
            for item in rows:
                table.appendRow(item)

        return (table.name, True)
