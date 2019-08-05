"""Initialize a git repo."""
import td

from tdgam import Path

UI = td.op(Path("<tdgam>")).ext.UI
UI.git_init()
