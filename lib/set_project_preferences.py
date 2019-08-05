"""Set Project Preferences"""
import os
import re

import td

tdgam_path = td.op("/local").fetch("tdgam_path")
app_ui = td.op(tdgam_path).extensions[1]

new_project_folder = td.op("nul_project_root_path").text.strip()
new_remote_repo = td.op("nul_project_remote_url").text.strip()

# handle relative path
if not re.search(r"[a-z]\:", new_remote_repo):
    new_remote_repo = os.path.join(td.project.folder, new_remote_repo)
    new_remote_repo = os.path.normpath(new_remote_repo)

settings = {
    "project_folder": new_project_folder,
    "project_remote_repo_url": new_remote_repo
}
app_ui.update_settings(settings)
