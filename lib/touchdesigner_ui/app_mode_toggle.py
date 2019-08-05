"""Toggle App Mode.

This will toggle where the TD UI elements point to for the main app.

production:  app will source from the hidden /ui dir, which sources from the
             TDGam site-packages folder on startup.
development: app will source from a TDGam tox located in the root.
"""
import td

args = globals()["args"]

SELECTION = args[0]
KEY = {
    "0": "production",
    "1": "development",
    "tdpath": {
        "0": "/ui/dialogs/mainmenu/TDGam",
        "1": "/TDGam"
    }
}

APP_MODE = KEY[SELECTION]
APP_TDPATH = KEY["tdpath"][SELECTION]

root = td.op("/local")
root.store("app_mode", APP_MODE)
root.store("tdgam_path", APP_TDPATH)

# check if a model instance is present
app_model = None
if td.op(APP_TDPATH) and td.op(APP_TDPATH).extensions:
    app_model = td.op(APP_TDPATH).extensions[0]

    app_model.log("TDGam App Mode set to: {}\n\n\tNow using tdpath: {}".format(
        td.op("/local").fetch("app_mode").upper(),
        td.op("/local").fetch("tdgam_path")
    ), "warning")

else:
    print("TDGam Could not be initialized at: {}!".format(APP_TDPATH))
