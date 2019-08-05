"""Add a remote origin for component repo."""
import td

from tdgam import Path

# TDGamProjectUI instance
UI = td.op(Path("<tdgam>")).ext.UI


def onOffToOn(channel, sampleIndex, val, prev):

    callback = UI.confirm_locals["ok"]["callback"]
    ok_args = UI.confirm_locals["ok"]["args"]
    callback(ok_args[0], ok_args[1])
