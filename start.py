"""This script simulates launching touchdesigner from a magla tool launcher.

MagLa is an open-source VFX-inspired pipeline and production management API for
Touch Designer studios heavily using Touch Designer with other DCC tools.
"""
import os
import subprocess
import sys

TDGAM = os.path.dirname(os.path.abspath(__file__))
THIRDPARTY = os.path.join(TDGAM, "lib", "third_party")

sys.path.append(os.path.join(TDGAM, "lib"))
from maglapath import Path


def main():
    """Launch a simulated magla process."""
    cmd_list = [str(Path("<touchdesigner>")), str(Path("<example_toe>"))]

    # inject custom PYTHONPATH
    env_ = os.environ.copy()
    env_["TDGAM_REPO"] = str(Path("<tdgam_repo>"))
    env_["PYTHONPATH"] = os.pathsep.join(
        [
            env_["PYTHONPATH"],
            TDGAM,
            os.path.join(THIRDPARTY, "GitPython"),
            os.path.join(THIRDPARTY, "gitdb"),
            os.path.join(THIRDPARTY, "smmap"),
            os.path.join(THIRDPARTY, "pyyaml", "lib"),
            os.path.join(THIRDPARTY, "pyyaml", "lib", "yaml"),
            os.path.join(THIRDPARTY, "scandir", "build", "lib.win-amd64-2.7")
        ]
    )
    subprocess.Popen(cmd_list, shell=True, env=env_)


if __name__ == "__main__":
    main()
