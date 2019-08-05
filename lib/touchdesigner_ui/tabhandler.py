"""Tabhandler for components.

/ui/dialogs/mainmenu/TDGam/controls/TDGamComponent_ui/text_tabhandler
"""
import os.path as osp

import td

from tdgam import Path

# args given to this textDAT
ARGS = globals()["args"]
SELECTED_TAB_INDEX = ARGS[0]

# tableDAT controllers for the ui
LIST_SELECT = td.op("../list")
LIST_STAGING_AREA = td.op("../list_staging_area")
LIST_OPS = td.op("../list_ops")
LIST_BRANCHES = td.op("../list_branches")

# TDGamProjectUI instance
UI = td.op(Path("<tdgam>")).ext.UI
# current component's TDGamComponent instance
CMPNT = UI.retrieve_component(td.op("../..").name)


def __set_select(name):
    """Set the 'select1' selectDAT's 'select' attribute.

    :param name: the op name to set to.
    :type  name: str
    """
    td.op("../select1").par.dat = name

    LIST_SELECT.par.display = 1
    LIST_STAGING_AREA.par.display = 0
    LIST_OPS.par.display = 0
    LIST_BRANCHES.par.display = 0


def __set_table(table_name, list_):
    """Map iterable to table rows.

    :param table_name: the table to map.
    :type  table_name: str
    :param list_: the list of data to map to the tableDAT rows.
    :type  list_: list
    """
    table = td.op(table_name)
    table.setSize(0, 1)

    for item in list_:
        table.appendRow(item)


def git_log():
    """Show the 'git log' tab."""
    LIST_SELECT.par.display = 1
    LIST_STAGING_AREA.par.display = 0
    LIST_OPS.par.display = 0
    LIST_BRANCHES.par.display = 0

    # set the 'select1' selectDAT to display git log data
    __set_select("tbl_git_log")


def git_branches():
    """Show 'git branches' tab."""
    LIST_SELECT.par.display = 0
    LIST_STAGING_AREA.par.display = 0
    LIST_OPS.par.display = 0
    LIST_BRANCHES.par.display = 1


def staging_area():
    """Show the 'staging area' tab."""
    LIST_SELECT.par.display = 0
    LIST_STAGING_AREA.par.display = 1
    LIST_OPS.par.display = 0
    LIST_BRANCHES.par.display = 0

    # populate tracked files
    __set_table(td.op("../tbl_tracked_files"),
                [[osp.basename(f), f] for f in CMPNT.retrieve_tracked_files()])
    # populate untracked files
    __set_table(td.op("../tbl_untracked_files"),
                [[osp.basename(f), f] for f in CMPNT.retrieve_untracked_files()])
    # populate modified files
    __set_table(td.op("../tbl_modified_files"),
                [[entry[0], entry[1]] for entry in CMPNT.retrieve_modified_files()])


def ops_():
    """Show the 'ops' tab."""
    LIST_SELECT.par.display = 0
    LIST_STAGING_AREA.par.display = 0
    LIST_OPS.par.display = 1
    LIST_BRANCHES.par.display = 0


def handle(selected_tab_index):
    """Use the tab index to run specified callable defined above.

    :param selected_tab_index: the index argument received from Touch Designer.
    :type  selected_tab_index: int
    """
    tabs = {
        "0": git_log,
        "1": git_branches,
        "2": staging_area,
        "3": ops_
    }

    callable_ = tabs[selected_tab_index]
    callable_()
    UI.refresh()


handle(SELECTED_TAB_INDEX)
