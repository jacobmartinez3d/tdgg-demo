"""Author: Jacob Martinez, Dec. 2018."""
if __name__ == "__main__":
    from TDGam.lib import TDGamProject
    from TDGam.lib import TDGamProjectUI
    from TDGam.lib import Path

else:
    # this import assumes you have copied the TDGam repo to:
    # C:\Program Files\Derivative\TouchDesigner099\bin\Lib\site-packages\TDGam
    from .lib import TDGamProject
    from .lib import TDGamProjectUI
    from .lib import Path

from os import environ
env_ = environ.copy()
env_["MAGLA_PROJECT_NAME"] = TDGamProject.get_current()
