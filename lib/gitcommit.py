"""panelexecuteDAT

/ui/dialogs/mainmenu/TDGam/controls/TDGamComponent_ui/menu1/buttontoggle/script
"""
import td

APP = td.op("/ui/dialogs/mainmenu/TDGam").extensions[1]
CMPNT = APP.retrieve_component(td.op("../../..").name)


def onOffToOn(panel_value):
    """Commit the added files to this Component's repo."""
    message = str(panel_value)
    commit = None
    try:
        commit = CMPNT.repo.git.commit('-m', message)
        APP.log(commit, "info")

    except Exception:
        APP.log("Nothing to commit!", "warning")

    return commit
