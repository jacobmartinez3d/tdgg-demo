"""Perform git add command."""
import os

import td

from tdgam import Path

UI = td.op(Path("<tdgam>")).ext.UI
CMPT_UI = UI.retrieve_component(td.op("../../../..").name)


def onOffToOn(panelValue):

    # very ugly here...
    tbl_untracked_files = td.op("../../../tbl_untracked_files")
    full_path = tbl_untracked_files[0, 1].val
    rel_path = full_path.replace(CMPT_UI.c.repo.working_dir, "")
    # rel_path = rel_path.replace("\\", "/")
    if rel_path[0] == os.sep:
        rel_path = rel_path[1:]

    return gitAdd(rel_path)


def gitAdd(filepath):

    CMPT_UI.c.repo.index.add([filepath])
    print("{} now being tracked.".format(filepath))
    CMPT_UI.refresh()
