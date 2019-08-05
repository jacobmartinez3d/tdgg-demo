"""Commit changes for a component repo."""
import td

from tdgam import Path

UI = td.op(Path("<tdgam>")).ext.UI
CMPT_UI = UI.retrieve_component(td.op("../../..").name)


def onOffToOn(panelValue):
    """Commit the added files to this Component's repo."""
    message = "Hello World!"
    commit = None
    try:
        commit = CMPT_UI.c.repo.git.commit('-m', message)
        UI.project.log(commit, "info")

    except Exception:
        UI.project.log("Nothing to commit!", "warning")

    CMPT_UI.refresh()

    return commit
