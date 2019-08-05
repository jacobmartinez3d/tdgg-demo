"""Create new git branch."""
import td

from tdgam import Path

UI = td.op(Path("<tdgam>")).ext.UI
CMPT_UI = UI.retrieve_component(td.op("../../..").name)
# origin = repo.create_remote('origin', repository)
# origin.fetch()
UI.git_initial_commit()
