"""Main TDGam UI window."""
import re
import logging
from pprint import pformat
from os import path as osp

import td

from .component_ui import TDGamComponentUI

ML_LOG_PATH = "e:\\logs\\TDGam"
if not osp.exists(ML_LOG_PATH):
    from os import makedirs
    makedirs(ML_LOG_PATH)

logging.getLogger(__name__)
logging.basicConfig(filename=osp.join(ML_LOG_PATH, __name__),
                    level=logging.DEBUG)


def td_path_join(*argv):
    """Construct TD path from args."""
    assert len(argv) >= 2, "Requires at least 2 tdpath arguments"

    return "/".join([str(arg_) for arg_ in argv])


def filter_only(keep_list, filter_list):
    """Filter out items in an iterable not in the keep_list.

    :param keep_list: list of key names to keep.
    :type: list of str
    :param filter_list: iterable to filter.
    :type: list or dict
    """
    return list(
        filter(
            lambda key: key in keep_list, filter_list
        )
    )


class TDGamProjectUI(object):
    """Provide interface between TDGamProject and Touch Designer."""

    def __init__(self, TDGamProject):
        """Ititialize default UI instance with project repo."""
        self.project = TDGamProject
        self.app_tdpath = td.op(
            "/local").fetch("app_tdpath", "/ui/dialogs/mainmenu/TDGam")

        btn_row_tdpath = self.app_tdpath + "/controls/list/list/"
        self.branch_btn_grp = {
            "checkout": td.op(btn_row_tdpath + "checkout"),
            "push": td.op(btn_row_tdpath + "push"),
            "pull": td.op(btn_row_tdpath + "pull"),
            "delete": td.op(btn_row_tdpath + "delete"),
            "create_branch": td.op(btn_row_tdpath + "create_branch"),
            "init": td.op(btn_row_tdpath + "init"),
        }

        # data tables used by UI
        self.tbl_git_branches = td.op("tbl_git_branches")
        self.tbl_gitLog = td.op("tbl_gitLog")
        self.tbl_ops = td.op("tbl_ops")
        self.tbl_preferences = td.op("tbl_preferences")

        self.confirm_locals = {
            "ok": None,
            "cancel": None
        }

        self.component_uis = []

    def refresh(self):
        """Update all UI mechanisms with new data."""
        # temporary set remote repo
        remote_url = self.project.preferences["project_remote_repo_url"]
        if remote_url and remote_url != "https://":

            if not self.project.repo.remotes:
                # remote = self.project.repo.remotes[0]
                remote_name = re.search(r".+\/(\w+)\.git$", remote_url)

                if remote_name:
                    remote_name = remote_name.group(1)

                else:
                    remote_name = self.project._name_hash(10)

                self.git_add_remote(remote_name, remote_url)

        self.__update_project_preferences_dialogue()

    def append_component(self, selected_ops, parent_op):
        """Append new Component instance to Project.

        :param selected_ops: selected ops to convert.
        :type: list of td.OP's
        :returns: TDGamComponentUI instance
        """
        # logging.debug(
        #     "\n\t[project_ui.append_component] -> :param selected_ops:\n\n{}\n".
        #     format(pformat(selected_ops)))

        c = self.project.append_component(selected_ops)
        c_ui = TDGamComponentUI(c, parent_op)
        self.component_uis.append(c_ui)
        c_ui.refresh()

        # logging.debug("Appending component:\n{}".format(pformat(selected_ops)))
        return c_ui

    def retrieve_component(self, name):
        """Return TDGamComponentUI instance from project.

        :param name: name of the component to retrieve.
        :type: str
        :returns: TDGamComponentUI instance
        """
        result = None
        for c_ui in self.component_uis:

            if c_ui.c.name == name:
                result = c_ui
                break

        return result

    def confirm(self, title, ui_components, show_buttons=True):
        """Show a popup dialogue with default 'ok' and 'cancel' button.

        Contents of the window will be in order of whats passed in
        'ui_components' param.

        :param title: Custom title to appear in titlebar.
        :type: str
        :param ui_components: UI components and values to display, in
            order.
        :type: dict
        :returns: td.containerCOMP instance used as the confirm dialog.
        """
        confirm = td.op(self.app_tdpath + "/controls/confirm")
        confirm_titlebar_define = td.op(
            self.app_tdpath + "/controls/confirm/titlebar/define")

        # set display on all ui components by cross-referencing 'ui_components'
        [self.__set_display(name, confirm) for name in ui_components.keys()]

        # populate all ui components
        self.__populate(ui_components, confirm)
        # set title
        confirm_titlebar_define["dialogname", 1] = title
        # set window height
        confirm.par.h = self.__calculate_window_height(ui_components, confirm)

        return confirm.openViewer(unique=False, borders=False)

    def init_project(self, path):

        self.project.init(path)
        self.refresh()

    def git_init(self):

        self.project.git_init()
        self.refresh()

    def git_create_branch(self, branch_name):

        self.project.git_create_branch(branch_name)
        self.refresh()

    def git_initial_commit(self):

        self.project.git_initial_commit()
        self.refresh()

    def git_add_remote(self, remote_name, remote_url):
        self.project.log("remote_name: {},\nremote_url: {}".format(
            remote_name, remote_url), "warning")
        remote = self.project.repo.create_remote(remote_name, url=remote_url)

        self.refresh()

        return remote

    def git_push(self, local_branch, remote_branch, remote):

        push_info = remote.push(
            refspec='{}:{}'.format(local_branch, remote_branch))

        self.project.log(str(push_info[0].summary), "info")

        self.refresh()

    def update_preferences(self, preferences):

        self.project.update_preferences(preferences)
        self.refresh()

    def __calculate_window_height(self, ui_components, parent):
        """Calculate height of all given ui components.

        :param ui_components: <list> Names of components.
        :param parent: <td.Op> Parent Op to search inside.
        """
        height = 0
        ui_components.update({"titlebar": None})
        spacing = parent.findChildren(
            name="confirm_content_root")[0].par.spacing

        for c_name in ui_components.keys():
            try:
                c_height = parent.findChildren(name=c_name)[0].par.h
                height += c_height
                print("{} height: {}".format(c_name, c_height))
            except KeyError as e:
                print("Couldn't find {}, SKIPPING!\n\n{}".format(c_name, e))

        return height + len(ui_components) * spacing

    def __set_display(self, name, parent):
        """Set display to True for ui element.

        :param name: <str> Name of ui element to display.
        :param parent: <td.Op> Parent Op to search inside.
        """
        parent.findChildren(name=name)[0].par.display = 1

        return True

    def __populate(self, ui_components, parent):
        """Set all labels and values for ui components.

        :param name: <str> Name of ui component.
        :param dict_: <dict> Dict containing 'label' and 'value' properties.
        :param parent: <td.Op> Parent Op containing the children to work on.
        """
        if "message" in ui_components:
            text_dat = td.op(self.app_tdpath +
                             "/controls/confirm/message/text2")
            text_dat.text = ui_components["message"]["val"]

        if "ok" in ui_components:
            define = td.op(self.app_tdpath + "/controls/confirm/ok/define")

            # bind and call ok button with args
            define["buttonlabel", 1] = ui_components["ok"]["label"]
            # store as local variabls to confirm comp
            self.confirm_locals.update(
                {"ok": {
                    "callback": ui_components["ok"]["callback"],
                    "args": ui_components["ok"]["args"]
                }}
            )

        if "list":
            table_list = td.op(self.app_tdpath
                               + "/controls/confirm/table_list")
            table_list.setSize(0, 1)

            [table_list.appendRow(dict__["label"])
             for dict__ in ui_components["list"]]

        for ui_c_name in ["stringfield_url", "stringfield_name"]:

            if ui_c_name in ui_components:
                define = td.op(self.app_tdpath
                               + "/controls/confirm/{}/define".format(
                                   ui_c_name))

                define["label", 1] = ui_components[ui_c_name]["label"]
                td.op(self.app_tdpath + "/controls/confirm/{}/string".format(
                    ui_c_name)).text = ui_components[ui_c_name]["val"]

    def __update_project_preferences_dialogue(self):
        """needs to be cleaned up."""

        # tbl_git_branches
        self.tbl_git_branches.setSize(0, 1)

        # reset all btns to hidden
        for btn in self.branch_btn_grp.values():

            btn.par.display = 0

        # portion of the row with the branch's name
        branch_name = td.op(self.app_tdpath + "/controls/list/list/list")

        if not self.project.repo:
            self.tbl_git_branches.appendRow("No Repo...")
            # init
            self.branch_btn_grp["init"].par.display = 1
            branch_name.par.w = branch_name.parent().width \
                - self.branch_btn_grp["init"].par.w

        elif not len(self.project.repo.branches):
            self.tbl_git_branches.appendRow(
                self.project.repo.active_branch.name)

            self.branch_btn_grp["create_branch"].par.display = 1
            self.branch_btn_grp["create_branch"].par.w = 128
            # change button label
            self.branch_btn_grp["create_branch"].op(
                "eval2").par.expr = "\'make initial commit.\'"

            branch_name.par.w = branch_name.parent().width \
                - self.branch_btn_grp["create_branch"].par.w
        else:
            # append rows for each branch
            for branch in self.project.repo.branches:

                self.tbl_git_branches.appendRow(str(branch))

            # turn on button display
            button_grp_width = 0
            for btn_name in ["checkout", "delete"]:

                btn = self.branch_btn_grp[btn_name]
                btn.par.display = 1
                button_grp_width += btn.par.w

            # set width
            branch_name.par.w = branch_name.parent().width \
                - button_grp_width
