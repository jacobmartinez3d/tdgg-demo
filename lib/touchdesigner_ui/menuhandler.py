"""Menu Handler for components.

This script runs each time a user clicks on a menu item.

/ui/dialogs/mainmenu/TDGam/controls/TDGamComponent_ui/menu1/script
"""
import td

from tdgam import Path

# TDGamProjectUI instance
UI = td.op(Path("<tdgam>")).ext.UI
# TDGamComponentUI instance
CMPT_UI = UI.retrieve_component(td.op("../..").name)

# args passed to this textDAT
ARGS = globals()["args"]

MENU_ID = td.op("id")[0, 0].val
SUBMENU_ID = ARGS[0]


def set_component_remote():
    """Open a confirm dialogue to add a new git repo URL to this component."""
    remote_name = td.op(UI.app_tdpath + "/controls/confirm/null_name").text
    remote_url = td.op(UI.app_tdpath + "/controls/confirm/null_url").text
    title, ui_components = CMPT_UI.set_component_remote(remote_name, remote_url)

    UI.confirm(title, ui_components)


MENU = {
    "0": {  # TDGam
        "0": CMPT_UI.stash,
        "1": CMPT_UI.rebuild,
        "2": CMPT_UI.dock,
        "3": "---",
        "4": CMPT_UI.export_json,
        "5": CMPT_UI.export_table_dat,
        "6": "---",
        "7": CMPT_UI.import_from_json,
        "8": CMPT_UI.import_from_table_dat,
        "9": CMPT_UI.import_from_remote_repo,
        "10": "---",
        "11": CMPT_UI.expand
    },
    "1": {  # git
        "0": CMPT_UI.git_commit,
        "1": CMPT_UI.git_reset,
        "2": CMPT_UI.git_push,
        "3": CMPT_UI.git_pull,
        "4": "----",
        "5": CMPT_UI.git_checkout_branch,
        "6": CMPT_UI.git_new_branch,
        "7": "----",
        "8": CMPT_UI.retrieve_git_log,
        "9": set_component_remote
    }
}


def handle(MENU_ID, SUBMENU_ID):
    """Run callback associated with selected menu item."""
    callable_ = MENU[MENU_ID][SUBMENU_ID]
    callable_()


handle(MENU_ID, SUBMENU_ID)
