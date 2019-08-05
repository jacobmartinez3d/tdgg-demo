"""Add new TDGamComponent instance to Project."""
import td

from tdgam import Path

UI = td.op(Path("<tdgam>")).ext.UI

CURRENT_PANE_CONTEXT = td.ui.panes[0].owner
SELECTION = CURRENT_PANE_CONTEXT.selectedChildren

UI.append_component(SELECTION, CURRENT_PANE_CONTEXT)
